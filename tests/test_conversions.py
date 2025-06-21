import unittest
import pujutils
from pujcommon import Accent, Pronunciation
from pathlib import Path


class ConversionTestCase(unittest.TestCase):
    def setUp(self):
        self.pujutils = pujutils.PUJUtils(
            (Path(__file__).parent / '..' / 'dist' / 'accents.pb').resolve(),
            (Path(__file__).parent / '..' / 'dist' / 'entries.pb').resolve(),
        )
        pass

    def test_puj_pronunciation_to_written(self):
        expect = lambda initial, final, tone, s: self.assertEqual(Pronunciation(initial, final, tone).to_written(), s)

        expect('p', 'eh', 8, 'péh')
        expect('0', 'ue', 7, 'uē')
        expect('j', 'i', 7, 'jī')
        expect('p', 'eng', 1, 'peng')
        expect('0', 'im', 1, 'im')
        expect('h', 'uang', 1, 'huang')
        expect('0', 'uann', 3, 'uànn')

        expect('t', 'iong', 1, 'tiong')
        expect('h', 'ua', 5, 'huâ')
        expect('n', 'ang', 5, 'nâng')
        expect('m', 'in', 5, 'mîn')
        expect('k', 'ang', 7, 'kāng')
        expect('h', 'ua', 5, 'huâ')
        expect('k', 'ok', 4, 'kok')

        expect('l', 'v', 2, 'lṳ́')
        expect('t', 'i', 1, 'ti')
        expect('0', 'iam', 5, 'iâm')
        expect('0', 'ua', 2, 'uá')
        expect('t', 'i', 1, 'ti')
        expect('tsh', 'ou', 3, 'tshòu')
        expect('t', 'io', 5, 'tiô')
        expect('s', 'uann', 1, 'suann')
        expect('n', 'ang', 5, 'nâng')
        expect('m', 'in', 5, 'mîn')
        expect('ts', 'u', 3, 'tsù')
        expect('0', 'i', 3, 'ì')
        expect('b', 'i', 2, 'bí')
        expect('h', 'ua', 5, 'huâ')
        expect('0', 'ue', 1, 'ue')
        expect('m', 'ng', 2, 'mńg')
        expect('s', 'ui', 6, 'suĩ')


if __name__ == '__main__':
    unittest.main()
