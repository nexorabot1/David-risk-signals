import requests
import pandas as pd

BINANCE_BASE = "https://api.binance.com/api/v3/klines"

def get_crypto_candles(symbol="BTCUSDT", interval="5m", limit=100):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(BINANCE_BASE, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "num_trades",
        "taker_base_vol", "taker_quote_vol", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df
