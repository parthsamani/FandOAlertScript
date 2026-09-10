import yfinance as yf
import pandas as pd
import requests, os, time
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PIVOT_LEN = 50
CHANNEL_W = 5
VOLUME_MULT = 1.5
MOVEMENT_MIN = 1.0
NEAR_PCT = 0.5 # Wapas 0.5 kar diya, ab sahi alerts ayenge

# TATAMOTORS.NS delisted hai isliye hata diya - ab 49 stocks
FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","ASIANPAINT.NS","WIPRO.NS","HCLTECH.NS","ULTRACEMCO.NS","TITAN.NS","SUNPHARMA.NS","POWERGRID.NS","NTPC.NS","ONGC.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","GRASIM.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","M&M.NS","TECHM.NS","BPCL.NS","INDUSINDBK.NS","VEDL.NS","HINDUNILVR.NS","NESTLEIND.NS","HINDALCO.NS","COALINDIA.NS","UPL.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS"]

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
        print(f"Telegram response: {r.status_code}", flush=True)
    except Exception as e:
        print(f"Send Error: {e}", flush=True)

def get_pivots(df, length=50):
    ph, pl = [], []
    highs = df['High'].values
    lows = df['Low'].values
    for i in range(length, len(df)-length):
        if highs[i] == max(highs[i-length:i+length+1]):
            ph.append((i, highs[i]))
        if lows[i] == min(lows[i-length:i+length+1]):
            pl.append((i, lows[i]))
    return ph, pl

if not is_market_open():
    exit(0)

print(f"Market OPEN - Scanning {len(FNO_STOCKS)}...", flush=True)

for stock in FNO_STOCKS:
    try:
        df = yf.Ticker(stock).history(period="5d", interval="5m", auto_adjust=True)
        if df.empty or len(df) < 100:
            print(f"{stock}: No data {
