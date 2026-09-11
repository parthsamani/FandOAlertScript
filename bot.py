# bot.py - FINAL - 200 STOCKS - FIXED
import yfinance as yf
import pandas as pd
import requests, os, time
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PIVOT_LEN = 20
CHANNEL_W = 5
VOLUME_MULT = 1.5
MOVEMENT_MIN = 1.0
NEAR_PCT = 0.5

# FULL 200 STOCKS LIST
ALL_STOCKS = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS",
"AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","ASIANPAINT.NS","WIPRO.NS","HCLTECH.NS","ULTRACEMCO.NS","TITAN.NS","SUNPHARMA.NS","POWERGRID.NS",
"NTPC.NS","ONGC.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","GRASIM.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS",
"BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","M&M.NS","TECHM.NS","BPCL.NS","INDUSINDBK.NS","VEDL.NS","HINDUNILVR.NS",
"NESTLEIND.NS","HINDALCO.NS","COALINDIA.NS","UPL.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS","SBICARD.NS","BAJAJHLDNG.NS",
"RELIANCE.NS","LTIM.NS","HDFCAMC.NS","ICICIGI.NS","PIDILITIND.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","MUTHOOTFIN.NS",
"BANDHANBNK.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","PNB.NS","BANKBARODA.NS","CANBK.NS","UNIONBANK.NS","INDIANB.NS","AUBANK.NS","RBLBANK.NS",
"CHOLAFIN.NS","SHREECEM.NS","AMBUJACEM.NS","ACC.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","BRIGADE.NS","INDHOTEL.NS",
"ZOMATO.NS","NYKAA.NS","PAYTM.NS","POLICYBZR.NS","DELHIVERY.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","LTTS.NS","LTI.NS",
"BIOCON.NS","LUPIN.NS","AUROPHARMA.NS","TORNTPHARM.NS","ALKEM.NS","LAURUSLABS.NS","IPCALAB.NS","ZYDUSLIFE.NS","GLENMARK.NS","TATACONSUM.NS",
"JUBLFOOD.NS","TATAMOTORS.NS","ASHOKLEY.NS","TVSMOTOR.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","BHARATFORG.NS","MOTHERSON.NS","BOSCHLTD.NS",
"SIEMENS.NS","ABB.NS","HAVELLS.NS","CUMMINSIND.NS","VOLTAS.NS","DIXON.NS","AMBER.NS","POLYCAB.NS","KEI.NS","CGPOWER.NS",
"ADANIGREEN.NS","ADANIPOWER.NS","TATAPOWER.NS","JSWENERGY.NS","NHPC.NS","SJVN.NS","PFC.NS","RECLTD.NS","IRFC.NS","HUDCO.NS",
"HAL.NS","BEL.NS","BDL.NS","BHEL.NS","CONCOR.NS","IRCTC.NS","RVNL.NS","IRCON.NS","MAZAGON.NS","COCHINSHIP.NS",
"SAIL.NS","NMDC.NS","NATIONALUM.NS","JINDALSTEL.NS","JSL.NS","TATASTEEL.NS","APLAPOLLO.NS","JINDALSAW.NS","WELCORP.NS","RATNAMANI.NS",
"SRF.NS","DEEPAKNTR.NS","AARTIIND.NS","NAVINFLUOR.NS","PIIND.NS","COROMANDEL.NS","CHAMBLFERT.NS","GNFC.NS","GSPL.NS","IGL.NS",
"MGL.NS","PETRONET.NS","GAIL.NS","OIL.NS","HINDPETRO.NS","IOC.NS","CHENNPETRO.NS","MRPL.NS","AEGISCHEM.NS","ATUL.NS",
"PAGEIND.NS","TRENT.NS","DMART.NS","ABFRL.NS","RAYMOND.NS","BATAINDIA.NS","METROPOLIS.NS","RELAXO.NS","KAJARIACER.NS","CERA.NS",
"INDIGO.NS","SPICEJET.NS","TATACOMM.NS","HFCL.NS","TEJASNET.NS","STERLITE.NS","RAJESHEXPO.NS","MANAPPURAM.NS","IIFL.NS","MOTILALOFS.NS",
"ANGELONE.NS","CDSL.NS","BSE.NS","MCX.NS","CAMS.NS","KFINTECH.NS","NAM-INDIA.NS","UTIAMC.NS","IDFC.NS","LICHSGFIN.NS",
"POONAWALLA.NS","MFSL.NS","STARHEALTH.NS","GICRE.NS","NIACL.NS","ICICIPRULI.NS","HDFCLIFE.NS","SBILIFE.NS","INDIAMART.NS","JUSTDIAL.NS",
"NAUKRI.NS","AFFLE.NS","INTELLECT.NS","BSOFT.NS","KPITTECH.NS","TATAELXSI.NS","SONATSOFTW.NS","MASTEK.NS","FIRSTSOURCE.NS","ECLERX.NS"
]

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    if now.weekday() >= 5: return False
    return now.replace(hour=9, minute=15) <= now <= now.replace(hour=15, minute=35)

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_pivots(df, length=20):
    ph, pl = [], []
    highs = df['High'].values
    lows = df['Low'].values
    for i in range(length, len(df)-length):
        if highs[i] == max(highs[i-length:i+length+1]): ph.append((i, highs[i]))
        if lows[i] == min(lows[i-length:i+length+1]): pl.append((i, lows[i]))
    return ph, pl

if not is_market_open(): exit(0)
print(f"OPEN - Scanning {len(ALL_STOCKS)} | 5m/5d W:{CHANNEL_W}%", flush=True)

for stock in ALL_STOCKS:
    try:
        df = yf.Ticker(stock).history(period="5d", interval="5m", auto_adjust=True)
        if df.empty or len(df) < 100: continue
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        mov = (df['High'].tail(78).max() - df['Low'].tail(78).min()) / df['Open'].iloc[-78] * 100
        if mov < MOVEMENT_MIN: continue

        avg_vol = df['Volume'].tail(20).mean()
        vol_ratio = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 0
        if vol_ratio < VOLUME_MULT: continue

        ph, pl = get_pivots(df, PIVOT_LEN)
        if len(ph+pl) < 5: continue

        cwidth = (df['High'].tail(300).max() - df['Low'].tail(300).min()) * CHANNEL_W / 100
        zones = []
        for _, price in sorted(ph+pl, key=lambda x: x[0])[-50:]:
            found=False
            for z in zones:
                if abs(z['hi'] - price) <= cwidth:
                    z['hi']=max(z['hi'],price); z['lo']=min(z['lo'],price); found=True; break
            if not found: zones.append({'hi':price,'lo':price})

        cmp = df['Close'].iloc[-1]
        sl_low = pl[-1][1] if pl else df['Low'].min()
        sl_high = ph[-1][1] if ph else df['High'].max()
        now_str = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p')

        for z in zones:
            if z['hi'] < cmp and abs(cmp - z['hi'])/cmp*100 <= NEAR_PCT:
                send(f"🔥 *{stock} - LONG*\nRange: {z['lo']:.2f}-{z['hi']:.2f}\nCMP: {cmp:.2f} SL: {sl_low:.2f}\nMove: {mov:.1f}% Vol: {vol_ratio:.1f}x\nTime: {now_str}")
                break
            if z['lo'] > cmp and abs(cmp - z['lo'])/cmp*100 <= NEAR_PCT:
                send(f"🔻 *{stock} - SHORT*\nRange: {z['lo']:.2f}-{z['hi']:.2f}\nCMP: {cmp:.2f} SL: {sl_high:.2f}\nMove: {mov:.1f}% Vol: {vol_ratio:.1f}x\nTime: {now_str}")
                break
        time.sleep(0.3)
    except: continue
print("Scan Complete", flush=True)
