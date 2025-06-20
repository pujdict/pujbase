# -*- coding: utf-8 -*-

import pathlib
import pujpb as pb
from pujcommon import (
    Accent as _Accent,
    Accent_Dummy as _Accent_Dummy,
    FuzzyRule as _FuzzyRule,
    Pronunciation as _Pronunciation,
)


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


def _test():
    puj = PUJUtils('dist/accents.pb', 'dist/entries.pb')
    while True:
        try:
            chars = input('Enter Han characters: ')
            print(*[puj.get_entry_from_han(c)[0].pron for c in chars])
        except KeyboardInterrupt:
            break
    pass


if __name__ == '__main__':
    _test()
