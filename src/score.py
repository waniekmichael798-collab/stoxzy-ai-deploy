from src.config import SCORING

def score(val, key):
    thresh, pts, lower = SCORING[key]
    if val is None: return pts[0] // 3, '⚪'
    for i, t in enumerate(thresh):
        if (lower and val < t) or (not lower and val > t):
            return pts[i], '🟢' if i == 0 else '🟡'
    return pts[-1], '🔴'

def score_all(d):
    s = {k: score(d.get(k), k)[0] for k in SCORING}
    val = s['pe'] + s['pb'] + s['mos']
    qual = s['roe'] + s['de'] + s['cr'] + s['gm']
    grow = s['revg'] + s['epsg']
    total = val + qual + grow
    rating = 'GREEN' if total >= 70 else 'YELLOW' if total >= 50 else 'RED'
    return {'s': s, 'val': val, 'qual': qual, 'grow': grow, 'total': total, 'rating': rating}
