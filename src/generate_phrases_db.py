import csv
from phrases_pb2 import *
from pathlib import Path


def main():
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


if __name__ == '__main__':
    main()
