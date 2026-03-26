# -*- coding: utf-8 -*-
# @Author   : pancicat
# @Time     : 2025/01/18
# @File     : allure_tools.py
# @Desc     : Allure 工具封装（step 装饰器 / 上下文管理器、附件工具等）

import functools
import logging
from datetime import datetime
from typing import Callable

import allure

logger = logging.getLogger(__name__)


class step:
    """
    支持两种用法：

      @step("标题")          → 装饰器，包裹整个函数
      with step("标题"):     → 上下文管理器，包裹代码块

    示例::

        @step("提交表单")
        def submit(page):
            ...

        with step("填写用户名"):
            page.fill("#user", "admin")
    """

    def __init__(self, title: str):
        self.title = title
        self._ctx = None

    # ── 装饰器用法 ──────────────────────────────────────────────────────────
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with allure.step(self.title or func.__name__):
                return func(*args, **kwargs)

        return inner

    # ── 上下文管理器用法 ────────────────────────────────────────────────────
    def __enter__(self):
        self._ctx = allure.step(self.title)
        self._ctx.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._ctx.__exit__(exc_type, exc_val, exc_tb)


# ---------------------------------------------------------------------------
# Allure 标注快捷方式（测试文件无需直接 import allure）
# ---------------------------------------------------------------------------

feature = allure.feature
story = allure.story
title = allure.title
description = allure.description
severity = allure.severity
tag = allure.tag


# ---------------------------------------------------------------------------
# 附件工具
# ---------------------------------------------------------------------------

def attach_text(name: str, content: str) -> None:
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_png(name: str, binary: bytes) -> None:
    allure.attach(binary, name=name, attachment_type=allure.attachment_type.PNG)


def attach_video(name: str, path: str) -> None:
    try:
        with open(path, "rb") as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.MP4)
    except OSError as e:
        logger.warning("attach_video: 无法读取视频文件 %s: %s", path, e)


def attach_json(name: str, content: str) -> None:
    allure.attach(content, name=name, attachment_type=allure.attachment_type.JSON)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
