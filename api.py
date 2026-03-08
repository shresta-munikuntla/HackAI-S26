"""
api.py — FastAPI backend for News Signal Analyzer
Uses a single Gemini prompt for the full analysis pipeline.

Run:
    uvicorn api:app --reload --port 8000

Endpoints:
    POST /analyze          — full pipeline (upload .txt file)
    POST /analyze/text     — full pipeline (JSON body)
    GET  /health           — health check
"""

import json
import re
import os
import base64
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google import genai
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="News Signal Analyzer API",
    description="Financial news signal pipeline powered by a single Gemini prompt",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────

class TextBody(BaseModel):
    text: str

class FullAnalysisResponse(BaseModel):
    understanding: dict
    entities: dict
    events: dict
    sentiment: dict
    signal: dict
    time_record: dict
    decision: dict
    explanation: str
    audio_base64: Optional[str] = None


# ── Config ────────────────────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-2.5-flash"
MAX_CHARS    = 6000


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


def call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return (response.text or "").strip()


def speak_text(text: str) -> bytes:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY is not set.")
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio)


def build_time_record(text: str, result: dict) -> dict:
    signal   = result.get("signal", {})
    entities = result.get("entities", {})
    date_match = re.search(
        r'\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})\b', text
    )
    timestamp = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp":        timestamp,
        "companies":        entities.get("companies", []),
        "signal_direction": signal.get("signal_direction", "neutral"),
        "signal_strength":  signal.get("signal_strength", 0),
        "signal_label":     signal.get("signal_label", "hold"),
        "confidence":       signal.get("confidence", 0.0),
        "tracked_at":       datetime.now().isoformat(),
    }


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


# ── Internal runner ───────────────────────────────────────────────────────────

def run_pipeline(text: str) -> FullAnalysisResponse:
    text   = text[:MAX_CHARS]
    result = analyze_news(text)

    understanding = result.get("understanding", {})
    entities      = result.get("entities", {})
    events        = result.get("events", {})
    sentiment     = result.get("sentiment", {})
    signal        = result.get("signal", {})
    decision      = result.get("decision", {})
    explanation   = result.get("explanation", "")
    time_record   = build_time_record(text, result)

    audio_bytes = speak_text(explanation)
    audio_b64   = base64.b64encode(audio_bytes).decode("utf-8")

    return FullAnalysisResponse(
        understanding=understanding,
        entities=entities,
        events=events,
        sentiment=sentiment,
        signal=signal,
        time_record=time_record,
        decision=decision,
        explanation=explanation,
        audio_base64=audio_b64,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health():
    return {"status": "ok", "model": GEMINI_MODEL}


@app.post("/analyze", response_model=FullAnalysisResponse, tags=["Pipeline"])
async def analyze_file(file: UploadFile = File(...)):
    """Upload a .txt news file and run the full signal analysis pipeline."""
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are accepted.")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return run_pipeline(text)


@app.post("/analyze/text", response_model=FullAnalysisResponse, tags=["Pipeline"])
def analyze_text(body: TextBody):
    """Send raw news text as a JSON body and run the full signal analysis pipeline."""
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="text field must not be empty.")
    return run_pipeline(body.text)