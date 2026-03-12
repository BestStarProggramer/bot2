import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
# TOKEN = os.getenv("BOT_TOKEN")
TOKEN = os.getenv("DEV_TOKEN")

ADMINS = {int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()}

DB_PATH = os.getenv("DB_NAME", "students.db")

K_FACTOR = float(os.getenv("K_FACTOR", "1.0"))
RECENT_QUEUE_LIMIT = int(os.getenv("RECENT_QUEUE_LIMIT", "5"))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
