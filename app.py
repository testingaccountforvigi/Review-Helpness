import html
import time
import streamlit as st
import streamlit.components.v1 as components
from model_utils import ensure_model, predict

st.set_page_config(page_title="ReviewRadar", page_icon="◉", layout="wide")

ARC_LEN = 314.159  # half-circle gauge arc length (pi * r, r = 100)


@st.cache_resource(show_spinner=False)
def get_model_snapshot():
    return ensure_model()


@st.cache_data(show_spinner=False)
def load_metrics():
    _, _, m = predict("This is a model warm-up sentence for loading metrics.", "Product")
    return m


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600;700&display=swap');
:root { --ink:#14182B; --paper:#F0F2F8; --white:#fff; --mute:#5E6580; --hi:#FFD84D; --blue:#3B4EFF; --line:#D3D9E9; --lilac:#DCD7FF; --mint:#C8F1E0; --peach:#FFD9CC; --ease:cubic-bezier(.2,.7,.2,1); }
#MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="InputInstructions"] { display:none !important; }
html, body, [class*="css"], .stApp, button, input, textarea { font-family:'Instrument Sans',sans-serif !important; color:var(--ink); -webkit-font-smoothing:antialiased; }
.stApp { background:var(--paper); }

/* one-section-per-scroll snapping */
[data-testid="stMain"], section.main, [data-testid="stAppViewContainer"] { scroll-snap-type:y mandatory; scroll-behavior:smooth; }
.block-container { max-width:1120px; padding:0 2rem !important; position:relative; z-index:1; }
.block-container > div[data-testid="stVerticalBlock"], [data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] { gap:0 !important; }
.snap, div[data-testid="stVerticalBlock"]:has(> div:first-child .snapmark) { min-height:100vh; min-height:100dvh; box-sizing:border-box; padding:96px 0 28px; display:flex; flex-direction:column; justify-content:center; scroll-snap-align:start; scroll-snap-stop:always; }
.snapmark { display:none; }
div[data-testid="stHorizontalBlock"] { align-items:center; }

/* fixed chrome: nav pill, stickers, progress rail */
.nav { position:fixed; top:18px; left:50%; transform:translateX(-50%); width:min(1056px, calc(100% - 3rem)); z-index:50; display:flex; align-items:center; justify-content:space-between; padding:10px 12px 10px 20px; background:var(--white); border:1.5px solid var(--ink); border-radius:999px; box-shadow:4px 4px 0 var(--ink); }
.brand { display:flex; align-items:center; gap:10px; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.25rem; letter-spacing:-.02em; }
.brand { cursor:pointer; transition:transform .3s var(--ease); }
.brand:hover { transform:scale(1.04) rotate(-1deg); }
.brand:focus-visible { outline:3px solid var(--hi); outline-offset:4px; border-radius:99px; }
.nav .meta { background:var(--paper); border-radius:999px; padding:8px 16px; color:var(--mute); font-size:.85rem; font-weight:600; }
.deco i { position:fixed; z-index:0; pointer-events:none; display:block; animation:bob 8s ease-in-out infinite; }
.deco .a { width:260px; height:260px; border-radius:50%; background:var(--hi); left:-120px; bottom:-90px; }
.deco .b { width:150px; height:150px; border-radius:50%; border:22px solid var(--blue); right:-50px; top:12%; animation-delay:-3s; }
.deco .c { width:120px; height:60px; border-radius:120px 120px 0 0; background:var(--ink); left:3%; top:16%; animation-delay:-5s; }
@keyframes bob { 50% { transform:translateY(-14px); } }
.rail { position:fixed; right:22px; top:50%; transform:translateY(-50%); height:44vh; width:22px; z-index:60; }
.rtrack { position:absolute; left:50%; top:0; bottom:0; width:6px; margin-left:-3px; border-radius:9px; background:#DDE2F0; border:1.5px solid var(--ink); box-sizing:content-box; }
.rfill { position:absolute; left:0; right:0; top:0; height:0%; background:var(--blue); border-radius:9px; }
.rknob { position:absolute; left:50%; top:0%; width:22px; height:22px; margin:-11px 0 0 -11px; border-radius:50%; background:var(--hi); border:2px solid var(--ink); z-index:3; display:grid; place-items:center; font-size:12px; font-weight:800; transition:background .3s; }
.rknob.complete { background:#7FE3B8; } .rknob.complete::after { content:"✓"; }
.rdot { position:absolute; left:50%; width:14px; height:14px; margin:-7px 0 0 -7px; padding:0; border-radius:50%; border:2px solid var(--ink); background:var(--white); cursor:pointer; z-index:2; transition:transform .3s var(--ease), background .3s; }
.rdot.done { background:var(--ink); } .rdot.on { background:var(--blue); transform:scale(1.3); }
.rdot::after { content:attr(data-l); position:absolute; right:26px; top:50%; transform:translateY(-50%) translateX(6px); white-space:nowrap; background:var(--ink); color:#fff; font-size:.75rem; font-weight:600; padding:5px 11px; border-radius:99px; opacity:0; pointer-events:none; transition:.25s var(--ease); }
.rdot:hover::after { opacity:1; transform:translateY(-50%); }
.rknob { top:0%; }

/* hero */
.headline { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:clamp(2.3rem, min(5vw, 7.8vh), 4.6rem); line-height:1; letter-spacing:-.04em; margin:0 0 .9rem; max-width:13ch; }
.headline mark { background:linear-gradient(var(--hi),var(--hi)) no-repeat 0 90% / 0% 46%; color:var(--ink); padding:0 .06em; animation:mark 1s .4s var(--ease) forwards; }
@keyframes mark { to { background-size:100% 46%; } }
.sub { color:var(--mute); font-size:clamp(.98rem,1.6vh + .4rem,1.12rem); line-height:1.6; max-width:44ch; margin:0 0 1.5rem; }
.field { font-weight:700; font-size:.95rem; margin:0 0 .4rem; }

/* inputs: light fields, border on the outer wrapper, only the text scrolls */
div[data-testid="stTextInput"], div[data-testid="stTextArea"] { color-scheme:light; margin-bottom:.4rem; }
div[data-testid="stTextInput"] div, div[data-testid="stTextArea"] div { background-color:#fff !important; border:0 !important; box-shadow:none !important; color:var(--ink) !important; }
div[data-testid="stTextInput"] div[data-baseweb="input"], div[data-testid="stTextArea"] div[data-baseweb="textarea"] { border:1.5px solid var(--ink) !important; border-radius:22px !important; box-shadow:4px 4px 0 var(--ink) !important; overflow:hidden; transition:box-shadow .3s var(--ease), border-color .3s, transform .3s var(--ease); }
div[data-testid="stTextInput"] div[data-baseweb="input"]:hover, div[data-testid="stTextArea"] div[data-baseweb="textarea"]:hover { box-shadow:6px 6px 0 var(--ink) !important; }
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within, div[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within { border-color:var(--blue) !important; box-shadow:6px 6px 0 var(--blue) !important; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea { background-color:#fff !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; caret-color:var(--blue); border:0 !important; box-shadow:none !important; outline:none !important; font-size:1.03rem !important; font-weight:500 !important; resize:none !important; }
div[data-testid="stTextInput"] input { padding:12px 22px !important; height:3.2rem; }
div[data-testid="stTextArea"] textarea { line-height:26px !important; padding:14px 22px 10px !important; overflow-y:auto !important; background-image:repeating-linear-gradient(to bottom, transparent 0, transparent 25px, #E3E8F5 25px, #E3E8F5 26px) !important; background-origin:content-box !important; background-attachment:local !important; }
div[data-testid="stTextArea"] textarea::-webkit-scrollbar { width:10px; } div[data-testid="stTextArea"] textarea::-webkit-scrollbar-thumb { background:var(--ink); border-radius:99px; border:3px solid #fff; }
div[data-testid="stTextInput"] input::placeholder, div[data-testid="stTextArea"] textarea::placeholder { color:#8A92AE !important; -webkit-text-fill-color:#8A92AE !important; opacity:1 !important; font-weight:400; }
.stButton button[kind="primary"] { margin-top:.6rem; background:var(--ink); color:#fff; border:1.5px solid var(--ink); border-radius:999px; min-height:56px; font-weight:700; font-size:1.05rem; box-shadow:3px 3px 0 var(--blue); transition:transform .25s var(--ease), box-shadow .25s var(--ease); }
.stButton button[kind="primary"]:hover { background:var(--ink); color:#fff; border-color:var(--ink); transform:translate(-2px,-2px); box-shadow:6px 6px 0 var(--blue); }
.stButton button[kind="primary"]:active { transform:translate(2px,2px); box-shadow:1px 1px 0 var(--blue); }
.stButton button:focus-visible { outline:3px solid var(--hi) !important; outline-offset:3px; }

/* attached tabs, fixed-size box (nothing can scroll except the text), footer counter and fill bar */
div[data-testid="stTextInput"], div[data-testid="stTextArea"] { margin:8px 0 0; overflow:visible; }
div[data-testid="stTextInput"]::before, div[data-testid="stTextArea"]::before { display:block; width:max-content; position:relative; z-index:3; margin:0 0 -1.5px 26px; padding:7px 18px 8px; border:1.5px solid var(--ink); border-bottom:0; border-radius:16px 16px 0 0; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:.88rem; line-height:1.1; transition:background .3s var(--ease), color .3s; }
div[data-testid="stTextInput"]::before { content:"Product"; background:var(--lilac); }
div[data-testid="stTextArea"]::before { content:"Your review sentence"; background:var(--hi); }
div[data-testid="stTextInput"]:focus-within::before, div[data-testid="stTextArea"]:focus-within::before { background:var(--blue); color:#fff; }
div[data-testid="stTextInput"] div[data-baseweb="input"] { overflow:hidden; overflow:clip; }
div[data-testid="stTextArea"] div[data-baseweb="textarea"] { position:relative; height:150px !important; padding-bottom:30px !important; box-sizing:border-box !important; overflow:hidden; overflow:clip; }
div[data-testid="stTextArea"] div[data-baseweb="base-input"] { height:100% !important; }
div[data-testid="stTextArea"] textarea { height:100% !important; min-height:0 !important; box-sizing:border-box !important; }
div[data-testid="stTextArea"] div[data-baseweb="textarea"]::after { content:""; position:absolute; left:22px; right:22px; bottom:11px; height:7px; border-radius:99px; background:linear-gradient(var(--blue),var(--blue)) no-repeat left center / var(--fill,0%) 100%, #E6EAF4; transition:background-size .4s var(--ease); pointer-events:none; }
div[data-testid="stTextArea"][data-ok="1"] div[data-baseweb="textarea"]::after { background:linear-gradient(#10A37F,#10A37F) no-repeat left center / var(--fill,0%) 100%, #E6EAF4; }
div[data-testid="stTextArea"]::after { content:"0 words"; display:block; text-align:right; margin:10px 6px 0 0; font-size:.82rem; font-weight:700; color:var(--mute); }
div[data-testid="stTextArea"][data-count]::after { content:attr(data-count); }
div[data-testid="stTextArea"][data-ok="1"]::after { content:"✓ " attr(data-count) ", good length"; color:#0B6B4F; }

/* result panel */
.panel { background:var(--white); border:1.5px solid var(--ink); border-radius:34px; box-shadow:9px 9px 0 var(--ink); padding:26px 28px 24px; }
.gauge { width:100%; max-width:330px; display:block; margin:0 auto; }
.gauge .track { stroke:#E6EAF4; }
.gauge .fill { stroke-dasharray:314.159; animation:sweep 1.2s var(--ease); }
@keyframes sweep { from { stroke-dashoffset:314.159; } }
.gauge .num { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:54px; fill:var(--ink); letter-spacing:-2px; }
.gauge .tick { font-size:11px; fill:var(--mute); font-family:'Instrument Sans',sans-serif; font-weight:600; }
.verdict { text-align:center; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.7rem; letter-spacing:-.025em; margin:4px 0; }
.panel .verdict-sub, .panel p.verdict-sub { display:block; width:100%; max-width:36ch; text-align:center !important; margin:0 auto !important; color:var(--mute); font-size:.93rem; line-height:1.5; }
.panel .verdict { width:100%; text-align:center !important; }
.quote { margin:16px 0 0; padding:14px 18px; border-radius:20px; background:var(--paper); font-size:.96rem; line-height:1.55; box-sizing:border-box; height:8.4rem; overflow-y:auto; overscroll-behavior:contain; scrollbar-width:thin; scrollbar-color:var(--ink) transparent; word-break:break-word; }
.quote::-webkit-scrollbar { width:8px; } .quote::-webkit-scrollbar-thumb { background:var(--ink); border-radius:99px; border:2px solid var(--paper); }
.quote span { background:linear-gradient(transparent 58%, var(--hi) 58%); }

/* sections */
.sh { text-align:center; margin:0 auto 2.4rem; }
.sh h2 { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:clamp(2rem, min(4.4vw, 7vh), 3.4rem); letter-spacing:-.035em; line-height:1.05; margin:0 0 .7rem; }
.sh p { color:var(--mute); margin:0 auto; max-width:50ch; line-height:1.6; font-size:1.05rem; }
.stButton button[kind="secondary"] { background:var(--white); color:var(--ink); border:1.5px solid var(--ink); border-radius:34px; box-shadow:6px 6px 0 var(--ink); justify-content:flex-start; align-items:flex-start; text-align:left; padding:28px 26px; min-height:250px; transition:transform .3s var(--ease), box-shadow .3s var(--ease); }
div[data-testid="stColumn"]:nth-child(1) .stButton button[kind="secondary"] { background:var(--lilac); }
div[data-testid="stColumn"]:nth-child(2) .stButton button[kind="secondary"] { background:var(--peach); }
div[data-testid="stColumn"]:nth-child(3) .stButton button[kind="secondary"] { background:var(--mint); }
.stButton button[kind="secondary"] p { font-size:1rem; line-height:1.6; text-align:left; font-weight:500; color:#2C3350; }
.stButton button[kind="secondary"] strong { display:block; font-family:'Bricolage Grotesque',sans-serif; font-size:1.55rem; font-weight:800; letter-spacing:-.02em; color:var(--ink); margin-bottom:12px; }
.stButton button[kind="secondary"]:hover { color:var(--ink); border-color:var(--ink); transform:translate(-3px,-3px) rotate(-.6deg); box-shadow:10px 10px 0 var(--ink); }
.g3, .g4 { display:grid; gap:24px; } .g3 { grid-template-columns:repeat(3,1fr); } .g4 { grid-template-columns:repeat(4,1fr); gap:20px; }
.card { border:1.5px solid var(--ink); border-radius:34px; box-shadow:6px 6px 0 var(--ink); padding:28px 26px; background:var(--white); }
.card:nth-child(1) { background:var(--lilac); } .card:nth-child(2) { background:var(--peach); } .card:nth-child(3) { background:var(--mint); } .card:nth-child(4) { background:#FFF0B3; }
.card .n { display:grid; place-items:center; width:54px; height:54px; border-radius:50%; background:var(--ink); color:#fff; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.5rem; margin-bottom:18px; }
.card .v { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:2.7rem; letter-spacing:-.04em; line-height:1; margin-bottom:14px; }
.card h3 { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.4rem; letter-spacing:-.02em; margin:0 0 8px; }
.card span { color:#3A4262; font-size:.97rem; line-height:1.6; }
.card .bar { height:10px; border-radius:99px; background:rgba(20,24,43,.12); margin-top:18px; overflow:hidden; } .card .bar i { display:block; height:100%; background:var(--ink); border-radius:99px; }
.again { display:block; margin:2.6rem auto 0; background:var(--ink); color:#fff; border:1.5px solid var(--ink); border-radius:999px; padding:16px 34px; font-weight:700; font-size:1.05rem; cursor:pointer; box-shadow:3px 3px 0 var(--blue); transition:transform .25s var(--ease), box-shadow .25s var(--ease); font-family:'Instrument Sans',sans-serif; }
.again:hover { transform:translate(-2px,-2px); box-shadow:6px 6px 0 var(--blue); }
.foot { text-align:center; color:var(--mute); font-size:.85rem; margin-top:2.2rem; }
@media (max-width:900px) {
  .rail, .deco { display:none; } .g3, .g4 { grid-template-columns:1fr; }
  [data-testid="stMain"], section.main, [data-testid="stAppViewContainer"] { scroll-snap-type:y proximity; }
  .snap, div[data-testid="stVerticalBlock"]:has(> div:first-child .snapmark) { min-height:auto; }
}
@media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; scroll-behavior:auto !important; } .headline mark { background-size:100% 46%; } }
</style>
<div class="deco"><i class="a"></i><i class="b"></i><i class="c"></i></div>
<div class="nav"><div class="brand" data-top="1" role="button" tabindex="0" aria-label="Back to the top"><svg width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="#14182B" stroke-width="2.4" stroke-linecap="round"><path d="M3 22a12 12 0 0 1 24 0"/><path d="M8.5 22a6.5 6.5 0 0 1 13 0"/><circle cx="15" cy="22" r="2.2" fill="#FFD84D"/></svg>ReviewRadar</div>
<div class="meta">TF-IDF + Ridge, trained on 20,000 human-rated sentences</div></div>
<div class="rail"><div class="rtrack"><div class="rfill"></div></div>
<button class="rdot" data-l="Score" style="top:0%"></button><button class="rdot" data-l="Samples" style="top:25%"></button><button class="rdot" data-l="How it works" style="top:50%"></button><button class="rdot" data-l="Accuracy" style="top:75%"></button><button class="rdot" data-l="Tips" style="top:100%"></button>
<div class="rknob"></div></div>
""", unsafe_allow_html=True)


def gauge_svg(score=None):
    if score is None:
        offset, color, label = ARC_LEN, "#E6EAF4", "–"
    else:
        offset = ARC_LEN * (1 - max(0, min(score, 2)) / 2)
        color = "#FF5C4D" if score < 0.7 else "#F5A524" if score < 1.3 else "#10A37F"
        label = f"{score:.2f}"
    return f"""<svg class="gauge" viewBox="0 0 240 150" role="img" aria-label="Helpfulness score {label} out of 2">
<path class="track" d="M 20 120 A 100 100 0 0 1 220 120" fill="none" stroke-width="20" stroke-linecap="round"/>
<path class="fill" d="M 20 120 A 100 100 0 0 1 220 120" fill="none" stroke="{color}" stroke-width="20" stroke-linecap="round" style="stroke-dashoffset:{offset}"/>
<text class="num" x="120" y="112" text-anchor="middle">{label}</text>
<text class="tick" x="20" y="144" text-anchor="middle">0</text><text class="tick" x="120" y="144" text-anchor="middle">out of 2</text><text class="tick" x="220" y="144" text-anchor="middle">2</text></svg>"""


def use_example(p, s):
    st.session_state["product"] = ""
    st.session_state["sentence"] = ""
    st.session_state.pop("result", None)
    st.session_state["product"] = p
    st.session_state["sentence"] = s
    st.session_state["goto_top"] = True


try:
    with st.spinner("Training the model for the first run. This happens once."):
        get_model_snapshot()
        base = load_metrics()
except Exception:
    base = None

# 1. Hero
with st.container():
    st.markdown('<span class="snapmark"></span>', unsafe_allow_html=True)
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown('<div class="headline">Is your review <mark>actually</mark> helpful?</div><p class="sub">Write one sentence about a product. ReviewRadar scores how useful it would be to someone deciding whether to buy, from 0 to 2.</p>', unsafe_allow_html=True)
        product = st.text_input("Product", key="product", placeholder="Wireless noise-cancelling headphones", label_visibility="collapsed")
        sentence = st.text_area("Review sentence", key="sentence", height=118, placeholder="What did you use it for? How did it compare, and why did it work or not?", label_visibility="collapsed")
        analyze = st.button("Score this sentence", type="primary", use_container_width=True)

    if analyze:
        if len(sentence.strip()) < 10:
            st.session_state["result"] = {"error": True}
        else:
            score, band, m = predict(sentence, product)
            st.session_state["result"] = {"score": score, "band": band, "text": sentence.strip(), "metrics": m}
    res = st.session_state.get("result")

    with right:
        if res and "score" in res:
            gauge, verdict = gauge_svg(res["score"]), html.escape(str(res["band"]))
            sub = "How useful this sentence is for a purchase decision, rated like the human benchmark."
            quote = f'<div class="quote"><span>{html.escape(res["text"])}</span></div>'
        else:
            gauge, quote = gauge_svg(None), ""
            if res and res.get("error"):
                verdict, sub = "Write a bit more", "Enter a full review sentence, at least 10 characters, to get a score."
            else:
                verdict, sub = "Waiting for a sentence", "Specific details and reasons score higher than general opinions. Your score lands here."
        st.markdown(f'<div class="panel">{gauge}<div class="verdict">{verdict}</div><p class="verdict-sub">{sub}</p>{quote}</div>', unsafe_allow_html=True)

metrics = (res or {}).get("metrics") or base

# 2. Samples
with st.container():
    st.markdown('<span class="snapmark"></span><div class="sh"><h2>Need a starting point?</h2><p>Pick a sample and it fills the form for you. Then score it and see how detail changes the result.</p></div>', unsafe_allow_html=True)
    examples = [
        ("Bluetooth headphones", "The noise cancellation is strong on flights, but voices remain audible enough to hear announcements."),
        ("Coffee machine", "It is good."),
        ("Walking DVD", "The routines are easy to follow, and the instructor gives clear modifications for beginners."),
    ]
    for col, (i, (p, s)) in zip(st.columns(3, gap="medium"), enumerate(examples)):
        with col:
            st.button(f"**{p}**\n\n{s}", key=f"ex_{i}", on_click=use_example, args=(p, s), use_container_width=True)

# 3. How it works
st.markdown("""<div class="snap"><div class="sh"><h2>How it works</h2><p>A small, fast model that learned from people instead of fixed rules.</p></div>
<div class="g3">
<div class="card"><div class="n">1</div><h3>Read</h3><span>TF-IDF turns your sentence into weighted word features, so rare, informative words count for more.</span></div>
<div class="card"><div class="n">2</div><h3>Weigh</h3><span>A Ridge regression, trained on 20,000 human-rated sentences, weighs those features.</span></div>
<div class="card"><div class="n">3</div><h3>Score</h3><span>You get a number from 0 to 2 that matches how a crowd would rate the sentence.</span></div></div></div>""", unsafe_allow_html=True)

# 4. Accuracy
if metrics:
    tiles = [("Within ±0.5", f'{metrics["within_half_accuracy"]:.1f}%', metrics["within_half_accuracy"], "Predictions that land within half a point of the human score."),
             ("Mean absolute error", f'{metrics["mae"]:.3f}', None, "Average gap between prediction and rating. Lower is better."),
             ("Mean squared error", f'{metrics["mse"]:.3f}', None, "Punishes big misses harder. Lower is better."),
             ("Pearson correlation", f'{metrics["pearson"]:.3f}', max(0, metrics["pearson"]) * 100, "How closely predictions follow human ratings. Higher is better.")]
    cells = "".join(f'<div class="card"><div class="v">{v}</div><h3>{t}</h3><span>{d}</span>' + (f'<div class="bar"><i style="width:{min(w, 100):.0f}%"></i></div>' if w is not None else "") + "</div>" for t, v, w, d in tiles)
else:
    cells = '<div class="card" style="grid-column:1/-1"><h3>Metrics are loading</h3><span>They appear here once the model has finished training.</span></div>'
st.markdown(f'<div class="snap"><div class="sh"><h2>How well does it work?</h2><p>Measured on 2,000 fixed test sentences, not on your input.</p></div><div class="g4">{cells}</div></div>', unsafe_allow_html=True)

# 5. Tips
st.markdown("""<div class="snap"><div class="sh"><h2>What raises the score</h2><p>Three habits that make a sentence useful to the next shopper.</p></div>
<div class="g3">
<div class="card"><h3>Be specific</h3><span>Name the feature, the situation or the number you noticed.</span></div>
<div class="card"><h3>Give a reason</h3><span>Explain why something worked or failed, not just that it did.</span></div>
<div class="card"><h3>Compare</h3><span>Say how it stacks up against something the reader may already know.</span></div></div>
<button class="again" data-top="1">Score another sentence</button>
<div class="foot">ReviewRadar, an academic machine learning case study.</div></div>""", unsafe_allow_html=True)

boot = "booted" not in st.session_state
st.session_state["booted"] = True
mode = "smooth" if st.session_state.pop("goto_top", False) else ("instant" if boot else "")
components.html("""<script>
(function () {
  // run __N__
  const P = window.parent, D = P.document;
  if (P.__rrClean) P.__rrClean();
  const sc = D.querySelector('[data-testid="stMain"]') || D.querySelector('section.main') || D.querySelector('[data-testid="stAppViewContainer"]');
  const fill = D.querySelector('.rfill'), knob = D.querySelector('.rknob'), dots = [...D.querySelectorAll('.rdot')];
  if (!sc || !fill) return;
  const secs = () => [...D.querySelectorAll('.snapmark, .snap')].map(e => e.classList.contains('snapmark') ? e.closest('[data-testid="stVerticalBlock"]') : e);
  function update() {
    const max = sc.scrollHeight - sc.clientHeight, p = max > 0 ? Math.min(1, sc.scrollTop / max) : 0;
    fill.style.height = (p * 100) + '%'; knob.style.top = (p * 100) + '%';
    knob.classList.toggle('complete', p > 0.985);
    let idx = 0; secs().forEach((s, i) => { if (s && s.getBoundingClientRect().top <= sc.clientHeight * 0.5) idx = i; });
    dots.forEach((d, i) => { d.classList.toggle('on', i === idx); d.classList.toggle('done', i < idx); });
  }
  sc.addEventListener('scroll', update, { passive: true }); P.addEventListener('resize', update);
  dots.forEach((d, i) => { d.onclick = () => { const s = secs()[i]; if (s) s.scrollIntoView({ behavior: 'smooth', block: 'start' }); }; });
  const top = e => { if (e.target.closest('[data-top]')) sc.scrollTo({ top: 0, behavior: 'smooth' }); };
  D.addEventListener('click', top);
  const key = e => { if (e.key === 'Enter') top(e); };
  D.addEventListener('keydown', key);
  P.__rrClean = () => { sc.removeEventListener('scroll', update); P.removeEventListener('resize', update); D.removeEventListener('click', top); D.removeEventListener('keydown', key); };
  const box = D.querySelector('[data-testid="stTextArea"]'), area = box && box.querySelector('textarea');
  function count() {
    if (!area) return;
    const n = (area.value.trim().match(/\\S+/g) || []).length;
    box.setAttribute('data-count', n + (n === 1 ? ' word' : ' words'));
    box.style.setProperty('--fill', Math.min(100, n / 25 * 100) + '%');
    if (n >= 8 && n <= 40) box.setAttribute('data-ok', '1'); else box.removeAttribute('data-ok');
  }
  if (area) { area.addEventListener('input', count); count(); setTimeout(count, 400); setTimeout(count, 900); }
  const prevClean = P.__rrClean;
  P.__rrClean = () => { prevClean(); if (area) area.removeEventListener('input', count); };
  update();
  try { P.history.scrollRestoration = 'manual'; } catch (e) {}
  const mode = '__MODE__';
  if (mode) {
    const go = () => sc.scrollTo({ top: 0, behavior: mode === 'instant' ? 'instant' : 'smooth' });
    go();
    if (mode === 'instant') { setTimeout(go, 150); setTimeout(go, 600); } else setTimeout(go, 80);
  }
})();
</script>""".replace("__MODE__", mode).replace("__N__", str(time.time_ns())), height=0)