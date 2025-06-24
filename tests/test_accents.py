import unittest
import pujutils
from pujcommon import Accent, Pronunciation, SandhiGroup, Entry
from pathlib import Path


class AccentTestCase(unittest.TestCase):
    def setUp(self):
        self.pujutils = pujutils.PUJUtils(
            (Path(__file__).parent / '..' / 'dist' / 'accents.pb').resolve(),
            (Path(__file__).parent / '..' / 'dist' / 'entries.pb').resolve(),
        )
        pass

    def expect_fuzzy(
            self,
            origin: Pronunciation,
            expected: Pronunciation,
            accent: Accent,
    ):
        fuzzy = accent.fuzzy_result(origin)
        self.assertEqual(origin, fuzzy)


class AccentActualTonesTest(AccentTestCase):
    def expect_sandhi_group(self, accent: Accent, sandhi_group: SandhiGroup, expected_actual_tones: list[int]):
        self.assertEqual(len(sandhi_group), len(expected_actual_tones))
        found_actual_tones = accent.get_actual_tones(sandhi_group)
        self.assertEqual(len(sandhi_group), len(found_actual_tones))
        for i, (expected, found) in enumerate(zip(expected_actual_tones, found_actual_tones)):
            self.assertEqual(expected, found, f"Index: {i}; {list(sandhi_group)}")

    @staticmethod
    def create_sandhi_group(combs: list[str], citation_index: int) -> SandhiGroup:
        mock_entries = []
        for comb in combs:
            pron = Pronunciation.from_combination(comb)
            entry = Entry(0, '', '', pron, 0, 0, '', [])
            mock_entries.append(entry)
        result = SandhiGroup(mock_entries, citation_index, 0, len(mock_entries))
        return result

    def test_ChengHai_ChengCheng(self):
        accent = self.pujutils.get_accent("ChengHai_ChengCheng")
        self.expect_sandhi_group(
            accent,
            self.create_sandhi_group(["liah8", "ngiau2", "tshv2"], 2),
            [2, 25, 21],
        )


if __name__ == '__main__':
    unittest.main()
