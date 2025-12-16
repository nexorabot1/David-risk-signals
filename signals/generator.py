from signals.indicators import calculate_rsi, calculate_ema

def generate_signal(df):
    close = df["close"]

    rsi = calculate_rsi(close).iloc[-1]
    ema_fast = calculate_ema(close, 9).iloc[-1]
    ema_slow = calculate_ema(close, 21).iloc[-1]

    if rsi < 30 and ema_fast > ema_slow:
        return "BUY"

    if rsi > 70 and ema_fast < ema_slow:
        return "SELL"

    return None
