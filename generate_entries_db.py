# -*- coding: utf-8 -*-
from pathlib import Path
import yaml
from puj.entries_pb2 import *


def _create_entries(yaml_entries) -> Entries:
    ESN = EntrySpecialNasalization
    EF = EntryFrequency
    EC = EntryCategory
    entries = Entries()
    index = 0
    for yaml_ent in yaml_entries:
        chars, pronunciations = yaml_ent
        char, char_sim = chars.split(',')
        for pronunciation, details in pronunciations.items():
            initial, final, tone, sp_nasal, cat, freq, char_ref = pronunciation.split(',')
            entry_details: list[EntryDetail] = []
            if details:
                for meaning, examples in details.items():
                    detail = EntryDetail(meaning=meaning, examples=[])
                    if examples:
                        for teochew_puj_mandarin in examples:
                            teochew, puj, mandarin = teochew_puj_mandarin
                            detail.examples.append(EntryDetailExample(teochew=teochew, puj=puj, mandarin=mandarin))
                    entry_details.append(detail)
            pron = Pronunciation(initial=initial, final=final, tone=int(tone), sp_nasal=ESN.Name(int(sp_nasal)))
            entries.entries.append(Entry(
                index=index,
                char=char,
                char_sim=char_sim,
                pron=pron,
                cat=EC.Name(int(cat)),
                freq=EF.Name(int(freq)),
                char_ref=char_ref,
                details=entry_details,
            ))
            index += 1
    return entries


def main():
    entries_file = Path('entries.yml')
    assert entries_file.exists(), 'entries.yml not found'
    with open(entries_file, 'r', encoding='utf-8') as f:
        yaml_entries = yaml.load(f, yaml.Loader)
    entries = _create_entries(yaml_entries)
    Path('dist').mkdir(exist_ok=True)
    with open('dist/entries.pb', 'wb') as f:
        f.write(entries.SerializeToString())
    with open('dist/entries.pb', 'rb') as f:
        entries = Entries()
        entries.ParseFromString(f.read())


if __name__ == '__main__':
    main()
