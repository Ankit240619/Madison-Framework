# Madison Transparency Agent

An AI-powered KPI anomaly detection and executive reporting dashboard built with Streamlit. This application replicates the Madison Transparency Agent n8n workflow, providing CPU utilization anomaly detection correlated with real-time tech news.

## What It Does

1. **Fetches CPU utilization metrics** from the Numenta Anomaly Benchmark (NAB) dataset
2. **Aggregates tech news** from TechCrunch RSS, VentureBeat AI RSS, and NewsAPI
3. **Computes statistics** (average, min, max, standard deviation) and anomaly thresholds
4. **Uses GPT-4o-mini** to classify anomalies as CRITICAL / HIGH / MEDIUM
5. **Generates an executive summary** with actionable recommendations
6. **Outputs downloadable reports** in HTML, JSON, and Markdown formats

## Tech Stack

- **Workflow Logic:** Ported from n8n automation workflow
- **AI Model:** OpenAI GPT-4o-mini (anomaly classification + insight narration)
- **Frontend:** Streamlit with Plotly charts
- **Data:** Pandas for processing, feedparser for RSS

## Live Demo

**[madison-framework-xselbtfvfdctrdgkv5fkem.streamlit.app](https://madison-framework-xselbtfvfdctrdgkv5fkem.streamlit.app/)**

## Local Setup

### Prerequisites

- Python 3.9+
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- A NewsAPI key ([get one here](https://newsapi.org/register)) — optional

### Installation

```bash
# Clone the repository
git clone https://github.com/Ankit240619/Madison-Framework.git
cd Madison-Framework

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configure Secrets

Edit `.streamlit/secrets.toml` with your API keys:

```toml
OPENAI_API_KEY = "sk-..."
NEWSAPI_KEY = "37899573a8cb4c98b3ef4349cacb1e03"
```

> **Note:** This file is in `.gitignore` and will not be committed.

### Run

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Deploy to Streamlit Cloud

1. Push this repository to GitHub (the `secrets.toml` file is excluded by `.gitignore`).
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub.
3. Click **New app** → select this repo → set `app.py` as the main file.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   NEWSAPI_KEY = "your-key-here"
   ```
5. Click **Deploy**. Your app will be live at a public URL.

## Project Structure

```
Madison-Framework/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── .streamlit/
│   ├── config.toml         # Streamlit theme configuration
│   └── secrets.toml        # Local API keys (not committed)


```

## Author

**Ankit Deopurkar**

---

*Built for Assignment 5 — Madison Transparency Agent*
