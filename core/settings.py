import os, yaml
from pathlib import Path
import configparser

config = configparser.ConfigParser()


def load_settings():
    try:
        config.read("config.ini")
        env = os.getenv("TEST_ENV", config.get("frame", "config"))  # dev/staging/prod
        cfg_file = Path(__file__).parent.parent / "config" / f"{env}.yaml"
        if not cfg_file.exists():
            raise FileNotFoundError(f"Config not found: {cfg_file}")
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data["env"] = env
        print(rf"【当前运行】:{env}环境,配置:{data}")

        return data
    except Exception as e:
        raise e
