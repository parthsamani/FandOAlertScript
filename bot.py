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
NEAR_PCT = 0.5

FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","ASIANPAINT.NS","WIPRO.NS","HCLTECH.NS","ULTRACEMCO.NS","TITAN.NS","SUNPHARMA.NS","POWERGRID.NS","NTPC.NS","ONGC.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","GRASIM.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","M&M.NS","TECHM.NS","BPCL.NS","INDUSINDBK.NS","VEDL.NS","HINDUNILVR.NS","NESTLEIND.NS","HINDALCO.NS","COALINDIA.NS","UPL.NS","TATAMOTORS.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS"]

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    if now.weekday() >= 5: # Saturday Sunday
        print(f"Weekend {now} - No Alert")
        return False
    if not (now.replace(hour=9, minute=15) <= now <= now.replace(hour=15, minute=35)):
        print(f"Market Closed {now.strftime('%I:%M %p')} - No Alert")
        return False
    return True

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(e)

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

# --- MAIN FILTER ---
if not is_market_open():
    exit(0)

print(f"Market OPEN - Scanning {len(FNO_STOCKS)}...")

for stock in FNO_STOCKS:
    try:
        df = yf.download(stock, period="5d", interval="5m", progress=False, auto_adjust=True, timeout=10)
        if len(df) < 300:
            time.sleep(1)
            continue
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        mov = (df['High'].tail(78).max() - df['Low'].tail(78).min()) / df['Open'].iloc[-78] * 100
        if mov < MOVEMENT_MIN:
            time.sleep(1)
            continue
        if df['Volume'].iloc[-1] < df['Volume'].tail(20).mean() * VOLUME_MULT:
            time.sleep(1)
            continue

        ph, pl = get_pivots(df, PIVOT_LEN)
        if len(ph+pl) < 5:
            time.sleep(1)
            continue

        cwidth = (df['High'].tail(300).max() - df['Low'].tail(300).min()) * CHANNEL_W / 100
        zones = []
        for _, price in sorted(ph+pl, key=lambda x: x[0])[-50:]:
            found=False
            for z in zones:
                if abs(z['hi'] - price) <= cwidth:
                    z['hi'] = max(z['hi'], price); z['lo'] = min(z['lo'], price); found=True; break
            if not found: zones.append({'hi': price, 'lo': price})

        cmp = df['Close'].iloc[-1]
        sl_low = pl[-1][1] if pl else df['Low'].min()
        sl_high = ph[-1][1] if ph else df['High'].max()
        ist = pytz.timezone('Asia/Kolkata')
        now_str = datetime.now(ist).strftime('%I:%M %p')

        for z in zones:
            if z['hi'] < cmp and abs(cmp - z['hi'])/cmp*100 <= NEAR_PCT:
                if z['lo'] <= df['Low'].iloc[-1] <= z['hi'] or z['lo'] <= cmp <= z['hi']:
                    send(f"🔥 *{stock} - LONG*\nBuying Range: {z['lo']:.2f} - {z['hi']:.2f}\nCMP: {cmp:.2f}\nSL: {float(sl_low):.2f} 🦎\nMove: {mov:.2f}% | Vol: {VOLUME_MULT}x\nTime: {now_str}")
                    break
            if z['hi'] > cmp and abs(cmp - z['lo'])/cmp*100 <= NEAR_PCT:
                if z['lo'] <= df['High'].iloc[-1] <= z['hi'] or z['lo'] <= cmp <= z['hi']:
                    send(f"🔥 *{stock} - SHORT*\nSelling Range: {z['lo']:.2f} - {z['hi']:.2f}\nCMP: {cmp:.2f}\nSL: {float(sl_high):.2f} 🐍\nMove: {mov:.2f}% | Vol: {VOLUME_MULT}x\nTime: {now_str}")
                    break
        time.sleep(1.2)
    except Exception as e:
        print(f"Error {stock}: {e}")
        time.sleep(1)
        continue
