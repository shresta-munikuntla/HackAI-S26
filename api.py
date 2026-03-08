"""
api.py — FastAPI backend for News Signal Analyzer
Mirrors the 8-step Gemini pipeline from app.py as REST endpoints.

Run:
    uvicorn api:app --reload --port 8000

Endpoints:
    POST /analyze          — full 8-step pipeline (upload .txt or send JSON body)
    POST /analyze/step/{n} — run a single step (1-8) for debugging
    GET  /health           — health check
"""

import json
import re
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google import genai
from dotenv import load_dotenv

load_dotenv()

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="News Signal Analyzer API",
    description="8-step financial news signal pipeline powered by Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ───────────────────────────────────────────────────────────

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


# ── Gemini helpers ────────────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"
MAX_CHARS = 6000


def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set.",
        )
    return genai.Client(api_key=api_key)


def call_gemini(prompt: str) -> str:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()


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


# ── 8-Step pipeline functions (identical logic to app.py) ─────────────────────

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
    date_match = re.search(
        r'\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})\b', text
    )
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


def step8_explanation(
    understanding: dict, entities: dict, events: dict,
    sentiment: dict, signal: dict, decision: dict,
) -> str:
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


# ── Internal runner ───────────────────────────────────────────────────────────

def run_full_pipeline(text: str) -> FullAnalysisResponse:
    text = text[:MAX_CHARS]

    understanding = step1_understand(text)
    entities      = step2_entities(text)
    events        = step3_events(text)
    sentiment     = step4_sentiment(text, entities)
    signal        = step5_signal(text, sentiment, events)
    time_record   = step6_time_record(text, signal, entities)
    decision      = step7_decision(entities, sentiment, signal, events)
    explanation   = step8_explanation(understanding, entities, events, sentiment, signal, decision)

    return FullAnalysisResponse(
        understanding=understanding,
        entities=entities,
        events=events,
        sentiment=sentiment,
        signal=signal,
        time_record=time_record,
        decision=decision,
        explanation=explanation,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health():
    """Simple health check."""
    return {"status": "ok", "model": GEMINI_MODEL}


@app.post("/analyze", response_model=FullAnalysisResponse, tags=["Pipeline"])
async def analyze_file(file: UploadFile = File(...)):
    """
    Upload a .txt news file and run the full 8-step signal pipeline.
    Returns structured JSON with all intermediate step results plus the final explanation.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are accepted.")

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    return run_full_pipeline(text)


@app.post("/analyze/text", response_model=FullAnalysisResponse, tags=["Pipeline"])
def analyze_text(body: TextBody):
    """
    Send raw news text as a JSON body and run the full 8-step signal pipeline.

    Body: { "text": "..." }
    """
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="text field must not be empty.")
    return run_full_pipeline(body.text)


@app.post("/analyze/step/{step_number}", tags=["Debug"])
def analyze_single_step(
    step_number: int,
    body: TextBody,
    sentiment_score: Optional[float] = Query(default=0.0),
    overall_sentiment: Optional[str] = Query(default="neutral"),
    primary_event: Optional[str] = Query(default="unknown"),
    event_category: Optional[str] = Query(default="other"),
):
    """
    Run a single pipeline step (1–8) for debugging purposes.

    Steps 4–8 may need context from earlier steps; pass optional query params
    or use /analyze for the full chained run.
    """
    text = body.text[:MAX_CHARS]

    if step_number == 1:
        return step1_understand(text)

    elif step_number == 2:
        return step2_entities(text)

    elif step_number == 3:
        return step3_events(text)

    elif step_number == 4:
        entities = step2_entities(text)
        return step4_sentiment(text, entities)

    elif step_number == 5:
        mock_sentiment = {"sentiment_score": sentiment_score, "overall_sentiment": overall_sentiment}
        mock_events    = {"primary_event": primary_event, "event_category": event_category}
        return step5_signal(text, mock_sentiment, mock_events)

    elif step_number == 6:
        entities   = step2_entities(text)
        sentiment  = step4_sentiment(text, entities)
        events     = step3_events(text)
        signal     = step5_signal(text, sentiment, events)
        return step6_time_record(text, signal, entities)

    elif step_number == 7:
        entities  = step2_entities(text)
        sentiment = step4_sentiment(text, entities)
        events    = step3_events(text)
        signal    = step5_signal(text, sentiment, events)
        return step7_decision(entities, sentiment, signal, events)

    elif step_number == 8:
        understanding = step1_understand(text)
        entities      = step2_entities(text)
        events        = step3_events(text)
        sentiment     = step4_sentiment(text, entities)
        signal        = step5_signal(text, sentiment, events)
        decision      = step7_decision(entities, sentiment, signal, events)
        return {"explanation": step8_explanation(understanding, entities, events, sentiment, signal, decision)}

    else:
        raise HTTPException(status_code=400, detail="step_number must be between 1 and 8.")
