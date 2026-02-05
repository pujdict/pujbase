import unittest
import libpuj.pujutils
from pathlib import Path
import csv
import libpuj.pujcommon
import typing


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.pujutils = libpuj.pujutils.PUJUtils(
            (Path(__file__).parent / '..' / 'dist' / 'accents.pb').resolve(),
            (Path(__file__).parent / '..' / 'dist' / 'entries.pb').resolve(),
        )

    def test_accents_expected(self):
        accents_expected_csv = Path(__file__).parent / '..' / 'data' / 'accents_expected.csv'
        self.assertTrue(accents_expected_csv.is_file())
        csv_content = list(csv.reader(open(accents_expected_csv)))
        header = csv_content[0]
        for row in csv_content[1:]:
            self.assertEqual(len(row), len(header))
        length = len(header)
        cur_accent: typing.Optional[libpuj.pujcommon.Accent] = None
        for row in csv_content[1:]:
            for i in range(length):
                if i == 0:
                    accent_name, accent_id = row[i].split('/')
                    cur_accent = self.pujutils.get_accent(accent_id)
                    self.assertIsNotNone(cur_accent)
                else:
                    char, std_pron_str = header[i].split('/')
                    accent_pron_str_expect = row[i]
                    accent_pron_fuzzy = cur_accent.fuzzy_result(libpuj.pujcommon.Pronunciation.from_combination(std_pron_str))
                    self.assertEqual(accent_pron_str_expect,
                                     accent_pron_fuzzy.to_combination(),
                                     f"ACCENT: {accent_name} "
                                     f"{char} "
                                     f"STD: {std_pron_str} "
                                     f"EXPECT IN TABLE: {accent_pron_str_expect} "
                                     f"FOUND: {accent_pron_fuzzy.to_combination()}")


if __name__ == '__main__':
    unittest.main()
