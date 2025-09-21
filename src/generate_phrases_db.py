import csv

import sys
import yaml

from phrases_pb2 import *
from pathlib import Path


def main_deprecated():
    phrases_dir = Path('../data/phrases')
    assert phrases_dir.exists() and phrases_dir.is_dir()
    phrases = Phrases()
    for phrase_file in phrases_dir.glob('*.csv'):
        with open(phrase_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) > 1
        for row in rows[1:]:
            phrase = Phrase(
                teochew=row[0],
                puj=row[1],
                mandarin=row[2] or None,
                node=row[3] or None,
            )
            phrases.phrases.append(phrase)
    with open('../dist/phrases.pb', 'wb') as f:
        f.write(phrases.SerializeToString())
    with open('../dist/phrases.pb', 'rb') as f:
        phrases = Phrases()
        phrases.ParseFromString(f.read())


def get_donor_lang(item):
    if isinstance(item, str):
        if any(s in item.upper() for s in ['粤语']):
            return PLDL_CANTONESE
        if any(s in item.upper() for s in ['普通话']):
            return PLDL_MANDARIN
        if any(s in item.upper() for s in ['英语']):
            return PLDL_ENGLISH
    return PLDL_NONE


PHRASE_TAG_MAP = {
    '动物': PT_ANIMALS,
    '蔬菜': PT_VEGETABLES,
}

def get_phrase_tag(item):
    if not item:
        return PT_NONE
    if isinstance(item, str):
        if item in PHRASE_TAG_MAP:
            return PHRASE_TAG_MAP[item]
        raise ValueError(f'Unknown phrase tag: {item}')
    return PT_NONE


def main():
    phrases_file = Path('../data/phrases.yml')
    assert phrases_file.exists(), 'phrases.yml not found'
    with open(phrases_file, 'r', encoding='utf-8') as f:
        yaml_phrases = yaml.load(f, yaml.Loader)
    phrases = Phrases()
    for i, yaml_phrase in enumerate(yaml_phrases):
        try:
            k, v = next(iter(yaml_phrase.items()))
            v = v or {}
            teochew_list, puj_list, cmn_list, word_class_list, tag_list = k.split('|')
            teochew_list = teochew_list.split('/')
            puj_list = puj_list.split('/')
            cmn_list = cmn_list.split('/')
            word_class_list = word_class_list.split('/')
            tag_list = [get_phrase_tag(x) for x in tag_list.split('/')] if tag_list else []
            accents = []
            for accent in v.get('accents', []):
                for accent_id, accent_puj in accent.items():
                    accents.append(PhraseAccent(
                        accent_id=accent_id,
                        puj=list(accent_puj),
                    ))
            loan = v.get('loan')
            donor_lang = PLDL_NONE if not loan else get_donor_lang(v.get('lang', '英语'))
            examples = []
            for example in v.get('examples', []):
                e_teochew, e_puj, e_mandarin = example
                examples.append(
                    PhraseExample(
                        teochew=e_teochew,
                        puj=e_puj,
                        mandarin=e_mandarin,
                    )
                )
            desc = v.get('desc')
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
                loan_word=loan,
                examples=examples,
            )
            phrases.phrases.append(phrase)
        except Exception as e:
            print(f'Error in phrase {i + 1}: {e}', file=sys.stderr)
            raise e
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/phrases.pb', 'wb') as f:
        f.write(phrases.SerializeToString())
    with open('../dist/phrases.pb', 'rb') as f:
        phrases = Phrases()
        phrases.ParseFromString(f.read())


if __name__ == '__main__':
    main()
