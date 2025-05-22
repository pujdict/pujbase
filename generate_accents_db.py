from pathlib import Path
from puj.accents_pb2 import *

import yaml


def main():
    accents_file = Path('accents.yml')
    assert accents_file.exists(), 'accents.yml not found'
    with open(accents_file, 'r', encoding='utf-8') as f:
        yaml_entries = yaml.load(f, yaml.Loader)
    ent_all = yaml_entries['All']
    rules_all = set(ent_all['rules'])
    accents = Accents()
    for k, v in yaml_entries.items():
        if k == 'All':
            continue
        area = v['area']
        subarea = v['subarea']
        rules = v['rules']
        for rule in rules:
            assert rule in rules_all, f'{rule} not in rules_all'
        accents.accents.append(Accent(
            area=area,
            subarea=subarea,
            rules=rules,
        ))
    Path('dist').mkdir(exist_ok=True)
    with open('dist/accents.pb', 'wb') as f:
        f.write(accents.SerializeToString())
    with open('dist/accents.pb', 'rb') as f:
        accents = Accents()
        accents.ParseFromString(f.read())


if __name__ == '__main__':
    main()
