import argparse
import os
import shutil
from pathlib import Path

import pytest

HERE = Path(__file__).parent.resolve()
INI = HERE / "pytest.ini"


def main():
    ap = argparse.ArgumentParser("Run pytest — 配置由 pytest.ini 统一管理")
    ap.add_argument("-s", action="store_true", help="禁用输出捕获")
    ap.add_argument("-k", default=None, help="按关键字筛选用例")
    ap.add_argument("-m", default=None, help="按 marker 筛选用例")
    ns = ap.parse_args()

    # 固定读取项目根目录的 pytest.ini，不受运行目录影响
    args = [f"-c={INI}"]

    if ns.s:
        args.append("-s")
    if ns.k:
        args += ["-k", ns.k]
    if ns.m:
        args += ["-m", ns.m]

    print("pytest args:", args)
    return pytest.main(args)


if __name__ == "__main__":
    from conftest import _ROOT

    for d in ("allure-results", "videos", "traces"):
        target = _ROOT / d
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)

    main()
    os.system("allure generate allure-results -o allure-report --clean")
