import os
from dotenv import load_dotenv

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Variable '{name}' is doesn't included in .env file")

    return value

TOKEN       = require_env("TOKEN")
id_maingroup= int(require_env("id_maingroup"))
bot_id      = int(require_env("bot_id"))
db_path     = require_env("db_path")
