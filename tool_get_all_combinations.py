from puj.entries_pb2 import *
from pujcommon import *


def pron_to_str(pron: Pronunciation):
    return f'{pron.initial}{pron.final}{pron.tone}'


def print_combinations(entries):
    pron : dict[str, list[Entry]] = {}
    initials = ['p','ph','m','b','pf','phf','mv','bv','t','th','n','l','k','kh','ng','g','h','f','ts','tsh','s','j','0']
    finals = set()
    for entry in entries.entries:
        finals.add(entry.pron.final)
        pron.setdefault(pron_to_str(entry.pron), []).append(entry)
        for rule in BUILTIN_FUZZY_RULE_GROUPS:
            p = Pronunciation()
            p.CopyFrom(entry.pron)
            p = rule.fuzzy_result(p)
            finals.add(p.final)
            pron.setdefault(pron_to_str(p), []).append(entry)
    # for final in sorted(finals):
    #     print(final)
    # print(len(pron))
    with open('combinations2.csv', 'w') as f:
        for initial in initials:
            for final in sorted(finals):
                for i in range(8):
                    j = i + 1
                    if (j == 4 or j == 8) ^ (final[-1] in ['p','t','k','h']):
                        continue
                    comb = f'{initial}{final}{j}'
                    if comb not in pron:
                        f.write(f'{initial},{final},{j},\n')
                    else:
                        f.write(f'{initial},{final},{j},{pron[comb][0].char}\n')


def print_all_in_table_combinations(entries):
    combinations = set()
    for entry in entries:
        comb = pron_to_str(entry.pron)
        combinations.add(comb)
    for comb in sorted(combinations):
        print(comb)
    print(len(combinations))


def print_extra_combinations_chao_zhou(entries):
    combinations = {}
    for entry in entries.entries:
        comb = pron_to_str(entry.pron)
        combinations[comb] = entry.pron
    rule_chao_zhou = FuzzyRulesGroup_ChaoZhou()
    fuzzy_combinations = set()
    for comb, pron in combinations.items():
        res_pron = rule_chao_zhou.fuzzy_result(pron)
        res_comb = pron_to_str(res_pron)
        if res_comb.startswith('bang'):
            res_pron = rule_chao_zhou.fuzzy_result(pron)
            res_comb = pron_to_str(res_pron)

        if res_comb not in combinations:
            fuzzy_combinations.add(res_comb)
    for comb in sorted(fuzzy_combinations):
        print(comb)
    print(len(fuzzy_combinations))


def main():
    with open('entries.pb', 'rb') as f:
        entries = Entries()
        entries.ParseFromString(f.read())
    print_all_in_table_combinations(entries.entries)
    print_extra_combinations_chao_zhou(entries)


if __name__ == '__main__':
    main()
