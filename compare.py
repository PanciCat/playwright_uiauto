@pytest.fixture(scope="session", autouse=True)
def save_cookies(browser, settings):
    if settings["no_backend"] and not os.path.exists(_STATE_PATH):
        raise RuntimeError("无backend鉴权接口，请使用 helpers 手动保存登录态！")
    elif settings["no_backend"]:
        return

    context = None
    page = None
    try:

        context = browser.new_context(
            base_url=settings["base_url"],
            viewport=settings.get("viewport"),
        )
        page = context.new_page()
        context.storage_state(path=str(_STATE_PATH))
    except Exception as e:
        logger.error("[save_cookies] failed: %s", e)
        raise
    finally:
        if page:
            page.close()
        if context:
            context.close()