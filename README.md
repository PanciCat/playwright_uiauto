# Playwright UiAuto for Test 自动化测试框架
# 使用claude code结合手搓生成，主要用于解决工作里跑ui自动化经常验证码识别失败的问题

基于 **Playwright + Pytest + Allure** 的 Web UI 自动化测试项目，采用 Page Object Model（POM）设计模式。


---


## 目录结构

```
pw_demo/
├── config/                    # 环境配置
│   ├── dev.yaml               # 开发环境
│   └── prod.yaml              # 生产环境
├── core/                      # 核心模块
│   ├── settings.py            # 配置加载
│   └── allure_tools.py        # Allure 报告工具
├── pages/                     # 页面对象层（POM）
│   ├── base_page.py           # 基础页面类
│   └── login_page.py          # 登录页面类
├── tests/                     # 测试用例
│   └── case_1/
│       └── test_example_edit.py
├── utils/                     # 工具模块
│   ├── util.py                # 数据生成 & 加密
│   ├── mock_data.py           # Mock 数据模板
│   ├── helpers.py             # 手动保存 storage 工具
│   └── record.py              # 录制脚本
├── allure-results/            # 测试结果数据（自动生成）
├── allure-report/             # Allure HTML 报告（自动生成）
├── traces/                    # Playwright trace 文件（自动生成）
├── videos/                    # 测试录制视频（自动生成）
├── state.json                 # 浏览器会话状态（自动生成）
├── conftest.py                # Pytest Fixtures & Hooks
├── config.ini                 # 框架默认环境配置
├── pytest.ini                 # Pytest 配置
├── main.py                    # 测试运行入口
└── requirements.txt           # 依赖包
```

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 测试框架 | Pytest | 8.1.1 |
| 浏览器自动化 | Playwright | 1.55.0 |
| 报告系统 | Allure | 2.13.5 |
| 配置管理 | PyYAML + configparser | 6.0.1 |
| 数据生成 | Faker | 24.4.0 |
| 密码加密 | pycryptodome | 3.20.0 |
| HTTP 请求 | requests | 2.31.0 |
| 设计模式 | Page Object Model | — |

---

## 架构说明

### 分层设计

```
┌────────────────────────────────────┐
│           测试用例层（tests/）       │  编写业务测试逻辑
├────────────────────────────────────┤
│          页面对象层（pages/）        │  封装页面操作
├────────────────────────────────────┤
│      核心基础层（core/ + utils/）    │  配置、工具、Mock 数据
├────────────────────────────────────┤
│         Playwright / Pytest        │  底层驱动
└────────────────────────────────────┘
```

### 核心模块职责

**`conftest.py`** — Fixtures 中枢

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `settings` | session | 加载环境配置，支持 `--env` CLI 参数切换 |
| `save_cookies` | session, autouse | 根据 `no_backend` 决定自动或手动获取 storage |
| `page_auth` | function | 加载 `state.json` 恢复会话，供测试直接使用已登录状态 |
| `tool_get_token` | session | 单独调用后端 API 获取 token（不依赖浏览器） |

**`core/settings.py`** — 三层配置优先级

```
CLI 参数 --env  >  环境变量 TEST_ENV  >  config.ini 默认值
```

**`core/allure_tools.py`** — 报告工具

```python
@step("步骤名")           # 作装饰器
with step("操作描述"):    # 作上下文管理器
    ...

attach_text / attach_png / attach_video / attach_json
```

**`pages/base_page.py`** — 基础页面封装

```python
goto(path)                          # 导航
click(selector, text)               # 点击
fill(selector, text)                # 填充输入框
menuitem_click_byRole(path)         # 级联菜单精确点击
menuitem_click_byRole_fuzzy(path)   # 级联菜单模糊点击
```

**`utils/util.py`** — 测试数据

```python
genVariable.generate_name()    # 随机中文姓名
genVariable.generate_phone()   # 随机手机号
genVariable.uuid_8()           # 8 位 UUID
encrypt_hex(word)              # AES-ECB 加密（密码加密）
```

---

## 鉴权 Storage 获取方式

框架通过 `state.json` 持久化浏览器的登录状态（cookies + localStorage）。根据被测系统是否提供可直连的后端鉴权接口，提供以下两种方式。

---

### 方式一：自动获取（推荐用于 CI / 有可达后端接口）

**适用场景：** 后端鉴权接口可直接访问，且验证码可通过 mock 绕过。

**配置方法：** 在对应环境的 yaml 文件中，将 `no_backend` 设置为 `false`（或删除此项）：

```yaml
# config/prod.yaml
no_backend: false   # 开启自动鉴权
login_url: "http://<YOUR_HOST>:<PORT>/prod-api/auth/backendLogin"
username: "<your-username>"
password: "<your-password>"
```

**执行流程：**

```
Session 启动（save_cookies fixture）
    │
    ├─ 1. API 登录（requests）
    │      POST login_url → 获取真实 token
    │
    ├─ 2. 注册 Mock 路由（拦截 3 个接口）
    │      ├─ **/prod-api/auth/login         → 返回含真实 token 的 mock 响应
    │      ├─ **/prod-api/ctuav/version/info → 返回版本信息
    │      └─ **/prod-api/ctuav/user/getInfo → 返回用户信息
    │
    ├─ 3. UI 登录（Playwright）
    │      填写用户名 / 密码 / 验证码（固定值"1"，由 mock 通过）→ 点击登录
    │
    └─ 4. 保存 state.json（context.storage_state）

Function 测试
    └─ 加载 state.json → 恢复已登录会话 → 执行测试
```

**优点：** 每次运行自动刷新登录态，无需手动干预，适合 CI 流水线。

---

### 方式二：手动获取（适用于无后端接口 / 含验证码场景）

**适用场景：** 后端鉴权接口不可直连（如需要 VPN / 跳板机），或验证码无法 mock 绕过。

**配置方法：** 在 yaml 文件中将 `no_backend` 设置为 `true`：

```yaml
# config/dev.yaml
no_backend: true   # 跳过自动鉴权，使用手动保存的 state.json
base_url: "http://<DEV_HOST>/"
```

**两种手动保存 state.json 的方法：**

#### 方法 A：使用框架内置的 helpers 工具

```python
# utils/helpers.py
from utils.helpers import save_cookies
import asyncio

asyncio.run(save_cookies("http://<YOUR_HOST>:<PORT>/"))
```

或直接运行：

```bash
python utils/helpers.py
```

脚本会打开浏览器窗口，等待你手动完成登录操作，登录成功后自动将 cookies 和 localStorage 保存为 `state.json`。

#### 方法 B：使用 Playwright Codegen（推荐，操作更直观）

```bash
playwright codegen --save-storage=state.json http://<YOUR_HOST>:<PORT>/
```

1. 浏览器窗口打开后，手动输入账号密码和验证码完成登录
2. 登录成功跳转首页后，关闭录制窗口
3. `state.json` 自动保存到项目根目录

**注意事项：**
- `state.json` 有时效性，登录态过期后需重新执行上述步骤
- 框架检测到 `no_backend: true` 且 `state.json` 不存在时，会抛出 `RuntimeError` 提醒手动保存

---

### 两种方式对比

| 对比项 | 方式一（自动） | 方式二（手动） |
|--------|---------------|---------------|
| `no_backend` 设置 | `false` | `true` |
| 前提条件 | 后端鉴权接口可直连 | 无需后端接口直连 |
| 验证码处理 | 通过 mock 路由绕过 | 手动输入 |
| 适用场景 | CI 流水线、自动化运行 | 本地调试、含验证码系统 |
| state.json 刷新 | 每次运行自动刷新 | 过期后需手动重新保存 |

---

## 环境配置

### 配置文件说明

```yaml
# config/dev.yaml 示例
base_url: "http://<DEV_HOST>/"
no_backend: true                    # true=手动 storage | false=自动鉴权
browser: "chromium"                 # chromium | firefox | webkit
headless: false                     # true 为无头模式（CI 推荐）
video: "on"                         # off | on | retain-on-failure
tracing: true                       # 开启 trace 追踪
slow_mo: 0                          # 操作间隔（毫秒），调试时可设为 500
viewport: { width: 1920, height: 1080 }
login_url: "http://<YOUR_HOST>:<PORT>/prod-api/auth/backendLogin"
username: "<your-username>"
password: "<your-password>"
```

### 切换环境

修改 `config.ini` 中的默认环境：

```ini
[frame]
config = dev    # 修改为 prod 切换生产环境
```

或在运行时指定（优先级最高）：

```bash
pytest --env prod
python main.py --env prod
```

---

## 环境准备

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器

```bash
playwright install chromium
# 或安装全部浏览器
playwright install
```

### 3. 安装 Allure 命令行工具

**Windows（Scoop）：**
```bash
scoop install allure
```

**macOS / Linux：**
```bash
brew install allure
```

> Allure 需要 Java 8+ 环境支持。

---

## 运行指南

### 方式一：使用 main.py（推荐）

```bash
python main.py
```

`main.py` 会自动：
1. 清理历史结果（`allure-results`、`videos`、`traces`、`state.json`）
2. 运行所有测试用例
3. 生成并打开 Allure 报告

支持传参：

```bash
python main.py -s              # 显示 print 输出
python main.py -k shelter      # 按关键字筛选用例
python main.py -m smoke        # 只运行冒烟用例
python main.py -m regression   # 只运行回归用例
```

### 方式二：直接使用 pytest

```bash
# 运行所有测试
pytest

# 指定环境
pytest --env prod

# 按关键字筛选
pytest -k "test_example"

# 按 marker 筛选
pytest -m smoke

# 生成并查看 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

### 生成 Allure 报告

```bash
# 生成静态报告
allure generate allure-results -o allure-report --clean

# 实时服务（自动打开浏览器）
allure serve allure-results
```

---

## 编写测试用例

### 基本结构

```python
from core.allure_tools import step, feature, story, title

@feature("功能模块名")
class TestXxx:

    @story("子功能")
    @title("用例标题")
    def test_xxx(self, page_auth, settings):
        # page_auth: 已登录的 Playwright 页面对象
        # settings:  当前环境配置字典

        with step("步骤一：导航到目标页面"):
            page_auth.goto(settings["base_url"] + "target-path")

        with step("步骤二：执行操作"):
            page_auth.click("button", "新增")

        with step("步骤三：验证结果"):
            assert page_auth.locator(".success-msg").is_visible()
```

### 使用 Page Object

```python
from pages.base_page import BasePage

class TestWithPOM:
    def test_example(self, page_auth, settings):
        page = BasePage(page_auth, settings)

        page.goto("/shelter")
        page.click("button", "新增")
        page.menuitem_click_byRole(["组织名", "子节点"])
        page.fill("input[placeholder='请输入序列号']", "SN-001")
```

### 使用测试数据工具

```python
from utils.util import genVariable

name  = genVariable.generate_name()    # 随机中文姓名
phone = genVariable.generate_phone()   # 随机手机号
uid   = genVariable.uuid_8()           # 随机 8 位 ID
```

### Marker 标签

| Marker | 说明 |
|--------|------|
| `smoke` | 冒烟用例（快速验证核心流程） |
| `regression` | 回归用例（全量功能验证） |

---

## 调试技巧

| 场景 | 配置方法 |
|------|---------|
| 查看浏览器操作 | `headless: false` |
| 放慢操作速度 | `slow_mo: 500`（毫秒） |
| 查看网络 & 截图 | `tracing: true`，结果在 `traces/` 目录 |
| 查看视频录像 | `video: on`，结果在 `videos/` 目录 |
| 回放 Trace | `playwright show-trace traces/trace.zip` |
| 打印调试信息 | `pytest -s` 或 `python main.py -s` |

---

## 常见问题

**Q: 运行报错 `No module named 'playwright'`**

```bash
pip install playwright
playwright install chromium
```

**Q: 报错 `无backend鉴权接口，请使用 helpers 手动保存登录态！`**

当前配置了 `no_backend: true` 但 `state.json` 不存在。参考 [鉴权方式二](#方式二手动获取适用于无后端接口--含验证码场景) 手动保存登录态：

```bash
playwright codegen --save-storage=state.json http://<YOUR_HOST>:<PORT>/
```

**Q: 登录失败 / state.json 过期**

删除 `state.json` 后重新运行，框架将自动重新登录（自动模式）或提示手动保存（手动模式）：

```bash
rm state.json
python main.py
```

**Q: Allure 报告无法打开**

确认已安装 Allure CLI 且 Java 环境可用：

```bash
allure --version
java --version
```

**Q: 切换测试环境**

修改 `config.ini`：

```ini
[frame]
config = prod
```

或运行时指定：

```bash
pytest --env prod
```
