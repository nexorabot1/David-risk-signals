from datetime import datetime, timedelta

def format_signal(asset, direction):
    now = datetime.now()
    entry_time = now.strftime("%H:%M")

    levels = [
        (now + timedelta(minutes=5 * i)).strftime("%H:%M")
        for i in range(1, 4)
    ]

    message = f"""
{asset}
🕘 Expiration: 5M
⏺ Entry at {entry_time}
{"🟩 BUY" if direction == "BUY" else "🟥 SELL"}

🔼 Martingale levels
1️⃣ {levels[0]}
2️⃣ {levels[1]}
3️⃣ {levels[2]}

⚠️ Market analysis signal only
""".strip()

    return message
