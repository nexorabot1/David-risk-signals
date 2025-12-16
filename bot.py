import os
import asyncio
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

CRYPTO_PAIRS = {
    "BTCUSDT": "BTC/USDT",
    "ETHUSDT": "ETH/USDT",
    "SOLUSDT": "SOL/USDT"
}

BINANCE_URL = "https://api.binance.com/api/v3/klines"

DISCLAIMER = "⚠️ Market analysis signal only. Not financial advice."

# ================= INDICATORS =================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

# ================= MARKET DATA =================

def get_candles(symbol):
    params = {"symbol": symbol, "interval": "5m", "limit": 100}
    r = requests.get(BINANCE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","trades","tb","tq","ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

# ================= SIGNAL LOGIC =================

def generate_signal(df):
    close = df["close"]
    r = rsi(close).iloc[-1]
    e9 = ema(close, 9).iloc[-1]
    e21 = ema(close, 21).iloc[-1]

    if r < 30 and e9 > e21:
        return "BUY"
    if r > 70 and e9 < e21:
        return "SELL"
    return None

# ================= FORMAT MESSAGE =================

def format_signal(asset, direction):
    now = datetime.now()
    entry = now.strftime("%H:%M")
    levels = [(now + timedelta(minutes=5*i)).strftime("%H:%M") for i in range(1,4)]

    return f"""
{asset}
🕘 Expiration: 5M
⏺ Entry at {entry}
{"🟩 BUY" if direction == "BUY" else "🟥 SELL"}

🔼 Martingale levels
1️⃣ {levels[0]}
2️⃣ {levels[1]}
3️⃣ {levels[2]}

{DISCLAIMER}
""".strip()

# ================= TELEGRAM =================

subscribers = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text(
        "📊 David Risk Signals Bot\n\nSignals will be sent automatically."
    )

async def signal_loop(app):
    while True:
        for symbol, display in CRYPTO_PAIRS.items():
            try:
                df = get_candles(symbol)
                signal = generate_signal(df)
                if signal:
                    msg = format_signal(display, signal)
                    for chat_id in subscribers:
                        await app.bot.send_message(chat_id, msg)
            except Exception:
                pass
        await asyncio.sleep(300)  # 5 minutes

async def on_startup(app):
    asyncio.create_task(signal_loop(app))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
