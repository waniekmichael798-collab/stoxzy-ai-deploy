import yfinance as yf
import math
import pandas as pd

def safe(v, m=1, d=1):
    if v is None: return None
    try:
        x = float(v)
        return None if math.isnan(x) or math.isinf(x) else x * m / d
    except: return None

def fetch(ticker):
    stk = yf.Ticker(ticker)
    info = stk.info
    if not info or not info.get('regularMarketPrice') and not info.get('currentPrice'):
        raise ValueError(f"Not found: {ticker}")
    
    price = safe(info.get('currentPrice')) or safe(info.get('regularMarketPrice'))
    shares = safe(info.get('sharesOutstanding')) or 1
    
    d = {
        'name': info.get('longName', ticker),
        'sector': info.get('sector', '—'),
        'price': price,
        'mcap': safe(info.get('marketCap')),
        'pe': safe(info.get('trailingPE')),
        'pb': safe(info.get('priceToBook')),
        'roe': safe(info.get('returnOnEquity'), m=100),
        'de': safe(info.get('debtToEquity'), d=100),
        'cr': safe(info.get('currentRatio')),
        'gm': safe(info.get('grossMargins'), m=100),
        'eps': safe(info.get('trailingEps')),
    }
    
    try:
        cf = stk.cashflow
        d['fcf'] = cf.loc['Free Cash Flow'].iloc[0] / shares if 'Free Cash Flow' in cf.index else None
    except: d['fcf'] = None
    
    try:
        inc = stk.income_stmt
        def cagr(row):
            if inc.empty or row not in inc.index: return None
            v = inc.loc[row].dropna()
            if len(v) < 2 or v.iloc[-1] <= 0 or v.iloc[0] <= 0: return None
            return ((v.iloc[0]/v.iloc[-1])**(1/(len(v)-1)) - 1) * 100
        d['revg'] = cagr('Total Revenue')
        d['epsg'] = cagr('Net Income')
    except: d['revg'], d['epsg'] = None, None
    
    d['hist'] = stk.history(period='1y')
    return d


