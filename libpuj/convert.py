# -*- coding: utf-8 -*-
"""
潮汕方言各拼音方案之间的转换 API。

将 `pujcommon` 上零散的转换方法封装为可直接调用的纯函数，
供命令行工具 `puj.py` 及其他脚本复用。

内部以 `Pronunciation`（白话字，ASCII 形式存储）作为中间表示：
- 源方案解析器将单个拼音单词解析为 `Pronunciation`；
- 目标方案格式化器将 `Pronunciation` 输出为目标方案字符串。

目前支持的源方案：`puj`（白话字 ASCII 形式，如 `peng1`）、
`dp`（潮拼，如 `bêng1`）。
"""

from __future__ import annotations

import pathlib

from typing import Callable, Optional, Union

import libpuj.pujpb as pb

from .pujcommon import (
    Accent,
    ConversionError,
    DPPronunciation,
    Entry,
    FuzzyRuleDescriptor,
    IPAPronunciation,
    Pronunciation,
    PronunciationWilliamDuffus,
    Sentence,
)

__all__ = [
    'convert',
    'load_accents',
    'load_entries',
    'try_deaccent',
    'ConversionError',
    'SUPPORTED_SOURCES',
    'SUPPORTED_TARGETS',
]

# 口音（模糊音规则）对象的类型。
FuzzyRuleLike = Optional[Accent]

# 支持的源拼音方案标识。
SUPPORTED_SOURCES = ('apuj', 'puj', 'dp', 'duffus')
# 支持的目标拼音方案标识。
SUPPORTED_TARGETS = ('apuj', 'puj', 'dp', 'ipa', 'xsampa', 'duffus')


# 源方案名 -> 解析函数（单个拼音单词 -> Pronunciation）。
_SOURCE_PARSERS: dict[str, Callable[[str], Pronunciation]] = {
    'apuj': Pronunciation.from_combination,
    'puj': Pronunciation.from_written,
    'dp': lambda x: Pronunciation.from_dp(DPPronunciation.from_written(x)),
    'duffus': PronunciationWilliamDuffus.from_written
}


def _pron_to_apuj(pron: Pronunciation) -> str:
    """Pronunciation -> 白话字(ASCII 形式)。"""
    return pron.to_combination()


def _pron_to_puj(pron: Pronunciation) -> str:
    """Pronunciation -> 白话字(书面形式，含调符)。"""
    return pron.to_written()


def _pron_to_dp(pron: Pronunciation) -> str:
    """Pronunciation -> 潮拼 (DP)。"""
    return pron.to_dp().__str__()


def _pron_to_ipa(pron: Pronunciation) -> str:
    """Pronunciation -> 国际音标 (IPA，书面形式)。"""
    return pron.to_ipa().to_written()


def _pron_to_x_sampa(pron: Pronunciation) -> str:
    """Pronunciation -> X-SAMPA 式国际音标。"""
    return pron.to_ipa().to_x_sampa()


def _pron_to_duffus(pron: Pronunciation) -> str:
    return PronunciationWilliamDuffus(pron.initial, pron.final, pron.tone).to_written()


# 目标方案名 -> 格式化函数（Pronunciation -> 目标方案字符串）。
_TARGET_FORMATTERS: dict[str, Callable[[Pronunciation], str]] = {
    'apuj': _pron_to_apuj,
    'puj': _pron_to_puj,
    'dp': _pron_to_dp,
    'ipa': _pron_to_ipa,
    'xsampa': _pron_to_x_sampa,
    'duffus': _pron_to_duffus,
}

# 目标方案名 -> 对应的输出音标类（用于判断该方案是否区分大小写）。
_TARGET_OUTPUT_CLASS: dict[str, type] = {
    'apuj': Pronunciation,
    'puj': Pronunciation,
    'dp': DPPronunciation,
    'ipa': IPAPronunciation,
    'xsampa': IPAPronunciation,
    'duffus': PronunciationWilliamDuffus,
}


def _target_has_case(target: str) -> bool:
    """目标方案是否区分大小写（国际音标等为 False）。"""
    return getattr(_TARGET_OUTPUT_CLASS[target], 'has_case')


def _make_word_converter(source: str, target: str,
                         fuzzy_rule: FuzzyRuleLike = None) -> Callable[[str], str]:
    """
    构造将单个拼音单词从 `source` 转换为 `target` 的函数。

    若传入 `fuzzy_rule`（口音），则在解析后、格式化前应用口音模糊音规则
    （`fuzzy_rule.fuzzy_result`）。
    """
    parser = _SOURCE_PARSERS[source]
    formatter = _TARGET_FORMATTERS[target]

    def word_converter(word: str) -> str:
        pron = parser(word)
        if fuzzy_rule is not None:
            pron = fuzzy_rule.fuzzy_result(pron)
        return formatter(pron)

    return word_converter


def _convert_sentence(sentence: str, word_converter: Callable[[str], str],
                      has_case: bool = True) -> str:
    """
    将一句由多个拼音单词组成的话逐词转换。

    以空格与连字符（" ", "-", "--", "- ", " -", "-- ", " --" 等）分割单词，
    非单词片段（空格、连字符、标点等）原样保留。转换时先统一转为小写，
    结束后再根据原始句子的字母大小写恢复（参考前端 SPuj.ts 的
    `convertPlainPUJSentence`）。

    Args:
        sentence: 待转换的句子。
        word_converter: 将单个拼音单词转换为目标方案字符串的函数。
        has_case: 目标方案是否区分大小写。为 False（如国际音标）时不进行
            大小写恢复，因为大小写在音标中表示不同音素。

    Returns:
        转换后的句子字符串。
    """
    chunks: list[str] = []

    def on_word(word: str, next_hyphen_count: int) -> None:
        chunks.append(word_converter(word))

    def on_non_word(non_word: str) -> None:
        chunks.append(non_word)

    if has_case:
        Sentence.for_each_word_in_sentence(sentence.lower(), on_word, on_non_word)
        result = ''.join(chunks)
        letter_case = Sentence.determine_letter_case(sentence)
        result = Sentence.change_letter_case(result, letter_case)
    else:
        Sentence.for_each_word_in_sentence(sentence, on_word, on_non_word)
        result = ''.join(chunks)
    return result


def load_accents(accent_pb_path: Union[str, pathlib.Path]) -> dict[str, Accent]:
    """
    从 protobuf 数据文件加载全部口音（`Accent`）对象。

    参考 `pujutils.PUJUtils.__init__` 的口音加载逻辑：先初始化
    `FuzzyRuleDescriptor` 的规则描述符表，再逐个解析 `Accent`。

    Args:
        accent_pb_path: `accents.pb` 文件路径。

    Returns:
        以口音 id 为键、`Accent` 对象为值的字典。
    """
    accent_pb_path = pathlib.Path(accent_pb_path)
    with open(accent_pb_path, 'rb') as f:
        accents_raw = pb.Accents()
        accents_raw.ParseFromString(f.read())
    FuzzyRuleDescriptor.init_from_pb(accents_raw.fuzzy_rule_descriptors)
    accents: dict[str, Accent] = {}
    for a in accents_raw.accents:
        accents[a.id] = Accent.from_pb(a)
    return accents


def load_entries(entries_pb_path: Union[str, pathlib.Path]) -> dict[str, list[Entry]]:
    """
    从 protobuf 数据文件加载字表，并按汉字建立索引。

    Args:
        entries_pb_path: `entries.pb` 文件路径。

    Returns:
        以汉字为键、`Entry` 对象列表为值的字典。同一个字可能对应多个读音，
        故值为列表；繁体与简体形式均会作为键收录。
    """
    entries_pb_path = pathlib.Path(entries_pb_path)
    with open(entries_pb_path, 'rb') as f:
        entries_raw = pb.Entries()
        entries_raw.ParseFromString(f.read())
    han_to_entry: dict[str, list[Entry]] = {}
    for e in entries_raw.entries:
        entry = Entry.from_pb(e)
        han_to_entry.setdefault(e.char_sim, []).append(entry)
        han_to_entry.setdefault(e.char, []).append(entry)
    return han_to_entry


def try_deaccent(char: str, accent_pron: str, accent: Accent,
                 han_to_entry: dict[str, list[Entry]]) -> str:
    """
    尝试将某个带口音的拼音反推为标准音。

    在字表中查找汉字 `char` 的各标准读音，将其应用口音 `accent` 的模糊音
    规则，若得到的口音化读音与输入的 `accent_pron` 一致，则返回该标准读音；
    否则原样返回输入的 `accent_pron`。

    Args:
        char: 汉字（繁体或简体均可）。
        accent_pron: 带口音的拼音（ASCII 白话字形式，如 `lieng7`）。
        accent: 口音对象。
        han_to_entry: `load_entries` 返回的字表索引。

    Returns:
        找到匹配时的标准读音；否则返回原输入的 `accent_pron`。
    """
    input_pron = Pronunciation.from_combination(accent_pron)
    input_comb = input_pron.to_combination()
    for entry in han_to_entry.get(char, []):
        accented = accent.fuzzy_result(entry.pron)
        if accented.to_combination() == input_comb:
            return entry.pron.to_combination()
    return accent_pron


def convert(text: str, source: str = 'puj', target: str = 'puj',
            fuzzy_rule: FuzzyRuleLike = None) -> str:
    """
    将拼音 `text` 从 `source` 方案转换为 `target` 方案。

    `text` 可以是一个拼音单词，也可以是一句由空格与连字符
    （" ", "-", "--", "- ", " -", "-- ", " --" 等）分割的句子；
    非拼音片段（标点等）会原样保留，并在转换结束后恢复原始大小写。

    Args:
        text: 待转换的一个拼音或一句拼音。
        source: 源拼音方案，可选 `'puj'`、`'dp'`。
        target: 目标拼音方案，可选 `'apuj'`、`'puj'`、`'dp'`、
            `'ipa'`、`'xsampa'`。
        fuzzy_rule: 口音（`Accent`）对象，用于应用口音模糊音规则；
            为 None 时不应用口音。

    Returns:
        转换后的拼音字符串。

    Raises:
        ConversionError: 输入无法解析，或指定了不支持的方案。
    """
    if source not in SUPPORTED_SOURCES:
        raise ConversionError(
            f"不支持的源拼音方案：{source!r}，可用：{', '.join(SUPPORTED_SOURCES)}")
    if target not in SUPPORTED_TARGETS:
        raise ConversionError(
            f"不支持的目标拼音方案：{target!r}，可用：{', '.join(SUPPORTED_TARGETS)}")
    word_converter = _make_word_converter(source, target, fuzzy_rule)
    return _convert_sentence(text, word_converter, has_case=_target_has_case(target))


# 为每种 (源, 目标) 组合生成便捷的"源方案 2 目标方案"函数，如：
# puj2apuj、puj2puj、puj2dp、puj2ipa、puj2xsampa、dp2apuj、dp2dp 等。
for _source in SUPPORTED_SOURCES:
    for _target in SUPPORTED_TARGETS:
        _name = f"{_source}2{_target}"

        def _single_word_api(text: str,
                             _parser=_SOURCE_PARSERS[_source],
                             _formatter=_TARGET_FORMATTERS[_target]) -> str:
            """将单个拼音单词从源方案转换为目标方案。"""
            return _formatter(_parser(text))

        _single_word_api.__name__ = _name
        _single_word_api.__qualname__ = _name
        _single_word_api.__doc__ = (
            f"将单个拼音单词从 {_source!r} 方案转换为 {_target!r} 方案。")
        globals()[_name] = _single_word_api
        __all__.append(_name)
