# QuantAnalyzer.AI 📡
**Gemini-Powered Financial News Signal Analyzer**

QuantAnalyzer.AI is an AI-powered financial news analysis system that converts raw news articles into **structured investment signals**.

By combining **Google Gemini LLMs**, **FastAPI**, **Streamlit**, and **ElevenLabs voice synthesis**, the system analyzes financial news through an **8-step intelligence pipeline** and produces:

- Market sentiment
- Signal strength
- Investment decision recommendations
- Natural language explanations
- Audio summaries

The goal is to help investors **quickly interpret financial news and understand potential market signals.**

---

# 🚀 Features

## AI-Powered News Intelligence
- Extracts companies, people, events, and indicators
- Detects financial events (earnings, M&A, regulation, etc.)
- Performs sentiment analysis on market impact

## Quantitative Signal Scoring
- Generates **signal strength scores (1–10)**
- Determines **bullish / bearish / neutral** signals
- Produces **buy / sell / hold / watch** recommendations

## Investor-Focused Insights
- Key drivers behind the signal
- Potential risks
- Expected market volatility
- Suggested investment timeframe

## Voice Explanation
Using **ElevenLabs**, the system converts the AI explanation into an **audio summary**.

## Dual Interface

| Interface | Purpose |
|-----------|---------|
| **Streamlit App** | Interactive dashboard |
| **FastAPI Backend** | REST API for programmatic access |

---

# 🧠 8-Step Analysis Pipeline

Every news article goes through the following AI pipeline:

| Step | Stage | Purpose |
|-----|------|---------|
| 1 | Understanding | Summarizes the article and identifies topic & industry |
| 2 | Entity Extraction | Detects companies, people, indicators, locations |
| 3 | Event Detection | Identifies financial events (earnings, M&A, regulation) |
| 4 | Sentiment Analysis | Evaluates market sentiment and company impact |
| 5 | Signal Scoring | Generates signal strength and direction |
| 6 | Time Tracking | Records timestamps and signal metadata |
| 7 | Decision Engine | Produces investment recommendation |
| 8 | Explanation | Writes a human-friendly analyst explanation |

---

# 🏗 System Architecture

```
                +----------------------+
                |   Financial News     |
                |     (.txt file)      |
                +----------+-----------+
                           |
                           v
                  Streamlit Dashboard
                           |
                           v
                    Gemini LLM API
                           |
                           v
                8-Step Analysis Pipeline
                           |
                           v
         +----------------------------------+
         | Structured Financial Signal      |
         | - Sentiment Score                |
         | - Signal Strength                |
         | - Buy/Sell Recommendation        |
         | - Risk Factors                   |
         +----------------------------------+
                           |
                           v
                ElevenLabs Voice Summary
```

---

# 📁 Project Structure

```
QuantAnalyzer-AI/
│
├── app.py          # Streamlit interactive dashboard
├── api.py          # FastAPI backend with REST endpoints
├── .env            # Environment variables (not committed)
├── news.txt        # Example input file
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/QuantAnalyzer-AI.git
cd QuantAnalyzer-AI
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit fastapi uvicorn python-dotenv google-generativeai elevenlabs
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Get API keys

Gemini API:  
https://ai.google.dev/

ElevenLabs:  
https://elevenlabs.io/

---

# 🖥 Running the Streamlit Dashboard

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

### Dashboard Workflow

1. Upload a `.txt` financial news article
2. Run the **8-step analysis pipeline**
3. View:
   - Signal direction
   - Sentiment score
   - Investment recommendation
   - Risk factors
4. Listen to the **AI-generated audio explanation**

---

# 🔌 Running the FastAPI Backend

Start the API server:

```bash
uvicorn api:app --reload --port 8000
```

API documentation automatically appears at:

```
http://localhost:8000/docs
```

# 🛠 Technologies Used

| Technology | Purpose |
|-----------|--------|
| **Google Gemini API** | LLM reasoning & structured analysis |
| **FastAPI** | Backend API service |
| **Streamlit** | Interactive dashboard UI |
| **ElevenLabs** | Text-to-speech explanations |
| **Python** | Core application logic |

---

# 🎯 Use Cases

- Financial news intelligence
- Market sentiment tracking
- Quantitative trading signals
- AI-powered analyst reports
- Hackathon AI demo projects

---

# ⚠️ Disclaimer

This project is for **educational and research purposes only**.

The signals generated by the system **should not be considered financial advice**.

---

# 👩‍💻 Author

**Shresta Munikuntla**

**Sadwitha Thopucharla**

**Jaya Vardhini Akurathi**

**Siddhaarth Balamuthaiya**
