import requests
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"   # FastAPI backend URL

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Text Analyzer",
    page_icon="🔍",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap');
:root {
    --bg:        #0d0f14;
    --surface:   #151820;
    --border:    #242836;
    --accent:    #e8ff47;
    --accent2:   #47c5ff;
    --text:      #e8eaf0;
    --muted:     #6b7280;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
/* Main container */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 3rem 4rem 4rem !important;
    max-width: 960px;
    margin: 0 auto;
}
/* ── Header ── */
.header-wrap {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
}
.header-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: var(--text);
    line-height: 1;
}
.header-badge {
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    border: 1px solid var(--accent);
    padding: 2px 8px;
    border-radius: 2px;
    position: relative;
    top: -4px;
}
.header-sub {
    font-size: 0.9rem;
    color: var(--muted);
    font-weight: 400;
    letter-spacing: 0.02em;
    margin-bottom: 2.5rem;
    font-family: 'DM Mono', monospace;
}
/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--border) 60%);
    margin: 2rem 0;
    border: none;
}
/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
    border-radius: 4px !important;
    transition: all 0.2s;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
/* ── Text preview box ── */
.preview-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.7;
    color: var(--muted);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 200px;
    overflow-y: auto;
}
.preview-box::-webkit-scrollbar { width: 4px; }
.preview-box::-webkit-scrollbar-track { background: transparent; }
.preview-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
/* ── Stat pills ── */
.stat-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 1rem 0 1.5rem;
}
.stat-pill {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
}
.stat-pill span {
    color: var(--accent);
    font-weight: 500;
}
/* ── Analysis buttons ── */
.analysis-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
/* Streamlit buttons */
.stButton > button {
    width: 100% !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(232,255,71,0.04) !important;
}
.stButton > button:active {
    background: rgba(232,255,71,0.08) !important;
}
/* ── Result card ── */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-label {
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.75rem;
}
.result-content {
    font-size: 0.9rem;
    line-height: 1.8;
    color: var(--text);
    font-weight: 400;
}
/* ── Spinner override ── */
[data-testid="stSpinner"] > div {
    color: var(--accent) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}
/* ── Error / info ── */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    color: var(--muted) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Analysis button labels → API keys ────────────────────────────────────────
ANALYSES = {
    "📋  Summarize":      "summarize",
    "😊  Sentiment":      "sentiment",
    "🔑  Key Themes":     "key_themes",
    "❓  Q&A Pairs":      "qa_pairs",
    "✍️  Writing Style":  "writing_style",
    "🌍  Translate → ES": "translate_es",
}


def call_api(analysis_type: str, text: str) -> str:
    """POST to the FastAPI backend and return the result string."""
    try:
        resp = requests.post(
            f"{API_BASE}/analyze",
            json={"analysis_type": analysis_type, "text": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["result"]
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Cannot reach the API server. "
            "Make sure FastAPI is running: `uvicorn api:app --reload`"
        )
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        return f"⚠️ API error {e.response.status_code}: {detail}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
  <div class="header-title">Text Analyzer</div>
  <div class="header-badge">AI · Powered</div>
</div>
<div class="header-sub">// upload a .txt file → choose an analysis → get instant insights</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── File upload ──────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop your file here or click to browse",
    type=["txt"],
    label_visibility="collapsed",
)

if uploaded:
    raw = uploaded.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    words     = len(text.split())
    chars     = len(text)
    lines     = len(text.splitlines())
    sentences = text.count('.') + text.count('!') + text.count('?')

    # Stats
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">words: <span>{words:,}</span></div>
      <div class="stat-pill">chars: <span>{chars:,}</span></div>
      <div class="stat-pill">lines: <span>{lines:,}</span></div>
      <div class="stat-pill">sentences: <span>{sentences:,}</span></div>
      <div class="stat-pill">file: <span>{uploaded.name}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Preview
    preview = text[:800] + ("…" if len(text) > 800 else "")
    st.markdown(f'<div class="preview-box">{preview}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**Choose an analysis**", help="Select one of the six analysis modes below.")

    # Analysis buttons in a 3-column grid
    cols = st.columns(3)
    selected_label = None
    for i, label in enumerate(ANALYSES):
        if cols[i % 3].button(label, key=f"btn_{i}"):
            selected_label = label

    if selected_label:
        api_key = ANALYSES[selected_label]
        with st.spinner(f"Analyzing · {selected_label.strip()} …"):
            result = call_api(api_key, text)

        st.markdown(f"""
        <div class="result-card">
          <div class="result-label">↳ {selected_label.strip()}</div>
          <div class="result-content">{result.replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #3a3f52; font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:0.1em;">
        NO FILE LOADED · AWAITING INPUT
    </div>
    """, unsafe_allow_html=True)
