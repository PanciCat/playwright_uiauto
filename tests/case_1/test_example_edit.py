from playwright.sync_api import expect

from core.allure_tools import step, feature, story
from pages.base_page import BasePage
from utils.util import genVariable


@feature("一级用例")
@story("用户故事")
@step("新增用户")
def test_user_index(page_auth, settings):
    """验证新增用户的完整操作流程。"""
    base_page = BasePage(page_auth, settings)
    page = base_page.page
    sn = genVariable().uuid_8()
    phone = genVariable().generate_phone()

    with step("导航到用户管理页"):
        base_page.goto_with_expect(
            f"{settings['base_url']}/system/user",
            '//*[@id="app"]/div[1]/div[2]/section/div/div[1]/div/div[3]/div/div[1]/div[1]',
            "增",
        )

    with step("点击新增用户按钮"):
        base_page.click(
            '//*[@id="app"]/div[1]/div[2]/section/div/div[1]/div/div[3]/div/div[1]/div[1]/button',
            "新增",
        )
        expect(page.get_by_role("dialog")).to_be_visible(timeout=5000)
        dialog = page.get_by_role("dialog")

    with step("输入用户名称"):
        dialog.get_by_placeholder("请输入用户名称").fill(rf"{sn}")

    with step("输入用户昵称"):
        dialog.get_by_placeholder("请输入用户昵称").fill(rf"{sn}")

    with step("提交表单"):
        dialog.locator(".el-button--primary").filter(has_text="确").click()

    with step("失败example"):
        dialog.locator(".el-s").filter(has_text="s").click()

    with step("验证结果"):
        page.get_by_text(rf"{sn}")
