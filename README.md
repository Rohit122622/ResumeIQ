<p align="center">
  <img src="static/favicon.svg" alt="Nexus CV Logo" width="80" height="80">
  <h1 align="center">Nexus CV</h1>
  <p align="center"><em>AI-Powered Resume Analysis & Career Intelligence Platform</em></p>
</p>

---

## Overview

**Nexus CV** is a full-stack AI-powered resume intelligence platform that analyzes resumes for ATS compatibility, generates career roadmaps, builds interview-ready resumes, and compares resume versions — all from a modern, responsive web interface.

Built with Flask, spaCy NLP, scikit-learn ML, and ReportLab PDF generation, Nexus CV demonstrates production-grade architecture patterns including OAuth 2.0, CSRF protection, rate limiting, background job scheduling, and automated email delivery.

---

## Features

| Module | Description |
|---|---|
| **Resume Analysis** | Upload a PDF resume → get ATS score, skill detection, role prediction, and AI improvement suggestions |
| **AI Resume Builder** | Fill in your details → get a professionally formatted, ATS-optimized PDF resume |
| **Resume Comparison** | Upload two resume versions → see ATS score diff, skills added/removed, and AI insight |
| **Career Roadmap** | Personalized 6-month learning plan based on detected skill gaps |
| **Job Description Match** | Paste a JD → get match percentage, matched/missing keywords |
| **Email Reports** | Auto-email PDF reports via SendGrid with SMTP fallback |
| **Auth System** | Local register/login + Google & Microsoft OAuth 2.0 |
| **Analysis History** | Track past analyses with downloadable PDF reports |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.x, Flask, Jinja2 |
| **NLP** | spaCy (`en_core_web_sm`) |
| **ML** | scikit-learn, joblib, numpy |
| **PDF** | ReportLab (generation), pdfplumber (parsing) |
| **Database** | SQLite via SQLAlchemy |
| **Auth** | Authlib (Google + Microsoft OAuth 2.0) |
| **Email** | SendGrid API + SMTP fallback |
| **Security** | Flask-WTF CSRF, Flask-Limiter, security headers |
| **Scheduling** | APScheduler (background file cleanup) |
| **Frontend** | Responsive HTML/CSS/JS with dark mode support |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Client                       │
│          (Browser — HTML/CSS/JS)                │
└───────────────────┬─────────────────────────────┘
                    │ HTTP
┌───────────────────▼─────────────────────────────┐
│              Flask Application                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Auth    │ │  CSRF    │ │  Rate Limiter    │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────────────────────────────────────┐   │
│  │           Route Handlers                 │   │
│  │  /analyze  /compare  /resume-builder     │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │  spaCy   │ │ sklearn  │ │  ReportLab     │  │
│  │  NLP     │ │ ML Model │ │  PDF Engine    │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ SQLite   │ │ SendGrid │ │  APScheduler   │  │
│  │ Database │ │ Email    │ │  Cleanup Jobs  │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## How It Works

### Resume Analysis
1. User uploads a PDF resume
2. **pdfplumber** extracts raw text
3. **spaCy** performs NLP entity/skill extraction
4. **scikit-learn** model predicts the best-fit job role
5. **ATS Scorer** calculates a composite score (skills match + keyword coverage + completeness)
6. **Career Recommender** generates a personalized 6-month roadmap
7. **ReportLab** generates a professional PDF report
8. Report is auto-emailed to the user

### Resume Builder
1. User fills in structured form data (education, experience, skills, projects)
2. Engine validates and formats the data
3. **ATS Refiner** iteratively optimizes for the target role
4. Professional PDF generated with score summary

### Resume Comparison
1. User uploads two resume versions
2. Both are independently analyzed for ATS scoring
3. Diff engine identifies skills added/removed and score changes
4. AI generates a contextual insight summary

---

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy environment config
cp .env.example .env
# Edit .env and add your keys (SECRET_KEY, SendGrid, OAuth, etc.)

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`

---

## Project Structure

```
AI_Resume_Analyzer/
├── app.py                    # Main Flask application & routes
├── resume_parser.py          # PDF text extraction
├── skill_matcher.py          # Skill matching engine
├── role_predictor.py         # ML role prediction
├── multi_role_predictor.py   # Multi-role ranking
├── ats_scorer.py             # ATS score calculator
├── career_recommender.py     # Career roadmap generator
├── jd_matcher.py             # Job description matcher
├── resume_insights.py        # Resume quality analysis
├── resume_suggestions.py     # AI improvement suggestions
├── resume_builder.py         # AI resume builder + PDF
├── pdf_generator.py          # Analysis report PDF
├── compare_pdf_generator.py  # Comparison report PDF
├── pdf_utils.py              # Shared PDF utilities
├── email_sender.py           # SendGrid + SMTP email
├── database.py               # SQLite database layer
├── cleanup.py                # Scheduled file cleanup
├── train_model.py            # ML model training script
├── templates/                # Jinja2 HTML templates
├── static/                   # CSS, JS, SVG assets
├── model/                    # Trained ML model files
├── data/                     # Training datasets
├── requirements.txt          # Python dependencies
└── .env.example              # Environment config template
```

---

## Screenshots

> _Screenshots coming soon._

---

## Author

**Rohit**

Built as an advanced AI/ML portfolio project demonstrating full-stack development, NLP, machine learning, and production-grade architecture patterns.

---

<p align="center">
  <sub>Built with ❤️ using Flask, spaCy, scikit-learn & ReportLab</sub>
</p>
