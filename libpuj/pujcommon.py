import dataclasses
import libpuj.pujpb as pb
import re
import unicodedata


class ConversionError(ValueError):
    """拼音转换过程中出现的错误，例如无法解析或使用了不支持的方案。"""


@dataclasses.dataclass
class AbstractPronunciation:
    initial: str = None
    final: str = None
    tone: int = 0
    # 该方案输出是否存在大小写区分。为 False 时（如国际音标），
    # 句子转换结束后不进行大小写转换，因为大小写在音标中表示不同音素。
    has_case: bool = True

    def __str__(self):
        return f'{self.initial}{self.final}{self.tone}'

    def __repr__(self):
        return self.__str__()


class Pronunciation(AbstractPronunciation):
    """
    ASCII 白话字拼音。内部存储为 ASCII 形式（特殊字母 ṳ o̤ 记录为 ur or），可输出为书面形式。
    """
    __special_vowels = {
        "ur": "ṳ",
        "or": "o̤",
    }
    __vowel_order = [
        'a', 'o', __special_vowels['ur'], 'ur', __special_vowels['or'], 'or', 'e', 'i', 'u',
    ]
    __vowels = set(__vowel_order)
    REGEXP_WORD = re.compile(
        r"^(?P<word>(?P<initial>(pfh|pf|phf|ph|p|mv(?=u)|bv(?=u)|f|m|b|th|t|l|kh|k|ng|n|g|h|tsh|ts|chh|ch|c|s|j|z|0))?(?P<final>(?P<medial>(y|yi|i|u|iu)(?=[aeoiu]))?(?P<nucleus>or|er|ur|ir|a|e|o|i|ṳ|u|o̤|ng|n|m)(?P<coda>(y|yi|i|u)?(m|ng|nn'?h|nn'?|n|p|t|k|h)?))(?P<tone>\d)?)$",
        re.IGNORECASE)
    PUJ_TONE_MARKS_MAP = [
        "",  # 0
        "",  # 1
        "\u0301",  # 2 锐音符 ́
        "\u0300",  # 3 抑音符 ̀
        "",  # 4
        "\u0302",  # 5 扬抑符 ̂
        "\u0303",  # 6 波浪符 ̃
        "\u0304",  # 7 长音符 ̄
        "\u0301",  # 8 锐音符 ́
    ]
    POSSIBLE_TONE_MARKS = {mark for mark in PUJ_TONE_MARKS_MAP if mark}
    __puj_possible_tone_marks = [
        [],  # 0
        [],  # 1
        ["\u0301", "\u0341"],  # 2
        ["\u0300", "\u0340"],  # 3
        [],  # 4
        ["\u0302"],  # 5
        ["\u0303", "\u0342", "\u030C", "\u0306"],  # 6
        ["\u0304"],  # 7
        ["\u0301", "\u0341", "\u0302", "\u030D"],  # 8
    ]
    __puj_dp_initial_map = {
        '': '',
        '0': '',
        'p': 'b',
        'ph': 'p',
        'm': 'm',
        'b': 'bh',
        't': 'd',
        'th': 't',
        'n': 'n',
        'l': 'l',
        'k': 'g',
        'kh': 'k',
        'ng': 'ng',
        'g': 'gh',
        'h': 'h',
        'ts': 'z',
        'tsh': 'c',
        's': 's',
        'j': 'r',
    }
    __dp_puj_initial_map = {dp: puj for puj, dp in __puj_dp_initial_map.items()}
    __puj_ipa_initial_map = {
        '': '',
        '0': '',
        'p': 'p',
        'pf': 'p_df',
        'ph': 'p_h',
        'phf': 'p_d_hf',
        'pfh': 'p_d_hf',
        'm': 'm',
        'mv': 'F',
        'b': 'b',
        'bv': 'b_d',
        't': 't',
        'th': 't_h',
        'n': 'n',
        'l': 'l',
        'k': 'k',
        'kh': 'k_h',
        'ng': 'N',
        'g': 'g',
        'h': 'h',
        'ts': 'ts',
        'ch': 'tS',
        'tsh': 'ts_h',
        'chh': 'tS_h',
        's': 's',
        'j': 'dz',
        'z': 'z',
    }
    __puj_ipa_special_map = {
        'm': 'm=',
        'ng': 'N=',
        'ngh': 'N=_}',
    }
    __puj_ipa_final_map = {
        'a': 'a',
        'o': 'o',
        'ur': 'M',
        'or': '@',
        'e': 'e',
        'i': 'i',
        'u': 'u',
        # 'nn': '~', # 特殊处理
        'ng': 'N',
        'n': 'n',
        'm': 'm',
        'h': '?',
        'k': 'k_}',
        't': 't_}',
        'p': 'p_}',
    }

    def __init__(self, initial: str = '', final: str = '', tone: int = 0):
        if initial == '0' or initial is None:
            initial = ''
        elif initial == 'ch':
            initial = 'ts'
        elif initial == 'chh':
            initial = 'tsh'
        elif initial == 'z':
            initial = 'j'
        if final is None:
            final = ''
        super().__init__(initial, final, tone)

    def __copy__(self):
        return Pronunciation(self.initial, self.final, self.tone)

    def __str__(self):
        return f'{self.initial}{self.final}{self.tone}'

    def __bool__(self):
        return self.initial or self.final or self.tone

    @classmethod
    def from_pb(cls, data: pb.Pronunciation):
        return cls(data.initial or '', data.final, data.tone)

    def to_pb(self) -> pb.Pronunciation:
        """
        ASCII 白话字转 Protobuf。
        """
        return pb.Pronunciation(
            initial=self.initial or '0',
            final=self.final,
            tone=self.tone,
        )

    @classmethod
    def from_written(cls, written: str) -> 'Pronunciation':
        if not written:
            return cls()
        written = unicodedata.normalize('NFD', written)
        tone = 0
        # 消除调符
        for i, possible_marks in enumerate(cls.__puj_possible_tone_marks):
            for possible_tone_mark in possible_marks:
                if possible_tone_mark in written:
                    written = written.replace(possible_tone_mark, '')
                    tone = i
                    break
            else:
                continue
            break
        # 消除末尾的数字声调
        if written[-1].isdigit():
            if tone:
                return cls()
            tone = int(written[-1])
            if not (1 <= tone <= 8):
                return cls()
            written = written[:-1]
        # 特殊字符转 ASCII（书面 ṳ o̤ 转内部 ur or）
        written = written.replace(cls.__special_vowels['ur'], 'ur')
        written = written.replace(cls.__special_vowels['or'], 'or')
        # 入声做一次额外处理：4 声无调符，8 声的调符可能与 2 声或 5 声相同。
        # 这里简化了判断的依据。如果是入声韵并且有声调符号，那么就认为是 8 声。
        # 如果是入声韵并且前面没发现调符，就是 4 声。
        if written[-1] in 'ptkhPTKH':
            tone = 8 if tone else 4
        match = cls.REGEXP_WORD.match(written)
        if not match:
            return cls()
        initial = match.group('initial') or '0'
        final = match.group('final')
        return cls(initial, final, tone)

    def to_written(self) -> str:
        """
        ASCII 白话字转书面白话字。
        """
        initial = self.initial if self.initial != '0' else ''
        final = self.final
        if not final:
            return ''
        final = final.replace('ur', self.__special_vowels['ur'])
        final = final.replace('or', self.__special_vowels['or'])
        coda_index = self.__get_coda_index(final)
        if coda_index == -1:
            return ''
        tone = self.tone
        if not (0 <= tone <= 8):
            return ''
        tone_mark = self.PUJ_TONE_MARKS_MAP[tone]
        final = f"{final[:coda_index + 1]}{tone_mark}{final[coda_index + 1:]}"
        return f"{initial}{final}"

    @classmethod
    def __get_coda_index(cls, final: str) -> int:
        """
        给定韵母求韵腹。
        """
        if final:
            if final[0].lower() in 'iu' and len(final) > 1 and final[1] in cls.__vowels:
                return 1
            if final.startswith(cls.__special_vowels['ur']):
                return len(cls.__special_vowels['ur']) - 1
            if final.startswith(cls.__special_vowels['or']):
                return len(cls.__special_vowels['or']) - 1
            return 0
        return -1

    @classmethod
    def from_combination(cls, combination: str) -> 'Pronunciation':
        """
        将 ASCII 白话字（如 `peng1`）解析为 `Pronunciation`。

        将缺失的调号视为 0；解析失败时抛出 `ConversionError`。
        """
        if not combination:
            raise ConversionError("输入为空，无法解析白话字拼音。")
        match = cls.REGEXP_WORD.match(combination)
        if not match:
            raise ConversionError(f"无法解析白话字拼音：{combination!r}")
        initial = match.group('initial') or ''
        final = match.group('final') or ''
        tone_text = match.group('tone')
        tone = int(tone_text) if tone_text else 0
        return cls(initial, final, tone)

    def to_combination(self) -> str:
        return (f"{self.initial if self.initial != '0' else ''}"
                f"{self.final}"
                f"{self.tone}")

    @classmethod
    def from_dp(cls, dp: 'DPPronunciation') -> 'Pronunciation':
        return Pronunciation(
            initial=cls.__from_dp_initial_or_final(dp.initial),
            final=cls.__from_dp_initial_or_final(dp.final),
            tone=dp.tone,
        )

    def to_dp(self) -> 'DPPronunciation':
        return DPPronunciation(
            initial=self.__to_dp_initial_or_final(self.initial),
            final=self.__to_dp_initial_or_final(self.final),
            tone=self.tone,
        )

    @classmethod
    def __to_dp_initial_or_final(cls, part: str) -> str:
        if not part:
            return ''
        try_to_map_initial = cls.__puj_dp_initial_map.get(part, None)
        if try_to_map_initial:
            return try_to_map_initial
        part = part.replace('e', 'ê')
        part = part.replace('ur', 'e')
        part = part.replace('or', 'er')
        part = part.replace('au', 'ao')
        if part[-1] == 'n':
            if part.endswith('nn'):
                part = part[:-1]
            else:
                part += 'd'
        if part[-1] == 'p':
            part = part[:-1] + 'b'
        if part[-1] == 't':
            part = part[:-1] + 'd'
        if part[-1] == 'k':
            part = part[:-1] + 'g'
        return part

    @classmethod
    def __from_dp_initial_or_final(cls, part: str) -> str:
        if not part:
            return ''
        try_to_map_initial = cls.__dp_puj_initial_map.get(part, None)
        if try_to_map_initial:
            return try_to_map_initial
        part = unicodedata.normalize('NFC', part)
        part = part.replace('er', 'or')
        part = part.replace('ee', 'ê')
        part = part.replace('e', 'ur')
        part = part.replace('ê', 'e')
        part = part.replace('ao', 'au')
        # 鼻化韵尾：DP nd -> PUJ n；DP n -> PUJ nn。
        if part.endswith('nd'):
            part = part[:-1]
        elif part[-1] == 'n':
            part += 'n'
        # 入声韵尾：DP b/d/g -> PUJ p/t/k（注意 ng 是鼻化韵，不转为 nk）。
        if part[-1] == 'b':
            part = part[:-1] + 'p'
        if part[-1] == 'd':
            part = part[:-1] + 't'
        if part[-1] == 'g' and not part.endswith('ng'):
            part = part[:-1] + 'k'
        return part

    def to_ipa(self) -> 'IPAPronunciation':
        initial = self.__puj_ipa_initial_map.get(self.initial, '')
        final_tmp = self.final
        if final_tmp in ['m', 'ng', 'ngh']:
            # 声化韵特殊处理
            final = self.__puj_ipa_special_map.get(final_tmp)
            if self.initial == 'h':
                if final_tmp in ['ng', 'ngh']:
                    initial = self.__puj_ipa_final_map.get('ng') + '_0'
                if final_tmp == 'm':
                    initial = self.__puj_ipa_final_map.get('m') + '_0'
        else:
            nasalize = final_tmp.endswith('nn')
            if nasalize:
                final_tmp = final_tmp[:-2]
            final = ''
            i = 0
            while i < len(final_tmp):
                for item in self.__puj_ipa_final_map.keys():
                    # print(item)
                    if final_tmp[i:i + len(item)] == item:
                        final += self.__puj_ipa_final_map[item]
                        i += len(item)
                        if nasalize and item in self.__vowels:
                            final += '~'
                        break
                else:
                    i += 1
            # print(final)
        return IPAPronunciation(initial, final, self.tone)


class DPPronunciation(AbstractPronunciation):
    """
    潮拼拼音。
    """

    # 潮拼单词正则，参考前端 SPuj.ts 的 regexpWordDp。
    REGEXP_WORD = re.compile(
        r"^(?P<initial>(bh|bf|pf|bhv|mv|ng|gh|b|p|m|f|v|d|t|n|l|g|k|h|z|c|s|r|0))?"
        r"(?P<final>(?P<medial>(i|u)(?=[aeoiu]))?"
        r"(?P<nucleus>ê|e|a|o|i|u|v|or|er|ng|m)"
        r"(?P<coda>(i|u)?(m|nd|ng|n'?|b|d|g|h)*))"
        r"(?P<tone>\d)?$",
        re.IGNORECASE)

    def __init__(self, initial: str = None, final: str = None, tone: int = 0):
        super().__init__(initial, final, tone)

    @classmethod
    def from_written(cls, written: str):
        return cls.from_combination(written)

    @classmethod
    def from_combination(cls, combination: str) -> 'DPPronunciation':
        """
        将潮拼（如 `bêng1`）解析并转换为白话字 `Pronunciation`。

        先解析为 `DPPronunciation`，再通过 `Pronunciation.from_dp` 转为白话字
        （内部 ASCII 形式）。解析失败时抛出 `ConversionError`。
        """
        if not combination:
            raise ConversionError("输入为空，无法解析潮拼。")
        combination = unicodedata.normalize('NFC', combination)
        match = cls.REGEXP_WORD.match(combination)
        if not match:
            raise ConversionError(f"无法解析潮拼：{combination!r}")
        initial = match.group('initial') or ''
        if initial == '0':
            initial = ''
        final = match.group('final') or ''
        tone_text = match.group('tone')
        tone = int(tone_text) if tone_text else 0
        return cls(initial, final, tone)


class IPAPronunciation(AbstractPronunciation):
    """
    国际音标。内部存储为 X-SAMPA 形式，可输出为书面形式。
    此处存储声调为调序，并非实际调值。实际调值另外建模处理。
    """

    has_case = False
    """国际音标中大小写表示不同音素，因此不进行大小写转换。"""

    __x_sampa_ipa_map = {
        '__1': '¹', '__2': '²', '__3': '³', '__4': '⁴', '__5': '⁵', '__6': '⁶', '__7': '⁷', '__8': '⁸', '__9': '⁹',
        't`_m': 'ȶ', 'd`_m': 'ȡ', 'n`_m': 'ȵ', 'l`_m': 'ȴ', 'ts': 'ts', 'dz': 'dz', 'tS': 'tʃ',
        'dZ': 'dʒ', 'ts\\': 'tɕ', 'dz\\': 'dʑ', 't`s`': 'ʈʂ', 'd`z`': 'ɖʐ',
        '_h': 'ʰ', '_j': 'ʲ', '_P': '̪', '_0': '̊',
        '_=': '̩', '=': '̍', '_}': '̚', '~': '̃', "'": 'ʲ', '_(': '₍', '_)': '₎',
        '+h\\': 'ʱ', '+h': 'ʰ', '+j': 'ʲ',
        'a': 'a', 'a\\': 'ä', 'A\\': 'ɐ̠', 'A': 'ɑ',
        'b\\': 'ⱱ', 'b': 'b', 'B\\': 'ʙ', 'B': 'β',
        'c': 'c', 'C': 'ç',
        'd': 'd', 'D`': 'ɻ̝', 'D\\': 'ʓ', 'D': 'ð',
        'e': 'e', 'E\\': 'e̽', 'E': 'ɛ',
        'f\\': 'ʩ', 'F\\': 'Ɬ', 'f': 'f', 'F': 'ɱ',
        'g': 'ɡ', 'G\\': 'ɢ', 'G': 'ɣ',
        'h\\': 'ɦ', 'h': 'h', 'H\\': 'ʜ', 'H': 'ɥ',
        'i\\': 'ɨ', 'i': 'i', 'I\\': 'ᵻ', 'I': 'ɪ',
        'j\\': 'ʝ', 'J\\': 'ɟ', 'j': 'j', 'J': 'ɲ',
        'k': 'k',
        'l': 'l',
        'm\\': 'ɯ̽', 'M\\': 'ɰ', 'm': 'm', 'M': 'ɯ',
        'n`': 'ɳ', 'n': 'n', 'N\\': 'ɴ', 'N': 'ŋ',
        'o': 'o', 'O': 'ɔ',
        'p\\': 'ɸ', 'p': 'p',
        'q': 'q',
        'r\\`': 'ɻ', 'r\\': 'ɹ', 'r`': 'ɽ', 'r': 'r', 'R\\': 'ʀ', 'R': 'ʁ',
        's`': 'ʂ', 's\\': 'ɕ', 's': 's', 'S': 'ʃ',
        't`': 'ʈ', 't': 't', 'T': 'θ',
        'u\\': 'ʉ', 'u': 'u', 'U\\': 'ᵿ', 'U': 'ʊ',
        'v\\': 'ʋ', 'v': 'v', 'V': 'ʌ',
        'w': 'w',
        'x': 'x', 'X\\': 'ħ', 'X': 'χ',
        'y': 'y', 'Y': 'ʏ',
        'z`': 'ʐ', 'z\\': 'ʑ', 'z': 'z', 'Z': 'ʒ',
        '.': '.', '"': 'ˈ', ',': 'ˌ', '%\\': 'я', '%': 'ˌ', '@`': 'ɚ', '@\\': 'ɘ', '@': 'ə',
        '{': 'æ', '}': 'ʉ', '1': 'ɨ', '2\\': 'ø̽', '2': 'ø', '3\\': 'ɞ', '3`': 'ɝ', '3': 'ɜ',
        '4\\': 'ɢ̆', '4': 'ɾ', '5\\': 'ꬸ', '5': 'ɫ', '6\\': 'ʎ̝', '6': 'ɐ', '7\\': 'ɤ̽', '7': 'ɤ',
        '8\\': 'ɥ̝̊', '8': 'ɵ', '9\\': 'ʡ̮', '9': 'œ', '0': 'Ø', ':\\': 'ˑ', ':': 'ː', '?\\': 'ʕ',
        '?': 'ʔ', '^\\': 'ğ', '^': 'ꜛ', '!': 'ꜜ', '&\\': 'ɶ̈', '&': 'ɶ',
        '*\\': '\\*', '$\\': 'ʀ̟', '$': '͢', ')': '͡', '(': '͜', '-\\\\': '\\\\', '-\\': '‿', '-': '',
        '||': '‖', '|': '|', '+\\': '⦀', ';': '¡'}
    __ipa_x_sampa_map = {k: v for v, k in __x_sampa_ipa_map.items()}

    def __init__(self, initial: str = None, final: str = None, tone: int = 0):
        super().__init__(initial, final, tone)

    def to_x_sampa(self):
        return f"{self.initial}{self.final}__{self.tone}"

    def to_written(self) -> str:
        initial = self.initial
        final = self.final
        for x_sampa, ipa in self.__x_sampa_ipa_map.items():
            initial = initial.replace(x_sampa, ipa, 1)
            final = final.replace(x_sampa, ipa, 1)
        tone = self.__x_sampa_ipa_map.get(f"__{self.tone}", '')
        return f"{initial}{final}{tone}"


@dataclasses.dataclass
class Entry:
    index: int
    char: str
    char_sim: str
    pron: Pronunciation
    cat: int
    freq: int
    char_ref: str
    details: list[pb.EntryDetail]

    @classmethod
    def from_pb(cls, entry: pb.Entry) -> 'Entry':
        return cls(
            index=entry.index,
            char=entry.char,
            char_sim=entry.char_sim,
            pron=Pronunciation.from_pb(entry.pron),
            cat=entry.cat,
            freq=entry.freq,
            char_ref=entry.char_ref,
            details=list(entry.details),
        )


@dataclasses.dataclass
class Tone:
    tone_number: int
    tone_pitch: int


@dataclasses.dataclass
class SandhiGroup:
    entries: list[Entry]
    citation_index: int
    begin_index: int
    end_index: int

    def __iter__(self):
        return iter(self.entries[self.begin_index : self.end_index])

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, item) -> Entry:
        if isinstance(item, int):
            if item >= 0:
                return self.entries[self.begin_index + item]
            else:
                return self.entries[self.end_index + item]
        else:
            raise TypeError(f"{SandhiGroup.__name__}.{SandhiGroup.__getitem__.__name__} only accepts integer index")


@dataclasses.dataclass
class Sentence:
    entries: list[Entry]
    """汉字集合"""
    sandhi_groups: SandhiGroup
    """连调单位列表"""
    word_groups: list[tuple[int, int, str]]
    """分词列表"""

    @staticmethod
    def for_each_word_in_sentence(sentence: str, func_word = None, func_non_word = None):
        sentence = unicodedata.normalize('NFD', sentence)
        # 除 ASCII 字母/数字/撇号外，还包含组合附加符号（U+0300-U+036F），
        # 使被 NFD 拆开的 ê(→e+◌̂)、ṳ、调符等保持在同一拼音单词内。
        regexp = re.compile(r"[a-zA-Z0-9'\u0300-\u036f]")
        next_hyphen_count = 0
        i = 0
        while i < len(sentence):
            cur = ''
            if regexp.match(sentence[i]):
                while i < len(sentence) and regexp.match(sentence[i]):
                    cur += sentence[i]
                    i += 1
                next_hyphen_count = 0
                if i < len(sentence) and sentence[i] == '-':
                    next_hyphen_count += 1
                    if i + 1 < len(sentence) and sentence[i + 1] == '-':
                        next_hyphen_count += 1
                if func_word:
                    func_word(cur, next_hyphen_count)
            else:
                while i < len(sentence) and not regexp.match(sentence[i]):
                    cur += sentence[i]
                    i += 1
                if func_non_word:
                    func_non_word(cur)

    # 句子字母大小写类别，与前端 SPuj.ts 的 ESentenceLetterCase 对应。
    LETTER_CASE_NONE = 0
    LETTER_CASE_LOWER = 1
    LETTER_CASE_UPPER_FIRST_LETTER = 2
    LETTER_CASE_UPPER = 3

    _LETTER_RE = re.compile(r"[a-zA-Z]")
    _LOWERCASE_LETTER_RE = re.compile(r"[a-z]")
    _UPPER_FIRST_RE = re.compile(r"[a-zê]")

    @staticmethod
    def determine_letter_case(sentence: str) -> int:
        """
        判断句子的字母大小写类别（对应前端 ESentenceLetterCase）。

        返回值：NONE=0、LOWER=1、UPPER_FIRST_LETTER=2、UPPER=3。
        """
        first_letter = True
        has_lower = False
        has_upper = False
        letters_cnt = 0
        for char in sentence:
            if Sentence._LETTER_RE.match(char):
                letters_cnt += 1
                if Sentence._LOWERCASE_LETTER_RE.match(char):
                    if first_letter:
                        return Sentence.LETTER_CASE_LOWER
                    has_lower = True
                else:
                    has_upper = True
                first_letter = False
        if (has_lower and has_upper) or (has_upper and letters_cnt == 1):
            return Sentence.LETTER_CASE_UPPER_FIRST_LETTER
        if has_upper:
            return Sentence.LETTER_CASE_UPPER
        return Sentence.LETTER_CASE_NONE

    @staticmethod
    def change_letter_case(sentence: str, letter_case: int) -> str:
        """
        将句子的大小写恢复为 `letter_case` 指定的类别。

        其中 UPPER_FIRST_LETTER 会为每个以 ? ! . 结尾的句子片段
        的起始字母（a-z 或 ê）大写。
        """
        if letter_case == Sentence.LETTER_CASE_LOWER:
            return sentence.lower()
        if letter_case == Sentence.LETTER_CASE_UPPER:
            return sentence.upper()
        if letter_case == Sentence.LETTER_CASE_UPPER_FIRST_LETTER:
            res = list(sentence)
            is_current_sentence_fixed = False
            for i, char in enumerate(res):
                if not is_current_sentence_fixed and Sentence._UPPER_FIRST_RE.match(char):
                    res[i] = char.upper()
                    is_current_sentence_fixed = True
                if char in '?!.':
                    is_current_sentence_fixed = False
            return ''.join(res)
        return sentence


@dataclasses.dataclass
class Paragraph:
    sentences: list[Sentence]


class FuzzyRule:
    description: str
    example_chars: list[str]

    def __init__(self):
        self._possible_pronunciations_map: dict[str, Pronunciation] = {}
        self._possible_pronunciations_map_reverse: dict[Pronunciation, list[Pronunciation]] = {}
        pass

    def _fuzzy(self, result: Pronunciation):
        pass

    def fuzzy_result(self, origin: Pronunciation) -> Pronunciation:
        if origin.__str__() in self._possible_pronunciations_map:
            return self._possible_pronunciations_map[origin.__str__()]
        result = origin.__copy__()
        self._fuzzy(result)
        return result

    def cache_possible_pronunciations_map(self, possible_pronunciations: list[Pronunciation]):
        self._possible_pronunciations_map = {}
        self._possible_pronunciations_map_reverse = {}
        for pronunciation in possible_pronunciations:
            fuzzy_pronunciation = pronunciation.__copy__()
            self._fuzzy(fuzzy_pronunciation)
            self._possible_pronunciations_map[pronunciation.__str__()] = fuzzy_pronunciation
            self._possible_pronunciations_map_reverse.setdefault(fuzzy_pronunciation.__str__(), []).append(
                pronunciation)


class FuzzyRuleAction(FuzzyRule):
    action: str
    pattern: re.Pattern
    replacement: str

    @classmethod
    def from_pb(cls, data: pb.FuzzyRuleAction):
        res = cls()
        res.action = data.action
        res.pattern = re.compile(data.pattern)
        res.replacement = data.replacement_backslash
        return res

    def _fuzzy(self, result: Pronunciation):
        if self.action == 'final':
            result.final = re.sub(self.pattern, self.replacement, result.final)
        if self.action == 'initial+final':
            initial_final = result.initial + result.final
            new_initial_final = re.sub(self.pattern, self.replacement, initial_final)
            match = Pronunciation.REGEXP_WORD.match(new_initial_final)
            if not match:
                Pronunciation.REGEXP_WORD.match(new_initial_final)
                raise Exception(f"New initial+final not matched: {new_initial_final} from {initial_final}")
            result.initial = match.group('initial') or ''
            result.final = match.group('final')


class FuzzyRuleDescriptor(FuzzyRule):
    ALL_DESCRIPTORS_MAP = []
    descriptor_id = None
    actions: list[FuzzyRule]

    @classmethod
    def init_from_pb(cls, data: list[pb.FuzzyRuleDescriptor]):
        cls.ALL_DESCRIPTORS_MAP = []
        for desc in data:
            descriptor = cls.from_pb(desc)
            cls.ALL_DESCRIPTORS_MAP.append(descriptor)

    @classmethod
    def from_pb(cls, data: pb.FuzzyRuleDescriptor):
        res = cls()
        res.descriptor_id = data.id
        res.actions = [FuzzyRuleAction.from_pb(a) for a in data.actions]
        return res

    @classmethod
    def get_rule_from_pb(cls, rule_id: int):
        return cls.ALL_DESCRIPTORS_MAP[rule_id]

    def _fuzzy(self, result: Pronunciation):
        for action in self.actions:
            action._fuzzy(result)


class Accent(FuzzyRule):
    id: str
    area: str
    subarea: str
    rules: list[FuzzyRule]
    citation_tones: list[int]
    sandhi_tones: list[int]
    neutral_tones: list[int]
    tones_special_smooth_2nd_3rd_4th: bool = False
    tones_special_smooth_neutral: bool = False
    tones_special_variable_3rd_2nd: bool = False

    __tone_2nd_3rd_4th_left_smooth = [0, 0, 23, 32, 3]
    __tone_2nd_right_smooth = 21
    __tone_3rd_left_variant = 25

    def _fuzzy(self, result: Pronunciation):
        for rule in self.rules:
            rule._fuzzy(result)

    @classmethod
    def from_pb(cls, data: pb.Accent):
        assert FuzzyRuleDescriptor.ALL_DESCRIPTORS_MAP
        result = Accent()
        result.id = data.id
        result.area = data.area
        result.subarea = data.subarea
        result.rules_input = data.rules
        result.rules = [FuzzyRuleDescriptor.get_rule_from_pb(rule) for rule in data.rules]
        result.citation_tones = [0] + list(data.tones.citation)
        result.sandhi_tones = [0] + list(data.tones.sandhi)
        result.neutral_tones = [0] + list(data.tones.neutral)
        for special in data.tones.specials:
            if special == pb.ToneSpecial.TS_SMOOTH_2ND_3RD_4TH:
                result.tones_special_smooth_2nd_3rd_4th = True
            elif special == pb.ToneSpecial.TS_SMOOTH_NEUTRAL:
                result.tones_special_smooth_neutral = True
            elif special == pb.ToneSpecial.TS_VARIABLE_3RD_2ND:
                result.tones_special_variable_3rd_2nd = True
        return result

    def get_actual_tones(self, sandhi_group: SandhiGroup) -> list[int]:
        length = len(sandhi_group)
        citation_index = sandhi_group.citation_index
        citation_tone_number = sandhi_group[citation_index].pron.tone
        result = [0] * length
        i = length - 1
        while i >= 0:
            tone_number = sandhi_group[i].pron.tone
            if i < citation_index:
                tone = self.sandhi_tones[tone_number]
                if self.tones_special_smooth_2nd_3rd_4th:
                    if i + 1 != citation_index and 2 <= tone_number <= 4:
                        tone = self.__tone_2nd_3rd_4th_left_smooth[tone_number]
                    else:
                        if tone_number == 3 and citation_tone_number == 2:
                            if self.tones_special_variable_3rd_2nd:
                                tone = self.__tone_3rd_left_variant
                            else:
                                tone = self.__tone_2nd_3rd_4th_left_smooth[tone_number]
                        elif 2 <= tone_number <= 4:
                            if citation_tone_number not in [2, 5, 8]:
                                tone = self.__tone_2nd_3rd_4th_left_smooth[tone_number]
                result[i] = tone
            elif i == citation_index:
                tone = self.citation_tones[tone_number]
                if self.tones_special_smooth_2nd_3rd_4th:
                    if tone_number == 2 and i != 0:
                        left_tone_number = sandhi_group[i - 1].pron.tone
                        if 2 <= left_tone_number <= 4:
                            tone = self.__tone_2nd_right_smooth
                result[i] = tone
            else:
                tone = self.neutral_tones[tone_number]
                result[i] = tone
            i -= 1
        return result


class Accent_Dummy(Accent):
    id = 'Dummy'
    area = ''
    subarea = ''
    rules = []
