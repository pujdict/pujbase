# -*- coding: utf-8 -*-
"""白话字辞典基础库 (pujbase.libpuj)。

提供拼音方案转换、字表/词表/口音数据读取等能力。
拼音方案转换相关的便捷函数见 `libpuj.convert`。
"""

from . import convert as _convert_mod

# 重新导出 convert 中公开的所有转换函数（puj2dp、dp2ipa、convert 等）。
__all__ = list(_convert_mod.__all__)
globals().update({name: getattr(_convert_mod, name) for name in _convert_mod.__all__})
