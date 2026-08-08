# -*- coding: utf-8 -*-
"""
白话字 (PUJ) 与其他拼音方案之间的转换 API。

将 `pujcommon.Pronunciation` 上零散的转换方法封装为可直接调用的
纯函数，供命令行工具 `puj.py` 及其他脚本复用。

目前仅支持源方案为白话字 (puj)，即 ASCII 形式的白话字
（例如 `peng1`、`iann5`，声调以数字形式出现在拼音之后）。
"""

from __future__ import annotations

from typing import Callable

from .pujcommon import Pronunciation

__all__ = [
    'puj2apuj',
    'puj2puj',
    'puj2dp',
    'puj2ipa',
    'puj2xsampa',
    'convert',
    'SUPPORTED_SOURCES',
    'SUPPORTED_TARGETS',
]

# 目前仅支持的白话字源方案标识。
SUPPORTED_SOURCES = ('puj',)
# 支持的目标方案标识。
SUPPORTED_TARGETS = ('apuj', 'puj', 'dp', 'ipa', 'xsampa')


class ConversionError(ValueError):
    """拼音转换过程中出现的错误，例如无法解析或使用了不支持的方案。"""


def _parse_puj(text: str) -> Pronunciation:
    """
    将 ASCII 白话字（如 `peng1`）解析为 `Pronunciation`。

    与 `Pronunciation.from_combination` 不同，此处对无调号输入给出
    更友好的错误信息，并将缺失的调号视为 0。
    """
    if not text:
        raise ConversionError("输入为空，无法解析白话字拼音。")
    match = Pronunciation.REGEXP_WORD.match(text)
    if not match:
        raise ConversionError(f"无法解析白话字拼音：{text!r}")
    initial = match.group('initial') or ''
    final = match.group('final') or ''
    tone_text = match.group('tone')
    tone = int(tone_text) if tone_text else 0
    return Pronunciation(initial, final, tone)


def puj2apuj(text: str) -> str:
    """白话字(ASCII 形式) 转 白话字(ASCII 形式)。"""
    return _parse_puj(text).to_combination()


def puj2puj(text: str) -> str:
    """白话字(ASCII 形式) 转 白话字(书面形式，含调符)。"""
    return _parse_puj(text).to_written()


def puj2dp(text: str) -> str:
    """白话字(ASCII 形式) 转 潮拼 (DP)。"""
    return _parse_puj(text).to_dp().__str__()


def puj2ipa(text: str) -> str:
    """白话字(ASCII 形式) 转 国际音标 (IPA，书面形式)。"""
    return _parse_puj(text).to_ipa().to_written()


def puj2xsampa(text: str) -> str:
    """白话字(ASCII 形式) 转 X-SAMPA 式国际音标。"""
    return _parse_puj(text).to_ipa().__str__()


# 目标方案名 -> 转换函数。
_TARGET_CONVERTERS: dict[str, Callable[[str], str]] = {
    'apuj': puj2apuj,
    'puj': puj2puj,
    'dp': puj2dp,
    'ipa': puj2ipa,
    'xsampa': puj2xsampa,
}


def convert(text: str, source: str = 'puj', target: str = 'puj') -> str:
    """
    将拼音 `text` 从 `source` 方案转换为 `target` 方案。

    目前仅支持源方案为 `puj`（白话字 ASCII 形式）。

    Args:
        text: 待转换的一个拼音。
        source: 源拼音方案，目前仅支持 `'puj'`。
        target: 目标拼音方案，可选 `'apuj'`、`'puj'`、`'dp'`、
            `'ipa'`、`'xsampa'`。

    Returns:
        转换后的拼音字符串。

    Raises:
        ConversionError: 输入无法解析，或指定了不支持的方案。
    """
    if source not in SUPPORTED_SOURCES:
        raise ConversionError(
            f"不支持的源拼音方案：{source!r}，可用：{', '.join(SUPPORTED_SOURCES)}")
    converter = _TARGET_CONVERTERS.get(target)
    if converter is None:
        raise ConversionError(
            f"不支持的目标拼音方案：{target!r}，可用：{', '.join(SUPPORTED_TARGETS)}")
    return converter(text)
