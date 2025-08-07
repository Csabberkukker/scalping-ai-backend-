import os
import requests
import pandas as pd
import numpy as np
from fastapi import FastAPI
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from fastapi.middleware.cors import 
CORSMiddleware

--- Alap beállítások ---

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY") BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

--- Binance adatlekérés ---

def get_binance_klines(symbol="BTCUSDT", interval="3m", limit=100): url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}" response = requests.get(url) data = response.json() df = pd.DataFrame(data, columns=[ "timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "num_trades", "taker_buy_base_vol", "taker_buy_quote_vol", "ignore" ]) df = df[["timestamp", "open", "high", "low", "close", "volume"]].astype(float) return df

--- Indikátorok számítása és setup generálás ---

def generate_setup(df): df["rsi"] = RSIIndicator(df["close"], window=14).rsi() df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()

latest = df.iloc[-1]
signal = ""

if latest["rsi"] < 30 and latest["close"] > latest["ema20"]:
    signal = "Buy"
elif latest["rsi"] > 70 and latest["close"] < latest["ema20"]:
    signal = "Sell"
else:
    signal = "No trade"

return {
    "symbol": "BTC/USDT",
    "interval": "3m",
    "close": round(latest["close"], 2),
    "signal": signal,
    "entry": round(latest["close"], 2),
    "sl": round(latest["close"] * 0.995, 2),
    "tp": round(latest["close"] * 1.01, 2),
    "rsi": round(latest["rsi"], 2)
}

--- API végpont ---

@app.get("/analyze") def analyze(): df = get_binance_klines() result = generate_setup(df) return result

