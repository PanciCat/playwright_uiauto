# -*- coding: utf-8 -*-
# @Author   : pancicat
# @Time     : 2025/01/18
# @File     : base_page.py
# @Desc     : Page Object 基类，封装常用页面操作

from enum import Enum
from playwright.sync_api import expect, Locator
from core.allure_tools import *


class BasePage:
    def __init__(self, page, settings):
        self.page = page
        self.settings = settings

    def goto(self, path: str = None):
        if path is None:
            path = self.settings["base_url"]
        self.page.goto(path, wait_until="domcontentloaded")

    def goto_with_expect(self, url: str, locator_selector: str, has_text: str):
        """导航到 url，并断言指定 locator 可见。

        参数名由 locator 改为 locator_selector 以避免与局部 Locator 变量遮蔽。
        """
        self.page.goto(url, wait_until="domcontentloaded")
        element = self.page.locator(locator_selector, has_text=has_text)
        expect(element).to_be_visible(timeout=8000)

    def click(self, locator_selector: str, has_text: str):
        element = self.page.locator(locator_selector, has_text=has_text)
        expect(element).to_be_visible(timeout=8000)
        element.click()

    def fill(self, locator_selector: str, fill_text: str, has_text: str = None):
        element = self.page.locator(locator_selector, has_text=has_text)
        expect(element).to_be_visible(timeout=8000)
        element.fill(fill_text)

    def clear(self, locator_selector: str):
        element = self.page.locator(locator_selector)
        expect(element).to_be_visible(timeout=8000)
        element.clear()

    def menuitem_click_byRole(self, path: list):
        """精确按级联菜单路径逐层点击。

        :param path: 各层节点 title 列表，例如
                     ["1", "2", "3"]
        """
        for name in path:
            menu = self.page.locator(".ant-cascader-menus-content:visible").last
            menu.locator(f'li[role="menuitem"][title="{name}"]:visible').first.click()


    def menuitem_click_byRole_fuzzy(self, path: list):
        """模糊按级联菜单路径逐层点击。

        :param path: 各层节点 title 列表，例如
                     ["1", "2", "3"]
        """
        for name in path:
            menu = self.page.locator(".ant-cascader-menus-content:visible").last
            menu.locator(f'li[role="menuitem"][title*="{name}"]:visible').first.click()
