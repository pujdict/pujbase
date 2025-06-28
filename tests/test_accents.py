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
        test_cases = [
            [['liah8', 'ngiau2', 'tshv2'], 2 , [2, 25, 21]],
            [['ua2'], 0 , [52]],
            [['si6', 'tua7', 'meng5', 'tshenn1'], 3, [21, 212, 212, 33]],
            [['tsin6', 'tiong1'], 1, [21, 33]],
            [['tseh4', 'siu2'], 1, [5, 21]],
            [['jit8'], 0, [5]],
            [['sua3', 'menn5'], 1, [52, 55]],
            [['ngiau2', 'tshv2'], 1, [25, 21]],
            [['tann2'], 0, [52]],
            [['kann2', 'lai5', 'tau2', 'luan6'], 3, [23, 212, 23, 25]],
            [['ua2'], 0, [52]],
            [['tsiat4', 'si5'], 1, [5, 55]],
            [['kio3', 'i1', 'hue5', 'lau6', 'ke1'], 4, [32, 23, 212, 21, 33]],
        ]
        for i, test_case in enumerate(test_cases):
            combs, citation_index, expected_actual_tones = test_case
            with self.subTest(i=i, case=' '.join(combs)):
                self.expect_sandhi_group(
                    accent,
                    self.create_sandhi_group(combs, citation_index),
                    expected_actual_tones,
                )


if __name__ == '__main__':
    unittest.main()
