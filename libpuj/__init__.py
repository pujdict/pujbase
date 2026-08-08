# -*- coding: utf-8 -*-
"""白话字辞典基础库 (pujbase.libpuj)。

提供拼音方案转换、字表/词表/口音数据读取等能力。
拼音方案转换相关的便捷函数见 `libpuj.convert`。
"""

from .convert import (
    ConversionError,
    SUPPORTED_SOURCES,
    SUPPORTED_TARGETS,
    convert,
    puj2apuj,
    puj2dp,
    puj2ipa,
    puj2puj,
    puj2xsampa,
)

__all__ = [
    'convert',
    'puj2apuj',
    'puj2puj',
    'puj2dp',
    'puj2ipa',
    'puj2xsampa',
    'ConversionError',
    'SUPPORTED_SOURCES',
    'SUPPORTED_TARGETS',
]
