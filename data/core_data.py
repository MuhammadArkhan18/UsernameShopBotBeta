import os
from dotenv import load_dotenv

load_dotenv()

TOKEN       = os.getenv("TOKEN")
id_maingroup= int(os.getenv("id_maingroup"))
bot_id      = int(os.getenv("bot_id"))
db_path     = os.getenv("db_path")
