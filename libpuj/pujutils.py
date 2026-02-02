# -*- coding: utf-8 -*-

import pathlib
import re
import unicodedata

import libpuj.pujpb as pb
from libpuj.pujcommon import (
    Accent as _Accent,
    Accent_Dummy as _Accent_Dummy,
    FuzzyRule as _FuzzyRule,
    FuzzyRuleDescriptor as _FuzzyRuleDescriptor,
    Pronunciation as _Pronunciation,
)

from libpuj.pujcommon import Pronunciation


class PUJUtils:
    _accents_raw: pb.Accents
    _entries_raw: pb.Entries
    _accents: dict[str, _Accent]
    _possible_pronunciations: list[pb.Pronunciation] = None
    _han_trd_to_entry: dict[str, list[pb.Entry]] = None
    _han_sim_to_entry: dict[str, list[pb.Entry]] = None
    _pronunciation_fast_map: dict[str, dict[str, dict[int, list[pb.Entry]]]] = None
    """
    This maps {initial: {final: {tone: [entry, ...]}.
    """

    def __init__(self, accents_pb_path, entries_pb_path):
        accents_pb_path = pathlib.Path(accents_pb_path)
        with open(accents_pb_path, 'rb') as f:
            self._accents_raw = pb.Accents()
            self._accents_raw.ParseFromString(f.read())
        _FuzzyRuleDescriptor.init_from_pb(self._accents_raw.fuzzy_rule_descriptors)
        self._accents = {}
        for a in self._accents_raw.accents:
            accent = _Accent.from_pb(a)
            self._accents[a.id] = accent

        entries_pb_path = pathlib.Path(entries_pb_path)
        with open(entries_pb_path, 'rb') as f:
            self._entries_raw = pb.Entries()
            self._entries_raw.ParseFromString(f.read())
        self._possible_pronunciations = [_Pronunciation.from_pb(e.pron) for e in self._entries_raw.entries]
        self._han_trd_to_entry = {}
        self._han_sim_to_entry = {}
        for e in self._entries_raw.entries:
            self._han_sim_to_entry.setdefault(e.char_sim, []).append(e)
            self._han_trd_to_entry.setdefault(e.char, []).append(e)
        for l in [self._han_trd_to_entry, self._han_sim_to_entry]:
            for han in l:
                entry = l[han]
                if len(entry) > 1:
                    l[han] = sorted(entry, key=lambda e: (-int(e.freq), -int(e.cat)))
        self._pronunciation_map = {}

    def get_entry_from_han(self, han) -> list[pb.Entry]:
        if han in self._han_sim_to_entry:
            return self._han_sim_to_entry[han]
        if han in self._han_trd_to_entry:
            return self._han_trd_to_entry[han]
        return []

    def get_accent(self, accent_id: str):
        return self._accents.get(accent_id, _Accent_Dummy())

    def get_accents(self):
        return self._accents.values()

    @staticmethod
    def is_cjk_character(char, basic_only=False) -> bool:
        # CJK Unified Ideographs                  4E00-9FFF   Common
        # CJK Unified Ideographs Extension A      3400-4DBF   Rare
        # CJK Unified Ideographs Extension B      20000-2A6DF Rare, historic
        # CJK Unified Ideographs Extension C      2A700–2B73F Rare, historic
        # CJK Unified Ideographs Extension D      2B740–2B81F Uncommon, some in current use
        # CJK Unified Ideographs Extension E      2B820–2CEAF Rare, historic
        # CJK Unified Ideographs Extension F      2CEB0–2EBEF  Rare, historic
        # CJK Unified Ideographs Extension G      30000–3134F  Rare, historic
        # CJK Unified Ideographs Extension H      31350–323AF Rare, historic
        # CJK Compatibility Ideographs            F900-FAFF   Duplicates, unifiable variants, corporate characters
        # CJK Compatibility Ideographs Supplement 2F800-2FA1F Unifiable variants
        # CJK Radicals / Kangxi Radicals          2F00–2FDF
        # CJK Radicals Supplement                 2E80–2EFF
        # CJK Symbols and Punctuation             3000–303F
        for c in char:
            o = ord(c)
            if basic_only:
                return 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF
            return (
                    0x4E00 <= o <= 0x9FFF or
                    0x3400 <= o <= 0x4DBF or
                    0x20000 <= o <= 0x2A6DF or
                    0x2A700 <= o <= 0x2B73F or
                    0x2B820 <= o <= 0x2CEAF or
                    0x2CEB0 <= o <= 0x2EBEF or
                    0x30000 <= o <= 0x3134F or
                    0x31350 <= o <= 0x323AF or
                    0xF900 <= o <= 0xFAFF or
                    0x2F800 <= o <= 0x2FA1F or
                    0x2F00 <= o <= 0x2FDF or
                    0x2E80 <= o <= 0x2EFF or
                    0x3000 <= o <= 0x303F
            )
        return False

    @staticmethod
    def for_each_word_in_sentence(sentence: str, func_word = None, func_non_word = None):
        sentence = unicodedata.normalize('NFD', sentence)
        regexp = re.compile(f"[a-zA-Z0-9']")
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

    @staticmethod
    def add_puj_tone_mark_word(word: str, tone: int | None = None) -> str:
        """
        为单个字添加音调符号

        Args:
            word: 拼音单词，可能包含数字声调
            tone: 指定的声调数字，如果不提供则从单词中提取

        Returns:
            添加了声调标记的单词
        """
        # 如果声调是 0、1 或 4，不需要添加标记
        if tone == 0 or tone == 1 or tone == 4:
            return word

        # 如果没有提供声调，从单词中提取
        if tone is None:
            tone = 0
            # 从后往前查找数字声调
            for i in range(len(word) - 1, -1, -1):
                if '1' <= word[i] <= '8':
                    tone = int(word[i])
                    # 移除声调数字
                    word = word[:i] + word[i + 1:]
                    break

        # 匹配单词结构
        match = Pronunciation.REGEXP_WORD.match(word)
        if match:
            groups = match.groupdict()
            initial = groups.get('initial') or ''
            medial = groups.get('medial') or ''
            nucleus = groups.get('nucleus') or ''
            coda = groups.get('coda') or ''

            if nucleus:
                # 在韵腹上添加声调标记
                tone_mark = Pronunciation.PUJ_TONE_MARKS_MAP[tone]
                if len(nucleus) == 1:
                    nucleus += tone_mark
                elif len(nucleus) == 2:
                    nucleus = nucleus[0] + tone_mark + nucleus[1]
                else:
                    nucleus = nucleus[0] + tone_mark + nucleus[1:]

            return initial + medial + nucleus + coda
        else:
            # 如果不匹配正则，直接返回原词
            print(f"Not a full word: {word} {tone}")
            return word


def _test():
    puj = PUJUtils('../dist/accents.pb', '../dist/entries.pb')
    while True:
        try:
            chars = input('Enter Han characters: ')
            print(*[puj.get_entry_from_han(c)[0].pron for c in chars])
        except KeyboardInterrupt:
            break
    pass


if __name__ == '__main__':
    _test()
