import unittest
import libpuj.pujutils
from libpuj.pujcommon import Accent, Pronunciation, IPAPronunciation
from pathlib import Path


class ConversionTestCase(unittest.TestCase):
    def setUp(self):
        self.pujutils = libpuj.pujutils.PUJUtils(
            (Path(__file__).parent / '..' / 'dist' / 'accents.pb').resolve(),
            (Path(__file__).parent / '..' / 'dist' / 'entries.pb').resolve(),
        )
        pass

    def test_puj_pronunciation_to_written(self):
        expect = lambda initial, final, tone, s: self.assertEqual(Pronunciation(initial, final, tone).to_written(), s)

        # 特殊韵母
        expect('l', 'ur', 2, 'lṳ́')
        expect('l', 'or', 5, 'lô̤')
        expect('0', 'ng', 5, 'n̂g')
        expect('h', 'ng', 5, 'hn̂g')
        expect('0', 'ngh', 8, 'ńgh')
        expect('0', 'innh', 8, 'ínnh')
        expect('0', 'm', 2, 'ḿ')

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

        expect('l', 'ur', 2, 'lṳ́')
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

    def test_puj_pronunciation_to_ipa_pronunciation(self):
        expect = lambda p_i, p_f, p_t, i_i, i_f, i_t: self.assertEqual(
            Pronunciation(p_i, p_f, p_t).to_ipa(),
            IPAPronunciation(i_i, i_f, i_t))
        expect('0', 'ng', 5, '', 'N=', 5)
        expect('h', 'ng', 5, 'N_0', 'N=', 5)
        expect('h', 'ngh', 4, 'N_0', 'N=_}', 4)
        expect('h', 'm', 7, 'm_0', 'm=', 7)

    def test_ipa_pronunciation_to_written(self):
        upper_nums = [
            '',
            "\u00b9",
            "\u00b2",
            "\u00b3",
            "\u2074",
            "\u2075",
            "\u2076",
            "\u2077",
            "\u2078",
            "\u2079",
        ]
        expect = lambda initial, final, tone, w_initial, w_final, w_tone: self.assertEqual(
            IPAPronunciation(initial, final, tone).to_written(),
            f"{w_initial}{w_final}{upper_nums[w_tone]}")
        
        # 特殊音素
        expect('', 'N=', 5, '', 'ŋ̍', 5)
        expect('N_0', 'N=', 5, 'ŋ̊', 'ŋ̍', 5)
        expect('N_0', 'N=_}', 4, 'ŋ̊', 'ŋ̍̚', 4)
        expect('p', 'N=', 5, 'p', 'ŋ̍', 5)
        expect('t_h', 'N=', 5, 'tʰ', 'ŋ̍', 5)

        expect('p', 'e?', 8, 'p', 'eʔ', 8)
        expect('?', 'ue', 7, 'ʔ', 'ue', 7)
        expect('dz', 'i', 7, 'dz', 'i', 7)

        expect('t', 'ioN', 1, 't', 'ioŋ', 1)
        expect('h', 'ua', 5, 'h', 'ua', 5)
        expect('n', 'aN', 5, 'n', 'aŋ', 5)
        expect('m', 'in', 5, 'm', 'in', 5)
        expect('k', 'aN', 7, 'k', 'aŋ', 7)
        expect('h', 'ua', 5, 'h', 'ua', 5)
        expect('k', 'ok_}', 4, 'k', 'ok̚', 4)

        expect('ts', 'ek_}', 8, 'ts', 'ek̚', 8)
        expect('p_h', 'ian', 3, 'pʰ', 'ian', 3)
        expect('ts_h', 'i', 1, 'tsʰ', 'i', 1)
        expect('ts_h', 'eN', 5, 'tsʰ', 'eŋ', 5)
        expect('s', 'i', 6, 's', 'i', 6)
        expect('k_h', 'ou', 2, 'kʰ', 'ou', 2)
        expect('l', 'uan', 3, 'l', 'uan', 3)

        expect('ts', 'ap_}', 8, 'ts', 'ap̚', 8)
        expect('dz', 'i', 7, 'dz', 'i', 7)
        expect('l', 'ou', 7, 'l', 'ou', 7)
        expect('p', 'i~', 1, 'p', 'ĩ', 1)
        expect('p', 'a', 2, 'p', 'a', 2)
        expect('l', 'M', 2, 'l', 'ɯ', 2)
        expect('h', 'u', 1, 'h', 'u', 1)
        expect('h', 'am', 3, 'h', 'am', 3)


if __name__ == '__main__':
    unittest.main()
