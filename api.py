import os
from google import genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="AI Text Analyzer API", version="1.0.0")

# Allow Streamlit (running on any localhost port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

ANALYSES = {
    "summarize": (
        "You are an expert summarizer. Produce a concise, well-structured summary of the provided text. "
        "Highlight the main ideas and key points in 3–5 sentences.",
        "Please summarize this text:\n\n{text}",
    ),
    "sentiment": (
        "You are a sentiment analysis expert. Analyze the emotional tone of the text. "
        "State the overall sentiment (Positive / Neutral / Negative), provide a confidence level, "
        "and briefly explain the key signals you found.",
        "Analyze the sentiment of this text:\n\n{text}",
    ),
    "key_themes": (
        "You are a thematic analysis expert. Identify and explain the 3–5 main themes or topics "
        "present in the text. Format each theme as a short title followed by a one-sentence explanation.",
        "Identify the key themes in this text:\n\n{text}",
    ),
    "qa_pairs": (
        "You are an educational content creator. Generate 5 insightful question-and-answer pairs "
        "based on the text. Each pair should test comprehension of an important concept.",
        "Generate Q&A pairs from this text:\n\n{text}",
    ),
    "writing_style": (
        "You are a writing style critic. Analyze the writing style: tone, vocabulary level, sentence "
        "structure, clarity, and intended audience. Be specific and constructive.",
        "Analyze the writing style of this text:\n\n{text}",
    ),
    "translate_es": (
        "You are a professional translator. Translate the text into Spanish, preserving the original "
        "tone and meaning as closely as possible.",
        "Translate this text to Spanish:\n\n{text}",
    ),
}


class AnalyzeRequest(BaseModel):
    analysis_type: str   # one of the ANALYSES keys
    text: str


class AnalyzeResponse(BaseModel):
    result: str


def call_gemini(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment / .env file")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=f"{system_prompt}\n\n{user_content}"
    )
    return response.text


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Text Analyzer API is running"}


@app.get("/analyses")
def list_analyses():
    """Return the list of supported analysis types."""
    return {"analyses": list(ANALYSES.keys())}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if req.analysis_type not in ANALYSES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown analysis_type '{req.analysis_type}'. "
                   f"Valid options: {list(ANALYSES.keys())}",
        )
    system_prompt, user_template = ANALYSES[req.analysis_type]
    user_prompt = user_template.format(text=req.text[:6000])  # trim to avoid token overrun
    try:
        result = call_gemini(system_prompt, user_prompt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {e}")
    return AnalyzeResponse(result=result)
