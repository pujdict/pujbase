# -*- coding: utf-8 -*-
from pathlib import Path
import yaml
from entries_pb2 import *
from accents_pb2 import *


def _verify_pronunciation(entry: Entry):
    pron = entry.pron
    if pron.final[-1] in ['p', 't', 'k', 'h']:
        assert pron.tone in [4, 8], f"入声声调错误: {pron.tone} {entry}"
    else:
        assert pron.tone in [1, 2, 3, 5, 6, 7], f"舒声声调错误: {pron.tone} {entry}"
    if pron.tone in [4, 8]:
        assert pron.final[-1] in ['p', 't', 'k', 'h'], f"入声韵尾错误: {pron.final} {entry}"
    else:
        assert pron.final[-1] not in ['p', 't', 'k', 'h'], f"舒声韵尾错误: {pron.final} {entry}"


def _create_entries(yaml_entries) -> Entries:
    ESN = EntrySpecialNasalization
    EF = EntryFrequency
    EC = EntryCategory
    entries = Entries()
    index = 1
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
    for entry in entries.entries:
        _verify_pronunciation(entry)
    return entries


def main():
    entries_file = Path('../data/entries.yml')
    assert entries_file.exists(), 'entries.yml not found'
    with open(entries_file, 'r', encoding='utf-8') as f:
        yaml_entries = yaml.load(f, yaml.Loader)
    entries = _create_entries(yaml_entries)
    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/entries.pb', 'wb') as f:
        f.write(entries.SerializeToString())
    with open('../dist/entries.pb', 'rb') as f:
        entries = Entries()
        entries.ParseFromString(f.read())

    entries_index_map = {
        f"{entry.char},{entry.char_sim},{entry.pron.initial},{entry.pron.final},{entry.pron.tone}": entry.index
        for entry in entries.entries
    }

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
        exceptions = {}
        exceptions_list = v['exceptions']
        for k_original, v_expected in exceptions_list.items():
            entry_index = entries_index_map[k_original]
            ex_initial, ex_final, ex_tone = v_expected.split(',')
            ex_pron = Pronunciation(
                initial=ex_initial,
                final=ex_final,
                tone=int(ex_tone),
            )
            exceptions[entry_index] = ex_pron
        accents.accents.append(Accent(
            id=k,
            area=area,
            subarea=subarea,
            rules=rules,
            exceptions=exceptions,
        ))

    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/accents.pb', 'wb') as f:
        f.write(accents.SerializeToString())
    with open('../dist/accents.pb', 'rb') as f:
        accents = Accents()
        accents.ParseFromString(f.read())


if __name__ == '__main__':
    main()
