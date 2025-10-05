# -*- coding: utf-8 -*-
import re
from pathlib import Path

import sys
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
    EF = EntryFrequency
    EC = EntryCategory
    entries = Entries()
    index = 1
    for yaml_ent in yaml_entries:
        chars, pronunciations = yaml_ent
        char, char_sim = chars.split(',')
        try:
            for pronunciation, details in pronunciations.items():
                initial, final, tone, cat, freq, char_ref = pronunciation.split(',')
                if initial == '0':
                    initial = ''
                entry_details: list[EntryDetail] = []
                pron_aka: list[Entry.PronunciationAka] = []
                accents_nasalized: list[str] = []
                if details:
                    for details_k, details_v in details.items():
                        if details_k in ['aka', 'aka_replace']:
                            aka_list = details_v
                            for aka_accent_id, aka_accent_pron in aka_list.items():
                                prons_aka = []
                                for pron_raw in aka_accent_pron.split('/'):
                                    pron_initial, pron_final, pron_tone = pron_raw.split(',')
                                    if pron_initial == '0':
                                        pron_initial = ''
                                    prons_aka.append(Pronunciation(
                                        initial=pron_initial,
                                        final=pron_final,
                                        tone=int(pron_tone),
                                    ))
                                pron_aka.append(Entry.PronunciationAka(
                                    accent_id=aka_accent_id,
                                    prons=prons_aka,
                                    replace=details_k == 'aka_replace',
                                ))
                            continue
                        if details_k == 'nasalize':
                            accents_nasalized = details_v
                            continue
                        detail = EntryDetail(meaning=details_k, examples=[])
                        if details_v:
                            for teochew_puj_mandarin in details_v:
                                teochew, puj, mandarin = teochew_puj_mandarin
                                detail.examples.append(EntryDetailExample(teochew=teochew, puj=puj, mandarin=mandarin))
                        entry_details.append(detail)
                pron = Pronunciation(initial=initial, final=final, tone=int(tone))
                entries.entries.append(Entry(
                    index=index,
                    char=char,
                    char_sim=char_sim,
                    pron=pron,
                    cat=EC.Name(int(cat)),
                    freq=EF.Name(int(freq)),
                    char_ref=char_ref,
                    details=entry_details,
                    accents_nasalized=accents_nasalized,
                    pron_aka=pron_aka,
                ))
                index += 1
        except Exception as e:
            print(f'Error {e} of char {char}', file=sys.stderr)
            raise
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

    fuzzy_rules_file = Path('../data/fuzzy_rules.yml')
    assert fuzzy_rules_file.exists(), 'fuzzy_rules.yml not found'
    with open(fuzzy_rules_file, 'r', encoding='utf-8') as f:
        yaml_fuzzy_rules = yaml.load(f, yaml.Loader)
    fuzzy_rule_descriptors = []
    for fuzzy_rule_id, fuzzy_rule_actions in yaml_fuzzy_rules.items():
        actions = []
        for fuzzy_rule_action in fuzzy_rule_actions:
            action, pattern, replacement_dollar, _ = fuzzy_rule_action.split('/')
            replacement_backslash = re.sub(r'\$(\d)', r'\\\1', replacement_dollar)
            actions.append(FuzzyRuleAction(
                action=action,
                pattern=pattern,
                replacement_dollar=replacement_dollar,
                replacement_backslash=replacement_backslash,
            ))
        fuzzy_rule_descriptors.append(FuzzyRuleDescriptor(
            id='FR_' + fuzzy_rule_id,
            actions=actions,
        ))

    accents_file = Path('../data/accents.yml')
    assert accents_file.exists(), 'accents.yml not found'
    with open(accents_file, 'r', encoding='utf-8') as f:
        yaml_entries = yaml.load(f, yaml.Loader)
    accents = Accents()
    accents.fuzzy_rule_descriptors.extend(fuzzy_rule_descriptors)
    for k, v in yaml_entries.items():
        area = v['area']
        subarea = v['subarea']
        rules = v['rules']
        rules = [f'FR_{rule}' for rule in rules]
        tones = v['tones']
        citation = tones['citation']
        sandhi = tones['sandhi']
        neutral = tones['neutral']
        specials = tones.get('specials') or []
        specials = [ToneSpecial.Value(f"TS_{special_name}") for special_name in specials]
        tones = Tones(citation=citation, sandhi=sandhi, neutral=neutral, specials=specials)
        accents.accents.append(Accent(
            id=k,
            area=area,
            subarea=subarea,
            rules=rules,
            tones=tones,
        ))

    Path('../dist').mkdir(exist_ok=True)
    with open('../dist/accents.pb', 'wb') as f:
        f.write(accents.SerializeToString())
    with open('../dist/accents.pb', 'rb') as f:
        accents = Accents()
        accents.ParseFromString(f.read())


if __name__ == '__main__':
    main()
