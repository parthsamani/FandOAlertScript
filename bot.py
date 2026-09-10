import yfinance as yf
import pandas as pd
import requests, os, time
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# TEST ke liye sirf 10 stocks
FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS"]

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    if now.weekday() >= 5:
        print(f"Weekend {now} - No Alert", flush=True)
        return False
    if not (now.replace(hour=9, minute=15) <= now <= now.replace(hour=15, minute=35)):
        print(f"Market Closed {now.strftime('%I:%M %p')} - No Alert", flush=True)
        return False
    return True

def send(msg):
    try:
        print(f"Sending: {msg[:80]}", flush=True)
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(f"Telegram response: {r.text}", flush=True)
    except Exception as e:
        print(f"Send Error: {e}", flush=True)

if not is_market_open():
    exit(0)

print(f"Market OPEN - Scanning {len(FNO_STOCKS)}...", flush=True)
print(f"TOKEN present: {bool(TOKEN)}, CHAT_ID present: {bool(CHAT_ID)}", flush=True)

# Pehle Telegram test
send("✅ *Test Alert* - Bot connected! Scanning starts now.")

for stock in FNO_STOCKS:
    try:
        print(f"Checking {stock}...", flush=True)
        df = yf.Ticker(stock).history(period="2d", interval="5m", auto_adjust=True)
        print(f"{stock}: got {len(df)} candles", flush=True)
        if df.empty or len(df) < 20:
            continue
        # Simple alert for test - har stock pe alert bhejega
        cmp = df['Close'].iloc[-1]
        send(f"🔥 *{stock} - TEST LONG*\nCMP: {cmp:.2f}\nTime: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p')}")
        time.sleep(1)
    except Exception as e:
        print(f"Error {stock}: {e}", flush=True)

print("Scan Complete", flush=True)
