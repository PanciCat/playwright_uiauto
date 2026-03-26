import copy
import json
import logging
import os
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright, expect

from core.allure_tools import attach_png, attach_text, attach_video, timestamp
from core.settings import load_settings
from utils.mock_data import (
    LOGIN_MOCK_BODY_TEMPLATE,
    VERSION_INFO_MOCK_BODY,
    USER_INFO_MOCK_BODY,
)
from utils.util import encrypt_hex

logger = logging.getLogger(__name__)

# 项目根目录（conftest.py 所在目录）
_ROOT = Path(__file__).parent
_STATE_PATH = _ROOT / "state.json"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _make_login_body(token: str) -> str:
    body = copy.copy(LOGIN_MOCK_BODY_TEMPLATE)
    body["token"] = str(token)
    return json.dumps(body)


def _register_mock_routes(page, token: str) -> None:
    """为 page 注册 login / version / userInfo 三条 mock 路由。"""
    page.route(
        "**/prod-api/auth/login",
        lambda route: route.fulfill(
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            body=_make_login_body(token),
        ),
    )
    page.route(
        "**/prod-api/ctuav/version/info",
        lambda route: route.fulfill(
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            body=json.dumps(VERSION_INFO_MOCK_BODY),
        ),
    )
    page.route(
        "**/prod-api/ctuav/user/getInfo",
        lambda route: route.fulfill(
            status=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            body=json.dumps(USER_INFO_MOCK_BODY),
        ),
    )


# ---------------------------------------------------------------------------
# session 级 fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def settings(pytestconfig):
    cli_env = pytestconfig.getoption("--env")
    if cli_env:
        os.environ["TEST_ENV"] = cli_env
    return load_settings()


@pytest.fixture(scope="session")
def pw():
    p = sync_playwright().start()
    yield p
    p.stop()




@pytest.fixture(scope="session")
def browser(pw, settings):
    browser_type = getattr(pw, settings.get("browser", "chromium"))
    # 清理文件
    if os.path.exists(_STATE_PATH) and not settings["no_backend"]:
        os.remove(_STATE_PATH)
    b = browser_type.launch(
        headless=settings.get("headless", True),
        slow_mo=settings.get("slow_mo", 0),
    )
    yield b
    b.close()


@pytest.fixture(scope="session", autouse=True)
def save_cookies(browser, settings):
    """API 登录取 token，再通过浏览器走 mock 登录流程，把 storage state 保存到 state.json。"""
    if settings["no_backend"] and not os.path.exists(_STATE_PATH):
        raise RuntimeError("无backend鉴权接口，请使用 helpers 手动保存登录态！")
    elif settings["no_backend"]:
        return

    try:
        res = requests.post(
            url=settings["login_url"],
            headers={
                "user-agent": (
                    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) "
                    "AppleWebKit/604.1.34 (KHTML, like Gecko) "
                    "Version/11.0 Mobile/15A5341f Safari/604.1"
                )
            },
            json={
                "username": settings["username"],
                "password": encrypt_hex(settings["password"]),
            },
        )
        res.raise_for_status()
        token = res.json()["token"]

        context = browser.new_context(
            base_url=settings["base_url"],
            viewport=settings.get("viewport"),
        )
        page = context.new_page()
        _register_mock_routes(page, token)

        page.goto(settings["base_url"], wait_until="domcontentloaded", timeout=150000)

        username_loc = page.locator('//*[@id="app"]/div[1]/form/div/div[1]/div/div/input')
        expect(username_loc).to_be_visible(timeout=8000)
        username_loc.fill(settings["username"])

        pwd_loc = page.locator('//*[@id="app"]/div[1]/form/div/div[2]/div/div/input')
        expect(pwd_loc).to_be_visible(timeout=8000)
        pwd_loc.fill(settings["password"])

        page.fill('//*[@id="app"]/div[1]/form/div/div[3]/div/div[1]/input', "1")

        btn = page.locator('//*[@id="app"]/div[1]/form/div/div[4]/div/button', has_text="登")
        expect(btn).to_be_visible(timeout=8000)
        btn.click()

        # 等待前端完成跳转后再保存 state，避免 time.sleep 硬等
        page.wait_for_url(f"{settings['base_url']}**", timeout=15000)
        page.wait_for_load_state("load", timeout=150000)

        # 修复 state.json domain 问题：存储前先刷新一次，确保 cookies domain 正确
        page.reload()
        page.wait_for_load_state("load", timeout=100000)

        context.storage_state(path=str(_STATE_PATH))
        logger.info("[save_cookies] storage state saved to %s", _STATE_PATH)

    except Exception as e:
        logger.error("[save_cookies] failed: %s", e)
        raise


@pytest.fixture(scope="session")
def tool_get_token(settings):
    res = requests.post(
        url=settings["login_url"],
        headers={
            "user-agent": (
                "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) "
                "AppleWebKit/604.1.34 (KHTML, like Gecko) "
                "Version/11.0 Mobile/15A5341f Safari/604.1"
            )
        },
        json={
            "username": settings["username"],
            "password": encrypt_hex(settings["password"]),
        },
    )
    res.raise_for_status()
    return res.json()["token"]


# ---------------------------------------------------------------------------
# function 级 fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def pw_context(browser, settings):

    video_cfg = settings.get("video", "off")
    ctx_kwargs: dict = {
        "base_url": settings["base_url"],
        "viewport": settings.get("viewport"),
    }
    if video_cfg in ("on", "retain-on-failure"):
        ctx_kwargs["record_video_dir"] = str(_ROOT / "videos")

    ctx = browser.new_context(**ctx_kwargs)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(pw_context):
    p = pw_context.new_page()
    yield p
    p.close()


@pytest.fixture(scope="function")
def tool_login_mock(tool_get_token, page):
    """为 page 注册 mock 路由，供需要独立 mock 登录的测试使用。"""
    if tool_get_token is None:
        raise RuntimeError("tool_get_token 为空，获取 token 失败")
    _register_mock_routes(page, tool_get_token)
    setattr(page, "_login_mock_ready", True)


@pytest.fixture(scope="function")
def pw_context_auth(browser, settings, request):
    if_tracing = settings.get("tracing")
    video_cfg = settings.get("video", "off")
    if not _STATE_PATH.exists():
        pytest.fail("save_cookies 未能生成 state.json，登录失败")
    ctx_kwargs: dict = {
        "base_url": settings["base_url"],
        "viewport": settings.get("viewport"),
        "storage_state": str(_STATE_PATH),
    }
    if video_cfg in ("on", "retain-on-failure"):
        ctx_kwargs["record_video_dir"] = str(_ROOT / "videos")

    ctx = browser.new_context(**ctx_kwargs)
    request.node._pw_context = ctx
    if if_tracing:
        ctx.tracing.start(screenshots=True, snapshots=True)
    yield ctx

    if if_tracing:
        failed = getattr(request.node, "_pw_failed", False)
        trace_path = str(_ROOT / "traces" / "trace.zip") if failed else None
        ctx.tracing.stop(path=trace_path)

    ctx.close()


@pytest.fixture(scope="function")
def page_auth(pw_context_auth):
    p = pw_context_auth.new_page()
    yield p
    p.close()


# ---------------------------------------------------------------------------
# pytest 钩子
# ---------------------------------------------------------------------------

@pytest.hookimpl
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=None, help="dev/staging/prod")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时挂载截图、视频、URL 到 Allure。"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" or not rep.failed:
        return

    page = item.funcargs.get("page") or item.funcargs.get("page_auth")
    if page:
        try:
            item._pw_failed = True
            png = page.screenshot(full_page=True)
            attach_png(f"失败截图_{timestamp()}", png)
            attach_text("失败URL", page.url)
        except Exception as e:
            attach_text("截图失败", str(e))

    # 视频附件（若 pw_context 开启了 record_video_dir）
    ctx = item.funcargs.get("pw_context") or item.funcargs.get("pw_context_auth")
    if ctx:
        try:
            for v in (_ROOT / "videos").glob("**/*.webm"):
                attach_video(f"视频_{v.name}", str(v))
        except Exception as e:
            attach_text("视频附件失败", str(e))
