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


def main():
    phrases_file = Path('../data/phrases.yml')
    assert phrases_file.exists(), 'phrases.yml not found'
    with open(phrases_file, 'r', encoding='utf-8') as f:
        yaml_phrases = yaml.load(f, yaml.Loader)
    phrases = Phrases()
    for i, yaml_phrase in enumerate(yaml_phrases):
        k, v = next(iter(yaml_phrase.items()))
        v = v or {}
        teochew, puj, word_class = k.split(',')
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
        phrase = Phrase(
            index=i + 1,
            teochew=teochew,
            puj=puj,
            word_class=word_class,
            desc=v.get('desc'),
            cmn=list(v.get('cmn', [])),
            char_var=list(v.get('char_var', [])),
            puj_var=list(v.get('puj_var', [])),
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
