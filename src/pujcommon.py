import dataclasses
import pujpb as pb
import re
import unicodedata


@dataclasses.dataclass
class AbstractPronunciation:
    initial: str = None
    final: str = None
    tone: int = 0

    def __str__(self):
        return f'{self.initial}{self.final}{self.tone}'

    def __repr__(self):
        return self.__str__()


class Pronunciation(AbstractPronunciation):
    """
    ASCII 白话字拼音。内部存储为 ASCII 形式（特殊字母 ṳ o̤ 记录为 v r），可输出为书面形式。
    """
    __special_vowels = {
        "v": "ṳ",
        "V": "Ṳ",
        "r": "o̤",
        "R": "O̤",
    }
    __vowel_order = [
        'A', 'a', 'E', 'e', 'O', 'o', 'I', 'i', 'U', 'u', 'V', 'v', 'R', 'r',
        __special_vowels['V'], __special_vowels['v'],
        __special_vowels['R'], __special_vowels['r'],
    ]
    __vowels = set(__vowel_order)
    __regexp_word = re.compile(
        r"^(?P<initial>(p|ph|m|b|pf|pfh|mv(?=u)|bv(?=u)|f|t|th|n|l|k|kh|ng|g|h|ts|c|ch|tsh|chh|s|j|z|0)'?)?(?P<final>(?P<medial>(y|yi|i|u)(?=[aeoiuvr]))?(?P<nucleus>a|e|o|i|u|v|r|ng|m)(?P<coda>(y|yi|i|u)?(m|n|ng|nn'?|p|t|k|h)*))(?P<tone>\d)?$",
        re.IGNORECASE)
    __puj_tone_marks = [
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
        'v': 'M',
        'r': '@',
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

    def __init__(self, initial: str = None, final: str = None, tone: int = 0, sp_nasal: int = 0):
        super().__init__('0' if initial == '' else initial, final, tone)
        self.sp_nasal = sp_nasal

    def __copy__(self):
        return Pronunciation(self.initial, self.final, self.tone, self.sp_nasal)

    def __str__(self):
        return f'{self.initial}{self.final}{self.tone} {self.sp_nasal}'

    def __bool__(self):
        return self.initial or self.final or self.tone or self.sp_nasal

    @classmethod
    def from_pb(cls, data: pb.Pronunciation):
        return cls(data.initial, data.final, data.tone, data.sp_nasal)

    def to_pb(self) -> pb.Pronunciation:
        """
        ASCII 白话字转 Protobuf。
        """
        return pb.Pronunciation(
            initial=self.initial or '0',
            final=self.final,
            tone=self.tone,
            sp_nasal=pb.EntrySpecialNasalization.Name(self.sp_nasal),
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
        # 特殊字符转 ASCII
        written = written.replace(cls.__special_vowels['v'], 'v')
        written = written.replace(cls.__special_vowels['V'], 'V')
        written = written.replace(cls.__special_vowels['r'], 'r')
        written = written.replace(cls.__special_vowels['R'], 'R')
        # 入声做一次额外处理：4 声无调符，8 声的调符可能与 2 声或 5 声相同。
        # 这里简化了判断的依据。如果是入声韵并且有声调符号，那么就认为是 8 声。
        # 如果是入声韵并且前面没发现调符，就是 4 声。
        if written[-1] in 'ptkhPTKH':
            tone = 8 if tone else 4
        match = cls.__regexp_word.match(written)
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
        coda_index = self.__get_coda_index(final)
        if coda_index == -1:
            return ''
        tone = self.tone
        if not (0 <= tone <= 8):
            return ''
        tone_mark = self.__puj_tone_marks[tone]
        final = f"{final[:coda_index + 1]}{tone_mark}{final[coda_index + 1:]}"
        final = final.replace('v', self.__special_vowels['v'])
        final = final.replace('V', self.__special_vowels['V'])
        final = final.replace('r', self.__special_vowels['r'])
        final = final.replace('R', self.__special_vowels['R'])
        return f"{initial}{final}"

    @classmethod
    def __get_coda_index(cls, final: str) -> int:
        """
        给定韵母求韵腹。
        """
        if final:
            if final[0].lower() in 'iu' and len(final) > 1 and final[1] in cls.__vowels:
                return 1
            return 0
        return -1

    @classmethod
    def from_combination(cls, combination: str) -> 'Pronunciation':
        match = cls.__regexp_word.match(combination)
        if match:
            initial = match.group('initial') or '0'
            final = match.group('final')
            tone = match.group('tone')
            return cls(initial, final, int(tone))
        return cls()

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
        try_to_map_initial = cls.__puj_dp_initial_map.get(part, None)
        if try_to_map_initial:
            return try_to_map_initial
        part = part.replace('e', 'ê')
        part = part.replace('v', 'e')
        part = part.replace('r', 'er')
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
        try_to_map_initial = cls.__dp_puj_initial_map.get(part, None)
        if try_to_map_initial:
            return try_to_map_initial
        part = unicodedata.normalize('NFC', part)
        part = part.replace('ê', 'e')
        part = part.replace('e', 'v')
        part = part.replace('er', 'r')
        part = part.replace('ao', 'au')
        if part[-1] == 'n':
            part += 'n'
        if part.endswith('nd'):
            part = part[:-1]
        if part[-1] == 'b':
            part = part[:-1] + 'p'
        if part[-1] == 'd':
            part = part[:-1] + 't'
        if part[-1] == 'g':
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
            for i, c in enumerate(final_tmp):
                final_map = self.__puj_ipa_final_map.get(c, '')
                if final_map:
                    final += final_map
                if nasalize and c in self.__vowels:
                    final += '~'
        return IPAPronunciation(initial, final, self.tone)


class DPPronunciation(AbstractPronunciation):
    """
    潮拼拼音。
    """

    def __init__(self, initial: str = None, final: str = None, tone: int = 0):
        super().__init__(initial, final, tone)


class IPAPronunciation(AbstractPronunciation):
    """
    国际音标。内部存储为 X-SAMPA 形式，可输出为书面形式。
    此处存储声调为调序，并非实际调值。实际调值另外建模处理。
    """

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

    def __init__(self, initial: str = None, final: str = None, tone: int = 0):
        super().__init__(initial, final, tone)

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

    @classmethod
    def from_pb(cls, data: pb.FuzzyRule):
        rule_name: str = pb.FuzzyRule.Name(data)
        rule_class_name = rule_name.replace("FR_", "FuzzyRule_")
        rule_class = globals()[rule_class_name]
        if rule_class is None:
            return cls()
        return rule_class()

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


class FuzzyRule_V_As_U(FuzzyRule):
    description = '单元音 ur 转为 u。潮阳、普宁、惠来、陆丰等地的口音。'
    example_chars = ['书', '之', '居', '鱼']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'v':
            result.final = 'u'


class FuzzyRule_R_As_O(FuzzyRule):
    description = '单元音 er 转为 o。潮汕大部分地区口音。'
    example_chars = ['坐', '罪', '短', '退']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'r':
            result.final = 'o'


class FuzzyRule_R_As_E(FuzzyRule):
    description = '单元音 er 转为 e。陆丰口音。'
    example_chars = ['坐', '罪', '短', '退']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'r':
            result.final = 'e'


class FuzzyRule_RH_As_OH(FuzzyRule):
    description = '单元音 erh 转为 oh。潮汕大部分地区口音。'
    example_chars = ['夺', '绝', '鳕', '雪']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'rh':
            result.final = 'oh'


class FuzzyRule_RM_As_IAM(FuzzyRule):
    description = 'erm 转为 iam。庄组深摄部分字音。'
    example_chars = ['森', '参', '簪']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'rm':
            result.final = 'iam'


class FuzzyRule_EU_As_IU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'eu':
            result.final = 'iu'


class FuzzyRule_OINN_As_AINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'oinn':
            result.final = 'ainn'


class FuzzyRule_UOINN_As_UINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uoinn':
            result.final = 'uinn'


class FuzzyRule_UOINN_As_UAINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uoinn':
            result.final = 'uainn'


class FuzzyRule_OI_As_UE(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['p', 'ph', 'm', 'b'] and result.final in ['oi', 'oinn', 'oih']:
            result.final = result.final.replace('oi', 'ue')


class FuzzyRule_OU_As_AU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.startswith('ou'):
            result.final = result.final.replace('ou', 'au')


class FuzzyRule_UE_As_UEI(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['ue', 'uenn', 'ueh']:
            result.final = result.final.replace('ue', 'uei')


class FuzzyRule_VN_As_IN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['vn', 'vt']:
            result.final = result.final.replace('v', 'i')


class FuzzyRule_IN_As_EN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['in', 'it']:
            result.final = result.final.replace('i', 'e')


class FuzzyRule_UENG_As_ENG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ueng':
            if result.initial == '0':
                result.final = 'eng'
            else:
                result.final = 'uang'


class FuzzyRule_UEK_As_UAK(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uek':
            result.final = 'uak'


class FuzzyRule_IO_As_IE(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['io', 'ionn', 'ioh']:
            result.final = result.final.replace('io', 'ie')


class FuzzyRule_IAU_As_IEU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.startswith('iau'):
            result.final = result.final.replace('iau', 'ieu')


class FuzzyRule_IAU_As_IOU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'iau':
            result.final = result.final.replace('iau', 'iou')


class FuzzyRule_IAN_As_IEN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ian':
            result.final = 'ien'
        elif result.final == 'iat':
            result.final = 'iet'


class FuzzyRule_UAN_As_UEN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uan':
            result.final = 'uen'
        elif result.final == 'uat':
            result.final = 'uet'


class FuzzyRule_IAM_As_IEM(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'iam':
            result.final = 'iem'
        elif result.final == 'iap':
            result.final = 'iep'


class FuzzyRule_N_As_L_ForMEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m') and result.initial == 'n':
            result.initial = 'l'


class FuzzyRule_N_As_L_ForNOrNGEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'n' and (
                (not result.final.endswith('nn') and result.final.endswith('n')) or
                result.final.endswith('ng')
        ):
            result.initial = 'l'


class FuzzyRule_L_As_N_ForMEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m') and result.initial == 'l':
            result.initial = 'n'


class FuzzyRule_MU_As_BU_ForNasalEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'm' and result.final.startswith('u') and (
                (not result.final.endswith('nn') and result.final.endswith('n')) or
                result.final.endswith('ng')
        ):
            result.initial = 'b'


class FuzzyRule_BU_As_MU_ForNasalEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'b' and result.final.startswith('u') and (
                (not result.final.endswith('nn') and result.final.endswith('n')) or
                result.final.endswith('ng')
        ):
            result.initial = 'm'


class FuzzyRule_Labiodentalized(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.startswith('u'):
            if result.initial == 'h':
                result.initial = 'f'
            elif result.initial in ['p', 'ph']:
                result.initial += 'f'
            elif result.initial in ['m', 'b']:
                result.initial += 'v'


class FuzzyRule_N_As_NG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('n') and not result.final.endswith('nn'):
            result.final = result.final.replace('n', 'ng')
        elif result.final.endswith('t'):
            result.final = result.final.replace('t', 'k')


class FuzzyRule_M_As_NG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m'):
            result.final = result.final.replace('m', 'ng')
        elif result.final.endswith('p'):
            result.final = result.final.replace('p', 'k')


class FuzzyRule_ENG_As_EN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'eng':
            result.final = 'en'
        elif result.final == 'ek':
            result.final = 'et'


class FuzzyRule_NG_As_UNG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['p', 'ph', 'm', 'b'] and result.final == 'ng':
            result.final = 'ung'


class FuzzyRule_NG_As_VNG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ng' and result.initial not in ['h', '0']:
            result.final = 'vng'


class FuzzyRule_IONG_As_ONG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['t', 'th', 'n', 'l', 'ts', 'tsh', 's', 'j'] and result.final == 'iong':
            result.final = 'ong'
        elif result.initial in ['t', 'n', 'l', 'ts', 'tsh', 's', 'j'] and result.final == 'iok':
            result.final = 'ok'


class FuzzyRule_NGU_As_U(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'ng' and result.final == 'u':
            result.initial = '0'


class FuzzyRule_RemoveApostrophe(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        result.initial = result.initial.replace("'", '')
        result.final = result.final.replace("'", '')


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
        result = Accent()
        result.id = data.id
        result.area = data.area
        result.subarea = data.subarea
        result.rules = [FuzzyRule.from_pb(rule) for rule in data.rules]
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
                    if i + 1 == citation_index:
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
