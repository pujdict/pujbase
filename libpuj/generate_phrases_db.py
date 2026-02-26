import csv

import sys
import yaml
import libpuj.pujcommon as pujcommon
import libpuj.pujutils as pujutils

from phrases_pb2 import *
from pathlib import Path

DATA_DIR_PATH = Path(__file__).parent.parent / 'data'
PHRASES_STD_DIR_PATH = DATA_DIR_PATH / 'pujcorpora' / 'std'
PHRASES_YML_FILES = list(PHRASES_STD_DIR_PATH.glob('**/*.std.yml')) + [
    DATA_DIR_PATH / 'phrases.yml'
]
DONOR_LANG_MAP = {
    '英语': PLDL_ENGLISH,
    '普通话': PLDL_MANDARIN,
    '粤语': PLDL_CANTONESE,
    '马来语': PLDL_MALAY,
    '印尼语': PLDL_INDONESIAN,
    '泰语': PLDL_THAI,
}


def get_donor_lang(item):
    if not item:
        return PLDL_NONE
    if isinstance(item, str):
        if item in DONOR_LANG_MAP:
            return DONOR_LANG_MAP[item]
        raise ValueError(f'Unknown donor language: {item}')
    return PLDL_NONE


def get_word_class(item):
    if not item:
        return ''
    if isinstance(item, str):
        if item.isalnum():
            return item
        raise ValueError(f'Unknown word class: {item}')
    return ''


PHRASE_TAG_MAP = {
    '': 0,
}


def get_phrase_tag(item) -> int:
    if not item:
        return 0
    if isinstance(item, str):
        if item not in PHRASE_TAG_MAP:
            PHRASE_TAG_MAP[item] = len(PHRASE_TAG_MAP)
        return PHRASE_TAG_MAP[item]
    return 0


def get_list_of_str(item):
    if not item:
        return []
    if isinstance(item, str):
        return [item]
    return item


def is_punctuation_full_width(c):
    return c in '，。？！：；、'


def main():
    phrases_file = Path('../data/phrases.yml')
    assert phrases_file.exists(), 'phrases.yml not found'
    phrases = Phrases()
    for path in PHRASES_YML_FILES:
        assert path.exists(), f'{path} not found'
        with open(path, 'r', encoding='utf-8') as f:
            yaml_phrases = yaml.load(f, yaml.Loader)
            add_phrase(phrases, yaml_phrases)
    # post_process_multiple_acceptable_written(phrases)
    phrases.phrase_tag_display.extend([''] * len(PHRASE_TAG_MAP))
    for k, v in PHRASE_TAG_MAP.items():
        phrases.phrase_tag_display[v] = k
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/phrases.pb', 'wb') as f:
        f.write(phrases.SerializeToString())
    with open('../dist/phrases.pb', 'rb') as f:
        phrases = Phrases()
        phrases.ParseFromString(f.read())


def verify_puj(puj_phrase: str):
    def assert_puj_word(puj_word: str, *args):
        matched = pujcommon.Pronunciation.REGEXP_WORD.match(puj_word)
        if not matched:
            raise ValueError(f'Invalid PUJ word: {puj_word}')
        if not matched.group('final'):
            raise ValueError(f'PUJ word without final: {puj_word}')
        if not matched.group('tone'):
            raise ValueError(f'PUJ word without tone: {puj_word}')
    pujutils.PUJUtils.for_each_word_in_sentence(puj_phrase, assert_puj_word)


def add_phrase(phrases: Phrases, yaml_phrases):
    i = len(phrases.phrases)
    for yaml_phrase in yaml_phrases:
        k, v = next(iter(yaml_phrase.items()))
        v = v or {}
        try:
            teochew_list, puj_list, cmn_list, word_class_list, tag_list = k.split('|')
            teochew_list = teochew_list.split('/')
            puj_list = puj_list.split('/')
            for puj in puj_list:
                verify_puj(puj)
            cmn_list = cmn_list.split('/')
            word_class_list = [get_word_class(x) for x in word_class_list.split('/')] if word_class_list else []
            tag_list = [get_phrase_tag(x) for x in tag_list.split('/')] if tag_list else []
            accents = []
            for accent in v.get('accents', []):
                for accent_id, accent_puj in accent.items():
                    accents.append(PhraseAccent(
                        accent_id=accent_id,
                        puj=list(accent_puj),
                    ))
            loan = v.get('loan')
            donor_lang, loan_word = None, None
            if loan:
                donor_lang, loan_word = loan.split('/')
                donor_lang = get_donor_lang(donor_lang)
            examples = []
            for example in v.get('examples', []):
                e_teochew, e_puj, e_mandarin = example
                e_teochew = e_teochew.split('/')
                e_puj = e_puj.split('/')
                e_mandarin = e_mandarin.split('/')
                examples.append(
                    PhraseExample(
                        teochew=e_teochew,
                        puj=e_puj,
                        mandarin=e_mandarin,
                    )
                )
            desc = v.get('desc')
            if desc and not is_punctuation_full_width(desc[-1]):
                desc += '。'
            informal = v.get('informal')
            informal = informal.split('/') if informal else []
            phrase = Phrase(
                index=i,
                teochew=teochew_list,
                puj=puj_list,
                cmn=cmn_list,
                word_class=word_class_list,
                tag=tag_list,
                desc=desc,
                accents=accents,
                donor_lang=donor_lang,
                loan_word=loan_word,
                examples=examples,
                informal=informal,
            )
            phrases.phrases.append(phrase)
        except Exception as e:
            print(f'Error in phrase {i} {k} {v}: {e}', file=sys.stderr)
            raise e
        i += 1


if __name__ == '__main__':
    main()
