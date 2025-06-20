from pathlib import Path
from accents_pb2 import *

import yaml


def main():
    accents_file = Path('../data/accents.yml')
    assert accents_file.exists(), 'accents.yml not found'
    with open(accents_file, 'r', encoding='utf-8') as f:
        yaml_entries = yaml.load(f, yaml.Loader)
    accents = Accents()
    for k, v in yaml_entries.items():
        area = v['area']
        subarea = v['subarea']
        rules = v['rules']
        rules = [f'FR_{rule}' for rule in rules]
        accents.accents.append(Accent(
            id=k,
            area=area,
            subarea=subarea,
            rules=rules,
        ))
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/accents.pb', 'wb') as f:
        f.write(accents.SerializeToString())
    with open('../dist/accents.pb', 'rb') as f:
        accents = Accents()
        accents.ParseFromString(f.read())


if __name__ == '__main__':
    main()
