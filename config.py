import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

TIMEFRAME = "5M"
MARTINGALE_LEVELS = 3

DISCLAIMER = (
    "⚠️ Market analysis signal only. "
    "Not financial advice. Trading involves risk."
)
