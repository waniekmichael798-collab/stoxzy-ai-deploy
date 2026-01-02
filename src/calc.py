def graham(eps, g=7):
    if not eps or eps <= 0: return 0
    return eps * (8.5 + 2 * min(g, 15)) * 4.4 / 5

def dcf(fcf, g=5):
    if not fcf or fcf <= 0: return 0
    g = min(g, 10) / 100
    pv, cf = 0, fcf
    for y in range(1, 11):
        cf *= (1 + g)
        pv += cf / (1.1 ** y)
    return pv + (cf * 1.025 / 0.075) / (1.1 ** 10)

def intrinsic(d):
    g = d.get('epsg') or d.get('revg') or 7
    gr, dc = graham(d.get('eps'), g), dcf(d.get('fcf'), d.get('revg') or 5)
    return gr * 0.6 + dc * 0.4 if gr and dc else gr or dc or 0

def mos(price, iv):
    return (iv - price) / price * 100 if price and iv else 0
