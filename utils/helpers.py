import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright


def record_action(url):
    os.system(
        rf"playwright codegen --browser chromium  --load-storage ../state.json --output record.py --target ../.venv/Scripts/Python {url}")


async def save_cookies(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            # user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari / 537.36")
            user_agent="Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'")
        page = await ctx.new_page()
        await page.goto(url)

        print("请在浏览器中手动登录，登录完成后回到终端按 Enter")
        input()

        # 保存完整状态（含 HttpOnly cookie）
        await ctx.storage_state(path="../state.json")
        print("已保存到 state.json")
        await browser.close()


# 硬编码 参考用
if __name__ == '__main__':
    _ROOT = Path(__file__).parent.parent
    _STATE_PATH = _ROOT / "state.json"
    url = "http://vue.ruoyi.vip/index"
    # if not os.path.exists(_STATE_PATH):
    #     Path(_STATE_PATH).touch()
    asyncio.run(save_cookies("http://vue.ruoyi.vip/index"))