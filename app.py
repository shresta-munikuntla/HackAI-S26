import streamlit as st
import json
import re
import os
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

/* ── Step progress ── */
.step-bar { display: flex; gap: 6px; margin: 1.5rem 0 0.5rem; flex-wrap: wrap; }
.step-dot {
    font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.08em;
    padding: 3px 10px; border-radius: 20px; border: 1px solid var(--border);
    color: var(--muted); text-transform: uppercase;
}
.step-dot.done   { border-color: var(--accent);  color: var(--accent); }
.step-dot.active { border-color: var(--accent2); color: var(--accent2); background: rgba(71,197,255,0.07); }

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


# ── Pipeline helpers ──────────────────────────────────────────────────────────

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


GEMINI_MODEL = "gemini-3-flash-preview"

def call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY not set. Run: export GEMINI_API_KEY='your_key_here'")
        st.stop()
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()

# ── Text to Speech ───────────────────────────────────────────────────────────
def speak_text(text: str):
    client = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )

    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    audio_bytes = b"".join(audio)

    return audio_bytes

# ── 8-Step Pipeline ───────────────────────────────────────────────────────────

def step1_understand(text: str) -> dict:
    raw = call_gemini(f"""You are a financial news analyst. Read the following news text and provide a structured understanding.

News Text:
\"\"\"{text}\"\"\"

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "summary": "A 1-2 sentence summary",
  "topic": "Main topic (earnings, product launch, regulation, M&A, macro-economic, etc.)",
  "industry": "Primary industry involved",
  "relevance": "Why this matters to investors"
}}""")
    return safe_parse_json(raw)


def step2_entities(text: str) -> dict:
    raw = call_gemini(f"""You are a financial entity extractor. Extract all important entities from the news below.

News Text:
\"\"\"{text}\"\"\"

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "companies": ["List of company names"],
  "people": ["Key individuals"],
  "events": ["Business/financial events"],
  "indicators": ["Financial indicators (revenue, EPS, margin, etc.)"],
  "locations": ["Countries or regions if relevant"],
  "products": ["Products or services mentioned"]
}}""")
    return safe_parse_json(raw)


def step3_events(text: str) -> dict:
    raw = call_gemini(f"""You are a financial event detector. Identify the specific business/financial event(s) in the news below.

News Text:
\"\"\"{text}\"\"\"

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "primary_event": "The single most important event",
  "event_category": "One of: earnings_report, product_launch, merger_acquisition, leadership_change, regulatory_action, market_movement, macro_event, partnership, legal_dispute, other",
  "secondary_events": ["Any additional events"],
  "event_stage": "announcement / completion / speculation / rumor",
  "time_horizon": "immediate / short_term / long_term"
}}""")
    return safe_parse_json(raw)


def step4_sentiment(text: str, entities: dict) -> dict:
    companies = ", ".join(entities.get("companies", ["the company"]))
    raw = call_gemini(f"""You are a financial sentiment analyst. Analyze the sentiment of the following news for: {companies}

News Text:
\"\"\"{text}\"\"\"

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "overall_sentiment": "positive / negative / neutral / mixed",
  "sentiment_score": <float -1.0 to 1.0>,
  "per_company": {{
    "<company_name>": {{"sentiment": "positive/negative/neutral", "score": <float>, "reason": "Brief reason"}}
  }},
  "market_reaction_expectation": "How markets are likely to react",
  "short_term_impact": "positive / negative / neutral",
  "long_term_impact": "positive / negative / neutral / uncertain"
}}""")
    return safe_parse_json(raw)


def step5_signal(text: str, sentiment: dict, events: dict) -> dict:
    raw = call_gemini(f"""You are a quantitative financial signal scorer. Score the signal strength based on the analysis below.

News Text:
\"\"\"{text}\"\"\"

Sentiment Score: {sentiment.get('sentiment_score', 0)}
Overall Sentiment: {sentiment.get('overall_sentiment', 'unknown')}
Primary Event: {events.get('primary_event', 'unknown')}
Event Category: {events.get('event_category', 'unknown')}

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "signal_strength": <integer 1-10>,
  "signal_direction": "bullish / bearish / neutral",
  "confidence": <float 0.0 to 1.0>,
  "signal_label": "strong_buy / buy / hold / sell / strong_sell",
  "volatility_expectation": "high / medium / low",
  "scoring_rationale": "2-3 sentences explaining the score"
}}""")
    return safe_parse_json(raw)


def step6_time_record(text: str, signal: dict, entities: dict) -> dict:
    date_match = re.search(r'\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})\b', text)
    timestamp = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
        "companies": entities.get("companies", []),
        "signal_direction": signal.get("signal_direction", "neutral"),
        "signal_strength": signal.get("signal_strength", 0),
        "signal_label": signal.get("signal_label", "hold"),
        "confidence": signal.get("confidence", 0.0),
        "tracked_at": datetime.now().isoformat(),
    }


def step7_decision(entities: dict, sentiment: dict, signal: dict, events: dict) -> dict:
    companies = ", ".join(entities.get("companies", ["Unknown"]))
    raw = call_gemini(f"""You are a financial decision support system. Synthesize these signals into a clear investment decision.

Companies: {companies}
Primary Event: {events.get('primary_event', 'N/A')}
Event Category: {events.get('event_category', 'N/A')}
Sentiment: {sentiment.get('overall_sentiment', 'N/A')} (score: {sentiment.get('sentiment_score', 0)})
Short-term Impact: {sentiment.get('short_term_impact', 'N/A')}
Long-term Impact: {sentiment.get('long_term_impact', 'N/A')}
Signal Direction: {signal.get('signal_direction', 'N/A')}
Signal Strength: {signal.get('signal_strength', 0)}/10
Signal Label: {signal.get('signal_label', 'N/A')}
Confidence: {signal.get('confidence', 0)}

Respond ONLY with a JSON object (no markdown, no backticks):
{{
  "decision": "strong_buy / buy / hold / sell / strong_sell / watch",
  "conviction_level": "high / medium / low",
  "key_drivers": ["2-4 key factors"],
  "risks": ["1-3 key risks"],
  "time_frame": "intraday / short_term (days) / medium_term (weeks) / long_term (months)",
  "per_company_decision": {{"<company_name>": "buy / sell / hold / watch"}},
  "action_summary": "One clear sentence: what should an investor consider doing?"
}}""")
    return safe_parse_json(raw)


def step8_explanation(understanding: dict, entities: dict, events: dict,
                       sentiment: dict, signal: dict, decision: dict) -> str:
    companies = ", ".join(entities.get("companies", ["the company"]))
    return call_gemini(f"""You are a financial analyst writing for a non-technical audience.
Write a clear, concise 3-4 sentence paragraph explaining:
1. What the news is about
2. Why it generates this signal
3. What the recommended action/watch is
4. What risks exist

Original Summary: {understanding.get('summary', '')}
Companies: {companies}
Event: {events.get('primary_event', 'N/A')}
Sentiment: {sentiment.get('overall_sentiment', 'N/A')}
Signal: {signal.get('signal_direction', 'N/A')} — strength {signal.get('signal_strength', 0)}/10
Decision: {decision.get('decision', 'N/A')}
Key Drivers: {', '.join(decision.get('key_drivers', []))}
Risks: {', '.join(decision.get('risks', []))}

Plain English only. No bullets. No headers. Just a clear paragraph.""")


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-wrap">
  <div class="header-title">QuantAnalyzer.AI</div>
  <div class="header-badge">Gemini · Powered</div>
</div>
<div class="header-sub">// upload a .txt news file → run the 8-step pipeline → get signal strength & decision insight</div>
""", unsafe_allow_html=True)

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

    text = text[:6000]  # cap to avoid token overrun

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

        STEPS = ["Understanding", "Entities", "Events", "Sentiment",
                 "Signal Score", "Timestamp", "Decision", "Explanation"]
        step_placeholder = st.empty()

        def render_steps(done_up_to: int, active: int):
            dots = ""
            for i, s in enumerate(STEPS):
                cls = "done" if i < done_up_to else ("active" if i == active else "")
                dots += f'<div class="step-dot {cls}">{s}</div>'
            step_placeholder.markdown(f'<div class="step-bar">{dots}</div>', unsafe_allow_html=True)

        render_steps(0, 0)
        with st.spinner("Step 1 · Understanding text…"):
            understanding = step1_understand(text)
        render_steps(1, 1)

        with st.spinner("Step 2 · Identifying entities…"):
            entities = step2_entities(text)
        render_steps(2, 2)

        with st.spinner("Step 3 · Detecting events…"):
            events = step3_events(text)
        render_steps(3, 3)

        with st.spinner("Step 4 · Analyzing sentiment…"):
            sentiment = step4_sentiment(text, entities)
        render_steps(4, 4)

        with st.spinner("Step 5 · Scoring signal strength…"):
            signal = step5_signal(text, sentiment, events)
        render_steps(5, 5)

        with st.spinner("Step 6 · Recording timestamp…"):
            time_record = step6_time_record(text, signal, entities)
        render_steps(6, 6)

        with st.spinner("Step 7 · Generating decision insight…"):
            decision = step7_decision(entities, sentiment, signal, events)
        render_steps(7, 7)

        with st.spinner("Step 8 · Writing analyst explanation…"):
            explanation = step8_explanation(understanding, entities, events, sentiment, signal, decision)

        # Generate speech
        audio_bytes = speak_text(explanation)

        # Play audio in the UI
        st.audio(audio_bytes, format="audio/mp3")

        render_steps(8, -1)

        # ── Results ──────────────────────────────────────────────────────────
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

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #3a3f52; font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:0.1em;">
        NO FILE LOADED · AWAITING INPUT
    </div>
    """, unsafe_allow_html=True)