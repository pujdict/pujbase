import csv

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
    if isinstance(item, str):
        if item in PHRASE_TAG_MAP:
            return PHRASE_TAG_MAP[item]
    return PT_NONE


def get_list_of_str(item):
    if not item:
        return []
    if isinstance(item, str):
        return [item]
    return item


def main():
    phrases_file = Path('../data/phrases.yml')
    assert phrases_file.exists(), 'phrases.yml not found'
    with open(phrases_file, 'r', encoding='utf-8') as f:
        yaml_phrases = yaml.load(f, yaml.Loader)
    phrases = Phrases()
    for i, yaml_phrase in enumerate(yaml_phrases):
        k, v = next(iter(yaml_phrase.items()))
        v = v or {}
        teochew, puj, word_class, tag = k.split(',')
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
        cmn = get_list_of_str(v.get('cmn'))
        char_var = get_list_of_str(v.get('char-var'))
        puj_var = get_list_of_str(v.get('puj-var'))
        tag = get_phrase_tag(tag)
        tag_var = [get_phrase_tag(s) for s in get_list_of_str(v.get('tag-var'))]
        phrase = Phrase(
            index=i + 1,
            teochew=teochew,
            puj=puj,
            tag=tag,
            word_class=word_class,
            desc=desc,
            cmn=cmn,
            char_var=char_var,
            puj_var=puj_var,
            tag_var=tag_var,
            accents=accents,
            donor_lang=donor_lang,
            loan_word=loan,
            examples=examples,
        )
        phrases.phrases.append(phrase)
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/phrases.pb', 'wb') as f:
        f.write(phrases.SerializeToString())
    with open('../dist/phrases.pb', 'rb') as f:
        phrases = Phrases()
        phrases.ParseFromString(f.read())


if __name__ == '__main__':
    main()
