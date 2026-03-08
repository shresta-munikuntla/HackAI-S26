import streamlit as st
import json
import re
import os
import base64
from datetime import datetime
from google import genai
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantAnalyzer.AI",
    page_icon="📡",
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
    --red:       #ff4f4f;
    --green:     #4fff91;
    --text:      #e8eaf0;
    --muted:     #6b7280;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 3rem 4rem 4rem !important;
    max-width: 1020px;
    margin: 0 auto;
}

/* ── Header ── */
.header-wrap { display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 0.25rem; }
.header-title { font-size: 2.6rem; font-weight: 800; letter-spacing: -0.04em; color: var(--text); line-height: 1; }
.header-badge {
    font-size: 0.65rem; font-family: 'DM Mono', monospace; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent); border: 1px solid var(--accent);
    padding: 2px 8px; border-radius: 2px; position: relative; top: -4px;
}
.header-sub {
    font-size: 0.85rem; color: var(--muted); font-weight: 400; letter-spacing: 0.02em;
    margin-bottom: 2.5rem; font-family: 'DM Mono', monospace;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--border) 60%);
    margin: 2rem 0; border: none;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 8px !important; padding: 1.5rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--muted) !important; font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important; border-radius: 4px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important;
}

/* ── Stat pills ── */
.stat-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 1rem 0 1.5rem; }
.stat-pill {
    font-family: 'DM Mono', monospace; font-size: 0.75rem; color: var(--muted);
    border: 1px solid var(--border); border-radius: 20px; padding: 4px 14px;
}
.stat-pill span { color: var(--accent); font-weight: 500; }

/* ── Preview box ── */
.preview-box {
    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    padding: 1.25rem 1.5rem; font-family: 'DM Mono', monospace; font-size: 0.8rem;
    line-height: 1.7; color: var(--muted); white-space: pre-wrap; word-break: break-word;
    max-height: 200px; overflow-y: auto;
}
.preview-box::-webkit-scrollbar { width: 4px; }
.preview-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Run button ── */
.stButton > button {
    width: 100% !important; background: var(--accent) !important;
    color: #0d0f14 !important; border: none !important; border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important; font-size: 0.95rem !important;
    font-weight: 800 !important; letter-spacing: 0.06em !important;
    padding: 0.85rem 1rem !important; transition: all 0.2s !important;
}
.stButton > button:hover { background: #d4eb3a !important; }

/* ── Signal hero ── */
.signal-hero {
    border-radius: 10px; padding: 2rem 2.5rem; margin: 1.5rem 0;
    border: 1px solid var(--border); animation: fadeIn 0.5s ease;
}
.signal-hero.bullish { border-left: 4px solid var(--green);  background: rgba(79,255,145,0.04); }
.signal-hero.bearish { border-left: 4px solid var(--red);    background: rgba(255,79,79,0.04); }
.signal-hero.neutral { border-left: 4px solid var(--muted);  background: var(--surface); }
.signal-hero-label { font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
.signal-hero-direction { font-size: 3rem; font-weight: 800; letter-spacing: -0.04em; margin: 0.25rem 0 0; line-height: 1; }
.signal-hero-direction.bullish { color: var(--green); }
.signal-hero-direction.bearish { color: var(--red); }
.signal-hero-direction.neutral { color: var(--muted); }
.signal-hero-sub { font-size: 0.8rem; font-family: 'DM Mono', monospace; color: var(--muted); margin-top: 0.4rem; }

/* ── Metric grid ── */
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.metric-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 1rem 1.25rem; animation: fadeIn 0.5s ease;
}
.metric-label { font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.4rem; }
.metric-value { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text); }
.metric-sub { font-size: 0.7rem; font-family: 'DM Mono', monospace; color: var(--muted); margin-top: 0.2rem; }

/* ── Section cards ── */
.section-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; animation: fadeIn 0.5s ease;
}
.section-title {
    font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 0.75rem;
}
.section-body { font-size: 0.88rem; line-height: 1.75; color: var(--text); }
.tag {
    display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.7rem;
    border: 1px solid var(--border); border-radius: 3px; padding: 2px 8px;
    margin: 2px 4px 2px 0; color: var(--muted);
}

/* ── Explanation card ── */
.explanation-card {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 3px solid var(--accent2); border-radius: 8px;
    padding: 1.5rem; margin-top: 1rem; animation: fadeIn 0.6s ease;
}
.explanation-title {
    font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--accent2); margin-bottom: 0.75rem;
}
.explanation-body { font-size: 0.9rem; line-height: 1.85; color: var(--text); }

/* ── Audio player ── */
.audio-label {
    font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--accent); margin: 1.5rem 0 0.5rem;
}
[data-testid="stAudio"] { margin-top: 0.25rem; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

[data-testid="stSpinner"] > div {
    color: var(--accent) !important; font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important;
}
[data-testid="stAlert"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important; color: var(--muted) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_parse_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {"parse_error": True, "raw": raw}


GEMINI_MODEL = "gemini-2.5-flash"

def call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY not set. Add it to your .env file.")
        st.stop()
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return (response.text or "").strip()


def speak_text(text: str) -> bytes:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        st.warning("ELEVENLABS_API_KEY not set — audio unavailable.")
        return b""
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio)


# ── Single combined analysis prompt ──────────────────────────────────────────

def analyze_news(text: str) -> dict:
    raw = call_gemini(f"""You are a senior financial news analyst, entity extractor, event detector, sentiment analyst, signal scorer, and investment decision advisor — all in one.

Analyze the following news text and return a SINGLE JSON object covering all aspects below.

News Text:
\"\"\"{text}\"\"\"

Respond ONLY with a JSON object (no markdown, no backticks) with exactly this structure:

{{
  "understanding": {{
    "summary": "1-2 sentence summary of the news",
    "topic": "Main topic (earnings, product launch, regulation, M&A, macro-economic, etc.)",
    "industry": "Primary industry involved",
    "relevance": "Why this matters to investors"
  }},
  "entities": {{
    "companies": ["List of company names mentioned"],
    "people": ["Key individuals mentioned"],
    "events": ["Business/financial events mentioned"],
    "indicators": ["Financial indicators mentioned (revenue, EPS, margin, etc.)"],
    "locations": ["Countries or regions if relevant"],
    "products": ["Products or services mentioned"]
  }},
  "events": {{
    "primary_event": "The single most important event",
    "event_category": "One of: earnings_report, product_launch, merger_acquisition, leadership_change, regulatory_action, market_movement, macro_event, partnership, legal_dispute, other",
    "secondary_events": ["Any additional events"],
    "event_stage": "announcement / completion / speculation / rumor",
    "time_horizon": "immediate / short_term / long_term"
  }},
  "sentiment": {{
    "overall_sentiment": "positive / negative / neutral / mixed",
    "sentiment_score": <float -1.0 to 1.0>,
    "per_company": {{
      "<company_name>": {{"sentiment": "positive/negative/neutral", "score": <float>, "reason": "Brief reason"}}
    }},
    "market_reaction_expectation": "How markets are likely to react",
    "short_term_impact": "positive / negative / neutral",
    "long_term_impact": "positive / negative / neutral / uncertain"
  }},
  "signal": {{
    "signal_strength": <integer 1-10>,
    "signal_direction": "bullish / bearish / neutral",
    "confidence": <float 0.0 to 1.0>,
    "signal_label": "strong_buy / buy / hold / sell / strong_sell",
    "volatility_expectation": "high / medium / low",
    "scoring_rationale": "2-3 sentences explaining the score"
  }},
  "decision": {{
    "decision": "strong_buy / buy / hold / sell / strong_sell / watch",
    "conviction_level": "high / medium / low",
    "key_drivers": ["2-4 key factors driving this decision"],
    "risks": ["1-3 key risks to this view"],
    "time_frame": "intraday / short_term (days) / medium_term (weeks) / long_term (months)",
    "per_company_decision": {{"<company_name>": "buy / sell / hold / watch"}},
    "action_summary": "One clear sentence: what should an investor consider doing?"
  }},
  "explanation": "3-4 sentences in plain English for a non-technical audience: what the news is about, why it generates this signal, what the recommended action is, and what risks exist."
}}""")
    return safe_parse_json(raw)


def build_time_record(text: str, result: dict) -> dict:
    signal   = result.get("signal", {})
    entities = result.get("entities", {})
    date_match = re.search(r'\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})\b', text)
    timestamp  = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp":        timestamp,
        "companies":        entities.get("companies", []),
        "signal_direction": signal.get("signal_direction", "neutral"),
        "signal_strength":  signal.get("signal_strength", 0),
        "signal_label":     signal.get("signal_label", "hold"),
        "confidence":       signal.get("confidence", 0.0),
        "tracked_at":       datetime.now().isoformat(),
    }


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-wrap">
  <div class="header-title">QuantAnalyzer.AI</div>
  <div class="header-badge">Gemini · Powered</div>
</div>
<div class="header-sub">// upload a .txt news file → run analysis → get signal strength & decision insight</div>
""", unsafe_allow_html=True)


# explanation_text = (
#        "Hi, this project is called QuantAnalyzer.AI, and it’s an AI system "
#        "that converts raw financial news into structured investment signals. "
#        "The main problem we wanted to solve is that investors often read large "
#        "amounts of news, but it’s difficult to quickly understand the real market impact. "
#        "So we built a system that uses Google Gemini large language models to automatically "
#        "analyze financial news articles. When a user uploads a news article, the system "
#        "runs it through an 8-step analysis pipeline. First it summarizes the article "
#        "and identifies the main topic and industry. Then it extracts important entities "
#        "like companies and events, detects financial events such as earnings or mergers, "
#        "and performs sentiment analysis on the potential market impact. Using this information, "
#        "the system generates a quantitative signal score from 1 to 10, determines whether the "
#        "signal is bullish, bearish, or neutral, and produces an investment recommendation like "
#        "buy, sell, hold, or watch. The results are displayed in an interactive Streamlit dashboard, "
#        "and the system also generates a human-friendly explanation of the signal. Finally, we use "
#        "ElevenLabs text-to-speech to convert the explanation into an audio summary. Overall, "
#        "the goal of this project is to demonstrate how AI can transform unstructured financial news "
#        "into actionable insights for investors."
#    )

# Generate speech
# audio_bytes2 = speak_text(explanation_text)

# st.markdown("Project Explanation Audio:")

# Play audio in the UI
# st.audio(audio_bytes2, format="audio/mp3")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your .txt news file here or click to browse",
    type=["txt"],
    label_visibility="collapsed",
)

if uploaded:
    raw = uploaded.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    text = text[:6000]

    words     = len(text.split())
    chars     = len(text)
    lines     = len(text.splitlines())
    sentences = text.count('.') + text.count('!') + text.count('?')

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">words: <span>{words:,}</span></div>
      <div class="stat-pill">chars: <span>{chars:,}</span></div>
      <div class="stat-pill">lines: <span>{lines:,}</span></div>
      <div class="stat-pill">sentences: <span>{sentences:,}</span></div>
      <div class="stat-pill">file: <span>{uploaded.name}</span></div>
    </div>
    """, unsafe_allow_html=True)

    preview = text[:700] + ("…" if len(text) > 700 else "")
    st.markdown(f'<div class="preview-box">{preview}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button("⚡  RUN SIGNAL ANALYSIS"):

        with st.spinner("Analyzing news — this will take a moment…"):
            result = analyze_news(text)
            build_time_record(text, result)

        # ── Unpack ────────────────────────────────────────────────────────────
        entities    = result.get("entities", {})
        events      = result.get("events", {})
        sentiment   = result.get("sentiment", {})
        signal      = result.get("signal", {})
        decision    = result.get("decision", {})
        explanation = result.get("explanation", "—")

        direction  = signal.get("signal_direction", "neutral").lower()
        strength   = signal.get("signal_strength", 0)
        label      = signal.get("signal_label", "hold").upper().replace("_", " ")
        confidence = int(signal.get("confidence", 0) * 100)
        sent_score = sentiment.get("sentiment_score", 0)
        sent_label = sentiment.get("overall_sentiment", "neutral").upper()
        volatility = signal.get("volatility_expectation", "—").upper()
        dec_label  = decision.get("decision", "hold").upper().replace("_", " ")
        conviction = decision.get("conviction_level", "—").upper()
        time_frame = decision.get("time_frame", "—")
        dir_emoji  = {"bullish": "▲", "bearish": "▼", "neutral": "◆"}.get(direction, "◆")

        # Signal hero
        st.markdown(f"""
        <div class="signal-hero {direction}">
          <div class="signal-hero-label">SIGNAL DIRECTION</div>
          <div class="signal-hero-direction {direction}">{dir_emoji} {direction.upper()}</div>
          <div class="signal-hero-sub">
            {label} &nbsp;·&nbsp; Strength {strength}/10 &nbsp;·&nbsp; {confidence}% confidence
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        sent_color = "var(--green)" if sent_score > 0.1 else ("var(--red)" if sent_score < -0.1 else "var(--muted)")
        st.markdown(f"""
        <div class="metric-grid">
          <div class="metric-card">
            <div class="metric-label">Sentiment Score</div>
            <div class="metric-value" style="color:{sent_color}">{sent_score:+.2f}</div>
            <div class="metric-sub">{sent_label}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Decision</div>
            <div class="metric-value">{dec_label}</div>
            <div class="metric-sub">conviction: {conviction}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Volatility</div>
            <div class="metric-value">{volatility}</div>
            <div class="metric-sub">time frame: {time_frame}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Detail cards
        companies_tags = "".join(f'<span class="tag">{c}</span>' for c in entities.get("companies", []))
        events_tags    = "".join(f'<span class="tag">{e}</span>' for e in entities.get("events", []))
        drivers_tags   = "".join(f'<span class="tag">{d}</span>' for d in decision.get("key_drivers", []))
        risks_tags     = "".join(f'<span class="tag">{r}</span>' for r in decision.get("risks", []))

        st.markdown(f"""
        <div class="section-card">
          <div class="section-title">↳ Companies & Entities</div>
          <div class="section-body">{companies_tags if companies_tags else "—"}</div>
        </div>
        <div class="section-card">
          <div class="section-title">↳ Primary Event</div>
          <div class="section-body">
            <strong>{events.get('primary_event', '—')}</strong>
            &nbsp;&nbsp;<span class="tag">{events.get('event_category', '')}</span>
            <span class="tag">{events.get('event_stage', '')}</span>
            <br><br>{events_tags}
          </div>
        </div>
        <div class="section-card">
          <div class="section-title">↳ Key Drivers</div>
          <div class="section-body">{drivers_tags if drivers_tags else "—"}</div>
        </div>
        <div class="section-card">
          <div class="section-title">↳ Risks</div>
          <div class="section-body">{risks_tags if risks_tags else "—"}</div>
        </div>
        <div class="section-card">
          <div class="section-title">↳ Signal Rationale</div>
          <div class="section-body">{signal.get('scoring_rationale', '—')}</div>
        </div>
        <div class="section-card">
          <div class="section-title">↳ Action Summary</div>
          <div class="section-body" style="font-size:1rem;font-weight:600;">{decision.get('action_summary', '—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Analyst explanation
        st.markdown(f"""
        <div class="explanation-card">
          <div class="explanation-title">// Analyst Explanation</div>
          <div class="explanation-body">{explanation.replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ElevenLabs audio
        with st.spinner("Generating audio…"):
            audio_bytes = speak_text(explanation)

        if audio_bytes:
            st.markdown('<div class="audio-label">↳ Listen to Analyst Explanation</div>', unsafe_allow_html=True)
            st.audio(audio_bytes, format="audio/mp3")

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #3a3f52; font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:0.1em;">
        NO FILE LOADED · AWAITING INPUT
    </div>
    """, unsafe_allow_html=True)

