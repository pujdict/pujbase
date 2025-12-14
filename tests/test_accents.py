import unittest
import libpuj.pujutils
from libpuj.pujcommon import Accent, Pronunciation, SandhiGroup, Entry
from pathlib import Path


class AccentTestCase(unittest.TestCase):
    def setUp(self):
        self.pujutils = libpuj.pujutils.PUJUtils(
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
            self.assertEqual(expected, found, f"Index: {i} {expected_actual_tones} {found_actual_tones}")

    @staticmethod
    def create_sandhi_group(combs: list[str], citation_index: int) -> SandhiGroup:
        mock_entries = []
        for comb in combs:
            pron = Pronunciation.from_combination(comb)
            entry = Entry(0, '', '', pron, 0, 0, '', [])
            mock_entries.append(entry)
        result = SandhiGroup(mock_entries, citation_index, 0, len(mock_entries))
        return result

    def _test_ChengHai_ChengCheng(self):
        accent = self.pujutils.get_accent("ChengHai_ChengCheng")
        test_cases = [
            [['liah8', 'ngiau2', 'tshur2'], 2, [2, 25, 21]],
            [['ua2'], 0, [52]],
            [['si6', 'tua7', 'meng5', 'tshenn1'], 3, [21, 212, 212, 33]],
            [['tsin6', 'tiong1'], 1, [21, 33]],
            [['tseh4', 'siu2'], 1, [5, 21]],
            [['jit8'], 0, [5]],
            [['sua3', 'menn5'], 1, [52, 55]],
            [['ngiau2', 'tshur2'], 1, [25, 21]],
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

    def _test_ShanTou_ShiQu(self):
        accent = self.pujutils.get_accent("ShanTou_ShiQu")
        test_cases = [
            [['liah8', 'ngiau2', 'tshur2'], 2, [2, 25, 52]],
            [['ua2'], 0, [52]],
            [['si6', 'tua7', 'meng5', 'tshenn1'], 3, [21, 21, 22, 33]],
            [['tsin6', 'tiong1'], 1, [21, 33]],
            [['tseh4', 'siu2'], 1, [5, 52]],
            [['jit8'], 0, [5]],
            [['sua3', 'menn5'], 1, [55, 55]],
            [['ngiau2', 'tshur2'], 1, [25, 52]],
            [['tann2'], 0, [52]],
            [['kann2', 'lai5', 'tau2', 'luan6'], 3, [25, 22, 25, 25]],
            [['ua2'], 0, [52]],
            [['tsiat4', 'si5'], 1, [5, 55]],
            [['kio3', 'i1', 'hue5', 'lau6', 'ke1'], 4, [55, 33, 22, 21, 33]],
            [['ti1', 'tann5', 'ngiau1'], 2, [33, 22, 33]],
            [['mai3', 'la1', 'phian2'], 2, [55, 33, 52]],
            [['ua2'], 0, [52]],
            [['kai5', 'khang1', 'khue3'], 2, [22, 33, 212]],
            [['huann1', 'bue7', 'tseng5', 'tian2'], 3, [33, 21, 22, 52]],
            [['tsi2', 'ainn3', 'ua2'], 2, [25, 55, 52]],
            [['liat8', 'si1'], 1, [2, 33]],
            [['siau2', 'ki6'], 1, [25, 25]],
            [['kuan2', 'ka3', 'lur2', 'nek8', 'thiann3'], 3, [25, 55, 25, 5, 21]],
            [['kiam1', 'sit4', 'liam2'], 2, [33, 5, 52]],
            [['leng5', 'tseng1', 'kiann2'], 2, [22, 33, 52]],
            [['mai3', 'ke2', 'gau5'], 2, [55, 25, 55]],
            [['koi1', 'nng6'], 1, [33, 25]],
            [['kann2', 'lai5', 'phong3', 'tsioh8', 'thau5'], 4, [25, 22, 55, 2, 55]],
            [['ti1', 'tann5', 'ngiau1'], 2, [33, 22, 33]],
            [['lur2'], 0, [52]],
            [['kai5', 'nuann6', 'tshiu1'], 2, [22, 21, 33]],
            [['mai3', 'suann3', 'phui3'], 2, [55, 55, 212]],
            [['nan2'], 0, [52]],
            [['nan5', 'hiann1'], 1, [22, 33]],
            [['nan5', 'ti6'], 1, [22, 25]],
            [['hua5'], 0, [55]],
            [['ui5', 'kui3'], 1, [22, 212]],
            [['u6', 'liau2', 'ua2'], 2, [21, 25, 52]],
            [['tsu2', 'jin5'], 1, [25, 55]],
            [['tshai5', 'iang2', 'lur2'], 2, [22, 25, 52]],
            [['bo5', 'liau2', 'ua2'], 2, [22, 25, 52]],
            [['lur2', 'ia7', 'tua7', 'poh4', 'khui3'], 4, [25, 21, 21, 5, 212]],
            [['i1', 'tann3', 'ue7'], 2, [33, 55, 22]],
            [['sui1', 'jian5', 'm7', 'hah8', 'thiann1'], 4, [33, 22, 21, 2, 33]],
            [['si6', 'tann3', 'tau6', 'li2'], 3, [21, 55, 21, 52]],
            [['ia7', 'u6', 'kui2', 'siann5'], 1, [21, 25, 212, 21]],
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
