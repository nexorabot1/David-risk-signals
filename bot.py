import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN, DISCLAIMER
from data.market_data import get_crypto_candles
from signals.generator import generate_signal
from utils.formatter import format_signal

# Track users who started the bot
subscribers = set()

# Crypto pairs to scan (can be moved to config later)
CRYPTO_PAIRS = {
    "BTCUSDT": "BTC/USDT",
    "ETHUSDT": "ETH/USDT",
    "SOLUSDT": "SOL/USDT",
}

# ================= TELEGRAM COMMAND =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)

    await update.message.reply_text(
        "📊 David Risk Signals Bot\n\n"
        "You are now subscribed to 5-minute crypto signals.\n\n"
        + DISCLAIMER
    )

# ================= SIGNAL WORKER =================

async def signal_worker(app):
    while True:
        for symbol, display in CRYPTO_PAIRS.items():
            try:
                df = get_crypto_candles(symbol)
                signal = generate_signal(df)

                if signal:
                    message = format_signal(display, signal)
                    for chat_id in subscribers:
                        await app.bot.send_message(chat_id, message)

            except Exception as e:
                # Silent fail to keep worker alive
                pass

        await asyncio.sleep(300)  # 5 minutes

# ================= APP STARTUP =================

async def on_startup(app):
    asyncio.create_task(signal_worker(app))

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
