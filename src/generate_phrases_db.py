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


def main():
    phrases_file = Path('../data/phrases.yml')
    assert phrases_file.exists(), 'phrases.yml not found'
    with open(phrases_file, 'r', encoding='utf-8') as f:
        yaml_phrases = yaml.load(f, yaml.Loader)
    phrases = Phrases()
    for i, yaml_phrase in enumerate(yaml_phrases):
        k, v = next(iter(yaml_phrase.items()))
        teochew, puj, word_class = k.split(',')
        phrase = Phrase(
            index=i + 1,
            teochew=teochew,
            puj=puj,
            word_class=word_class,
            desc=(v or {}).get('desc'),
            cmn=list((v or {}).get('cmn') or []),
            char_var=list((v or {}).get('char_var') or []),
            puj_var=list((v or {}).get('puj_var') or []),
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
