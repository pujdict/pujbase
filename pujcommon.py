from entries_pb2 import *

entry_index = 0


class FuzzyRule:
    description: str
    example_chars: list[str]

    def __init__(self):
        self._possible_pronunciations_map: dict[Pronunciation, Pronunciation] = {}
        self._possible_pronunciations_map_reverse: dict[Pronunciation, list[Pronunciation]] = {}
        pass

    def _fuzzy(self, result: Pronunciation):
        pass

    def fuzzy_result(self, origin: Pronunciation) -> Pronunciation:
        if origin.SerializeToString() in self._possible_pronunciations_map:
            return self._possible_pronunciations_map[origin.SerializeToString()]
        result = Pronunciation()
        result.CopyFrom(origin)
        self._fuzzy(result)
        return result

    def cache_possible_pronunciations_map(self, possible_pronunciations: list[Pronunciation]):
        self._possible_pronunciations_map = {}
        self._possible_pronunciations_map_reverse = {}
        for pronunciation in possible_pronunciations:
            fuzzy_pronunciation = Pronunciation()
            fuzzy_pronunciation.CopyFrom(pronunciation)
            self._fuzzy(fuzzy_pronunciation)
            self._possible_pronunciations_map[pronunciation.SerializeToString()] = fuzzy_pronunciation
            self._possible_pronunciations_map_reverse.setdefault(fuzzy_pronunciation.SerializeToString(), []).append(
                pronunciation)


class FuzzyRule_V_As_U(FuzzyRule):
    description = '单元音 ur 转为 u。潮阳、普宁、惠来、陆丰等地的口音。'
    example_chars = ['书', '之', '居', '鱼']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'v':
            result.final = 'u'


class FuzzyRule_R_As_O(FuzzyRule):
    description = '单元音 er 转为 o。潮汕大部分地区口音。'
    example_chars = ['坐', '罪', '短', '退']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'r':
            result.final = 'o'


class FuzzyRule_R_As_E(FuzzyRule):
    description = '单元音 er 转为 e。陆丰口音。'
    example_chars = ['坐', '罪', '短', '退']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'r':
            result.final = 'e'


class FuzzyRule_RH_As_OH(FuzzyRule):
    description = '单元音 erh 转为 oh。潮汕大部分地区口音。'
    example_chars = ['夺', '绝', '鳕', '雪']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'rh':
            result.final = 'oh'


class FuzzyRule_RM_As_IAM(FuzzyRule):
    description = 'erm 转为 iam。庄组深摄部分字音。'
    example_chars = ['森', '参', '簪']

    def _fuzzy(self, result: Pronunciation):
        if result.final == 'rm':
            result.final = 'iam'


class FuzzyRule_EU_As_IU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'eu':
            result.final = 'iu'


class FuzzyRule_OINN_As_AINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'oinn':
            result.final = 'ainn'


class FuzzyRule_UOINN_As_UINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uoinn':
            result.final = 'uinn'


class FuzzyRule_UOINN_As_UAINN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uoinn':
            result.final = 'uainn'


class FuzzyRule_OI_As_UE(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['p', 'ph', 'm', 'b'] and result.final == 'oi':
            result.final = result.final.replace('oi', 'ue')


class FuzzyRule_OU_As_AU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.startswith('ou'):
            result.final = result.final.replace('ou', 'au')


class FuzzyRule_UE_As_UEI(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['ue', 'uenn', 'ueh']:
            result.final = result.final.replace('ue', 'uei')


class FuzzyRule_VN_As_IN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['vn', 'vt']:
            result.final = result.final.replace('v', 'i')


class FuzzyRule_IN_As_EN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['in', 'it']:
            result.final = result.final.replace('i', 'e')


class FuzzyRule_UENG_As_ENG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ueng':
            if result.initial == '0':
                result.final = 'eng'
            else:
                result.final = 'uang'


class FuzzyRule_UEK_As_UAK(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uek':
            result.final = 'uak'


class FuzzyRule_IO_As_IE(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final in ['io', 'ionn', 'ioh']:
            result.final = result.final.replace('io', 'ie')


class FuzzyRule_IAU_As_IEU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.startswith('iau'):
            result.final = result.final.replace('iau', 'ieu')


class FuzzyRule_IAU_As_IOU(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'iau':
            result.final = result.final.replace('iau', 'iou')


class FuzzyRule_IAN_As_IEN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ian':
            result.final = 'ien'
        elif result.final == 'iat':
            result.final = 'iet'


class FuzzyRule_UAN_As_UEN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'uan':
            result.final = 'uen'
        elif result.final == 'uat':
            result.final = 'uet'


class FuzzyRule_IAM_As_IEM(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'iam':
            result.final = 'iem'
        elif result.final == 'iap':
            result.final = 'iep'


class FuzzyRule_N_As_L_ForMEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m') and result.initial == 'n':
            result.initial = 'l'


class FuzzyRule_N_As_L_ForNOrNGEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'n' and (result.final.endswith('n') or result.final.endswith('ng')):
            result.initial = 'l'


class FuzzyRule_L_As_N_ForMEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m') and result.initial == 'l':
            result.initial = 'n'


class FuzzyRule_MU_As_BU_ForNasalEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'm' and (
                result.final.endswith('m') or result.final.endswith('n') or result.final.endswith('ng')):
            result.initial = 'b'


class FuzzyRule_BU_As_MU_ForNasalEnding(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial == 'b' and (
                result.final.endswith('m') or result.final.endswith('n') or result.final.endswith('ng')):
            result.initial = 'm'


class FuzzyRule_N_As_NG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('n'):
            result.final = result.final.replace('n', 'ng')
        elif result.final.endswith('t'):
            result.final = result.final.replace('t', 'k')


class FuzzyRule_M_As_NG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final.endswith('m'):
            result.final = result.final.replace('m', 'ng')
        elif result.final.endswith('p'):
            result.final = result.final.replace('p', 'k')


class FuzzyRule_ENG_As_EN(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'eng':
            result.final = 'en'
        elif result.final == 'ek':
            result.final = 'et'


class FuzzyRule_NG_As_UNG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['p', 'ph', 'm', 'b'] and result.final == 'ng':
            result.final = 'ung'


class FuzzyRule_NG_As_VNG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.final == 'ng' and result.initial not in ['h', '0']:
            result.final = 'vng'


class FuzzyRule_IONG_As_ONG(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        if result.initial in ['t', 'th', 'n', 'l', 'ts', 'tsh', 's', 'j'] and result.final == 'iong':
            result.final = 'ong'
        elif result.initial in ['t', 'n', 'l', 'ts', 'tsh', 's', 'j'] and result.final == 'iok':
            result.final = 'ok'


class FuzzyRule_RemoveApostrophe(FuzzyRule):
    def _fuzzy(self, result: Pronunciation):
        result.final = result.final.replace("'", '')


class FuzzyRuleGroup(FuzzyRule):
    index: int
    name: str
    rules: list[FuzzyRule]

    def _fuzzy(self, result: Pronunciation):
        for rule in self.rules:
            rule._fuzzy(result)


class FuzzyRulesGroup_Dummy(FuzzyRuleGroup):
    index = 0
    name = '辞典'
    rules = []


class FuzzyRulesGroup_ChaoZhou(FuzzyRuleGroup):
    index = 1
    name = '潮州'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_IO_As_IE(),
        FuzzyRule_IAU_As_IEU(),
        FuzzyRule_IAN_As_IEN(),
        FuzzyRule_UAN_As_UEN(),
        FuzzyRule_IAM_As_IEM(),
        FuzzyRule_N_As_L_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_UNG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_XiQiang(FuzzyRuleGroup):
    index = 2
    name = '戏腔'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_IO_As_IE(),
        FuzzyRule_IAU_As_IOU(),
        FuzzyRule_N_As_L_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_N_As_NG(),
    ]


class FuzzyRulesGroup_ChaoAn(FuzzyRuleGroup):
    index = 3
    name = '潮安'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_OI_As_UE(),
        FuzzyRule_IAN_As_IEN(),
        FuzzyRule_N_As_L_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_FengShun(FuzzyRuleGroup):
    index = 4
    name = '丰顺'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_IO_As_IE(),
        FuzzyRule_IAU_As_IEU(),
        FuzzyRule_IAN_As_IEN(),
        FuzzyRule_UAN_As_UEN(),
        FuzzyRule_IAM_As_IEM(),
        FuzzyRule_N_As_L_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_ENG_As_EN(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_RaoPing(FuzzyRuleGroup):
    index = 5
    name = '饶平'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_OI_As_UE(),
        FuzzyRule_N_As_L_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_BU_As_MU_ForNasalEnding(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_ChengHai(FuzzyRuleGroup):
    index = 6
    name = '澄海'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_UENG_As_ENG(),
        FuzzyRule_UEK_As_UAK(),
        FuzzyRule_IO_As_IE(),
        FuzzyRule_IAU_As_IOU(),
        FuzzyRule_L_As_N_ForMEnding(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_M_As_NG(),
        FuzzyRule_NG_As_UNG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_ShanTou(FuzzyRuleGroup):
    index = 7
    name = '汕头'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_UOINN_As_UINN(),
        FuzzyRule_UENG_As_ENG(),
        FuzzyRule_UEK_As_UAK(),
        FuzzyRule_IO_As_IE(),
        FuzzyRule_IAU_As_IOU(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_UNG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_JieYang(FuzzyRuleGroup):
    index = 8
    name = '揭阳'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_OINN_As_AINN(),
        FuzzyRule_UOINN_As_UAINN(),
        FuzzyRule_N_As_L_ForNOrNGEnding(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_VN_As_IN(),
        FuzzyRule_IN_As_EN(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_IONG_As_ONG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_ChaoYang(FuzzyRuleGroup):
    index = 9
    name = '潮阳'
    rules = [
        FuzzyRule_V_As_U(),
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_OINN_As_AINN(),
        FuzzyRule_UOINN_As_UAINN(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_VN_As_IN(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_PuNing(FuzzyRuleGroup):
    index = 10
    name = '普宁'
    rules = [
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_OINN_As_AINN(),
        FuzzyRule_UOINN_As_UAINN(),
        FuzzyRule_VN_As_IN(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_HuiLai(FuzzyRuleGroup):
    index = 11
    name = '惠来'
    rules = [
        FuzzyRule_V_As_U(),
        FuzzyRule_R_As_O(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_OINN_As_AINN(),
        FuzzyRule_UOINN_As_UAINN(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_VN_As_IN(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_RemoveApostrophe(),
    ]


class FuzzyRulesGroup_LuFeng(FuzzyRuleGroup):
    index = 12
    name = '陆丰'
    rules = [
        FuzzyRule_V_As_U(),
        FuzzyRule_R_As_E(),
        FuzzyRule_RH_As_OH(),
        FuzzyRule_RM_As_IAM(),
        FuzzyRule_EU_As_IU(),
        FuzzyRule_OINN_As_AINN(),
        FuzzyRule_UOINN_As_UAINN(),
        FuzzyRule_OU_As_AU(),
        FuzzyRule_MU_As_BU_ForNasalEnding(),
        FuzzyRule_UE_As_UEI(),
        FuzzyRule_N_As_NG(),
        FuzzyRule_NG_As_VNG(),
        FuzzyRule_RemoveApostrophe(),
    ]


BUILTIN_FUZZY_RULE_GROUPS = [
    FuzzyRulesGroup_Dummy(),
    FuzzyRulesGroup_ChaoZhou(),
    FuzzyRulesGroup_XiQiang(),
    FuzzyRulesGroup_ChaoAn(),
    FuzzyRulesGroup_FengShun(),
    FuzzyRulesGroup_RaoPing(),
    FuzzyRulesGroup_ChengHai(),
    FuzzyRulesGroup_ShanTou(),
    FuzzyRulesGroup_JieYang(),
    FuzzyRulesGroup_ChaoYang(),
    FuzzyRulesGroup_PuNing(),
    FuzzyRulesGroup_HuiLai(),
    FuzzyRulesGroup_LuFeng(),
]
