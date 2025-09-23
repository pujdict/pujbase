import csv

import sys
import yaml

from phrases_pb2 import *
from pathlib import Path

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
        if item.isalpha():
            return item
        raise ValueError(f'Unknown word class: {item}')
    return ''


PHRASE_TAG_MAP = {
    '动物': PT_ANIMALS,
    '水产': PT_SEAFOOD,
    '蔬菜': PT_VEGETABLES,
    '水果': PT_FRUITS,
    '特产': PT_SPECIALTIES,
    '人称': PT_RELATIONSHIPS,
    '人体': PT_HUMAN_BODY,
    '音乐': PT_HUMAN_BODY,
    '拟声拟态': PT_ONOMATOPOEIA,
    'AAB': PT_ONOMATOPOEIA_AAB,
    'XX叫': PT_ONOMATOPOEIA_KIO,
}


def get_phrase_tag(item):
    if not item:
        return PT_NONE
    if isinstance(item, str):
        if item in PHRASE_TAG_MAP:
            return PHRASE_TAG_MAP[item]
        raise ValueError(f'Unknown phrase tag: {item}')
    return PT_NONE


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
    with open(phrases_file, 'r', encoding='utf-8') as f:
        yaml_phrases = yaml.load(f, yaml.Loader)
    phrases = Phrases()
    for i, yaml_phrase in enumerate(yaml_phrases):
        k, v = next(iter(yaml_phrase.items()))
        v = v or {}
        try:
            teochew_list, puj_list, cmn_list, word_class_list, tag_list = k.split('|')
            teochew_list = teochew_list.split('/')
            puj_list = puj_list.split('/')
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
            informal = get_list_of_str(v.get('informal'))
            phrase = Phrase(
                index=i + 1,
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
            print(f'Error in phrase {i + 1} {k} {v}: {e}', file=sys.stderr)
            raise e
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/phrases.pb', 'wb') as f:
        f.write(phrases.SerializeToString())
    with open('../dist/phrases.pb', 'rb') as f:
        phrases = Phrases()
        phrases.ParseFromString(f.read())


if __name__ == '__main__':
    main()
