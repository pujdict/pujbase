#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""潮汕方言拼音方案转换命令行工具。

示例：
    python puj.py --convert puj2dp --text peng1
    python puj.py --convert puj2ipa --text tshout3
    python puj.py -c puj2xsampa -t iann5
    python puj.py -c puj2apuj -t eu1 --accent ChaoZhou_FuCheng --accent-data dist/accents.pb
"""

from __future__ import annotations

import sys

import click

from libpuj import (
    SUPPORTED_SOURCES,
    SUPPORTED_TARGETS,
    ConversionError,
    convert,
    load_accents,
)

# 允许通过 -h 打印帮助信息。
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--convert', '-c',
    'convert_spec',
    type=str,
    default='puj2puj',
    show_default=True,
    help=(
        '转换类型，格式为 <源方案>2<目标方案>，如 puj2dp 表示白话字转潮拼。'
        f'源方案目前支持 {"、".join(SUPPORTED_SOURCES)}；'
        f'目标方案支持 {"、".join(SUPPORTED_TARGETS)}。'
    ),
)
@click.option(
    '--text', '-t',
    type=str,
    default=None,
    help='需要转换的拼音（源拼音使用 ASCII 形式，如 peng1；'
         '也支持由空格与连字符分割的整句话）。',
)
@click.option(
    '--accent', '-a',
    type=str,
    default=None,
    help='口音 id，指定后按该口音的模糊音规则转换（需配合 --accent-data）。',
)
@click.option(
    '--accent-data',
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help='口音数据文件（accents.pb）的路径，用于加载口音。',
)
def main(convert_spec: str, text: str, accent: str, accent_data: str) -> None:
    """潮汕方言白话字工具。"""
    if not text:
        raise click.UsageError("请通过 --text 指定需要转换的拼音。")

    # 解析 <源方案>2<目标方案>，例如 puj2dp -> (puj, dp)。
    parts = convert_spec.split('2')
    if len(parts) != 2 or not all(parts):
        raise click.BadParameter(
            f"无法解析转换类型 {convert_spec!r}，"
            "格式应为 <源方案>2<目标方案>，如 puj2dp。",
            param_hint='--convert',
        )
    source, target = parts

    if source not in SUPPORTED_SOURCES:
        raise click.BadParameter(
            f"不支持的源拼音方案：{source!r}，可用：{', '.join(SUPPORTED_SOURCES)}。",
            param_hint='--convert',
        )
    if target not in SUPPORTED_TARGETS:
        raise click.BadParameter(
            f"不支持的目标拼音方案：{target!r}，可用：{', '.join(SUPPORTED_TARGETS)}。",
            param_hint='--convert',
        )

    # 口音处理：给定 --accent 时必须加载口音数据。
    fuzzy_rule = None
    if accent is not None:
        if accent_data is None:
            raise click.UsageError(
                "指定 --accent 时必须同时通过 --accent-data 指定口音数据文件。")
        try:
            accents = load_accents(accent_data)
        except Exception as exc:
            raise click.ClickException(f"加载口音数据失败：{exc}")
        if accent not in accents:
            available = "、".join(sorted(accents))
            raise click.BadParameter(
                f"未知口音：{accent!r}。可用口音：{available}。",
                param_hint='--accent',
            )
        fuzzy_rule = accents[accent]

    try:
        result = convert(text, source=source, target=target, fuzzy_rule=fuzzy_rule)
    except ConversionError as exc:
        raise click.ClickException(str(exc))

    click.echo(result)


if __name__ == '__main__':
    main(sys.argv[1:])
