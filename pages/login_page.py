# -*- coding: utf-8 -*-
# @Author   : pancicat
# @Time     : 2025/01/18
# @File     : login_page.py
# @Desc     : 登录页面 Page Object

from playwright.sync_api import expect

from core.allure_tools import step
from .base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page, settings):
        super().__init__(page, settings)

    def login(
        self,
        loginPath: str,
        usernamePath: str,
        passwordPath: str,
        verifyPath: str,
        expectUrl: str = None,
    ):
        """执行登录操作。

        :param loginPath:    登录按钮的 XPath
        :param usernamePath: 用户名输入框的 XPath
        :param passwordPath: 密码输入框的 XPath
        :param verifyPath:   验证码输入框的 XPath
        :param expectUrl:    登录成功后期望跳转到的 URL（可选）
        """
        self.goto()
        self.fill(usernamePath, self.settings["username"])
        self.fill(passwordPath, self.settings["password"])
        self.fill(verifyPath, "1")
        self.click(loginPath, "登")

        # 等待前端路由跳转，避免 time.sleep 硬等
        base = self.settings["base_url"]
        self.page.wait_for_url(f"{base}**", timeout=15000)
        self.page.wait_for_load_state("networkidle", timeout=15000)

        if expectUrl is not None:
            expect(self.page).to_have_url(expectUrl, timeout=10000)
