import streamlit as st
import plotly.graph_objects as go
from src import fetch, intrinsic, mos, score, score_all
from src.config import APP, TAG, COLORS, SCORING

st.set_page_config(page_title=APP, page_icon="📊", layout="wide")
st.markdown("""<style>
.block-container{padding:1rem 2rem}
.score-box{text-align:center;padding:1rem;background:#f8f9fa;border-radius:12px}
.score-num{font-size:3rem;font-weight:700;margin:0;line-height:1}
.score-lbl{color:#6b7280;font-size:0.875rem}
#MainMenu,footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
c1.markdown(f"## 📊 {APP}")
c1.caption(TAG)
ticker = c2.text_input("", value="AAPL", placeholder="Ticker", label_visibility="collapsed").upper().strip()

if not ticker:
    st.info("Enter a ticker")
    st.stop()

try:
    with st.spinner(""):
        d = fetch(ticker)
        d['iv'] = intrinsic(d)
        d['mos'] = mos(d['price'], d['iv'])
        r = score_all(d)
except ValueError as e:
    st.error(f"❌ {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ {e}")
    st.stop()

st.divider()
h1, h2 = st.columns([3, 1])
h1.subheader(d['name'])
h1.caption(d['sector'])
col = COLORS[r['rating']]
h2.markdown(f'<div class="score-box"><p class="score-num" style="color:{col}">{r["total"]}</p><p class="score-lbl">stoxzy Score</p><p class="score-lbl" style="color:{col};font-weight:600">{r["rating"]}</p></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Price", f"${d['price']:,.2f}" if d['price'] else "—")
m2.metric("Fair Value", f"${d['iv']:,.2f}" if d['iv'] else "—")
m3.metric("Margin of Safety", f"{d['mos']:+.1f}%" if d['mos'] else "—", delta="Undervalued" if d.get('mos', 0) > 0 else "Overvalued")
m4.metric("Market Cap", f"${d['mcap']/1e9:.1f}B" if d['mcap'] else "—")

st.divider()
ch, va = st.columns([2.5, 1])
with ch:
    st.caption("**Price (1Y)**")
    if not d['hist'].empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d['hist'].index, y=d['hist']['Close'], mode='lines', line=dict(color='#3b82f6', width=2)))
        if d['iv'] > 0: fig.add_hline(y=d['iv'], line_dash="dot", line_color="#10b981", annotation_text=f"Fair ${d['iv']:.0f}")
        fig.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0), showlegend=False, plot_bgcolor='white', yaxis=dict(tickprefix='$', gridcolor='#f0f0f0'))
        st.plotly_chart(fig, use_container_width=True)
with va:
    st.caption("**Valuations**")
    from src.calc import graham, dcf
    g = d.get('epsg') or d.get('revg') or 7
    st.metric("Graham", f"${graham(d.get('eps'), g):,.0f}" if d.get('eps') else "—")
    st.metric("DCF", f"${dcf(d.get('fcf'), d.get('revg') or 5):,.0f}" if d.get('fcf') else "—")
    st.metric("Combined", f"${d['iv']:,.0f}" if d['iv'] else "—")

st.divider()
st.caption("**Score Breakdown**")
def cat(title, sc, mx, metrics):
    st.markdown(f"**{title}** {sc}/{mx}")
    st.progress(sc / mx)
    for k, lbl, fmt in metrics:
        v = d.get(k)
        p, icon = score(v, k)
        st.caption(f"{icon} {lbl}: {f'{v:{fmt}}' if v is not None else '—'} → {p}")

s1, s2, s3 = st.columns(3)
with s1: cat("Valuation", r['val'], 40, [('pe','P/E','.1f'), ('pb','P/B','.2f'), ('mos','MoS','+.0f%')])
with s2: cat("Quality", r['qual'], 35, [('roe','ROE','.0f%'), ('de','D/E','.2f'), ('cr','CR','.2f'), ('gm','GM','.0f%')])
with s3: cat("Growth", r['grow'], 25, [('revg','Rev','.1f%'), ('epsg','EPS','.1f%')])

st.divider()
cols = st.columns(5)
for c, t in zip(cols, ['AAPL','MSFT','GOOGL','JNJ','KO']):
    if c.button(t, use_container_width=True):
        st.session_state.ticker = t
        st.rerun()
st.caption("⚠️ Educational only. Not financial advice. | stoxzy.ai")
