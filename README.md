<p align="center">
  <img src="static/favicon.svg" alt="ResumeIQ Logo" width="80" height="80">
  <h1 align="center">ResumeIQ</h1>
  <p align="center">
    <strong>AI-Powered Resume Analysis, Building & Career Intelligence Platform</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#installation">Installation</a> •
    <a href="#deployment">Deployment</a> •
    <a href="#license">License</a>
  </p>
</p>

---

> **Live Demo:** _Coming soon_

## Overview

ResumeIQ is a full-stack AI-powered resume intelligence platform that analyzes resumes for ATS compatibility, generates career roadmaps, builds interview-ready resumes, and compares resume versions — all from a modern, responsive web interface.

Built as a production-grade Flask SaaS application with security hardening, email automation, and deployment infrastructure included.

---

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **ATS Scoring Engine** | Scores resumes against job descriptions using NLP-based keyword matching and formatting analysis |
| 📝 **AI Resume Builder** | Multi-section form that generates ATS-optimized, recruiter-friendly PDFs with AI refinement |
| 🔄 **Resume Comparison** | Upload two versions of a resume to track ATS improvement with side-by-side scoring and charts |
| 📧 **Email Automation** | SendGrid API with SMTP fallback — automatically emails analysis reports as PDF attachments |
| 🗺️ **Dynamic Career Roadmap** | Predicts career paths, recommends skills, and generates personalized upskilling guides |
| 📊 **PDF Report Generation** | Professionally formatted PDF reports with scores, charts, and actionable insights |
| 🔒 **Security Hardening** | CSRF protection, rate limiting, session security, Content Security Policy headers |
| 🚀 **Production Ready** | Gunicorn config, Nginx reverse proxy, CI/CD pipeline, environment-based configuration |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+, Flask 3.1 |
| **NLP** | spaCy (skill extraction, text analysis) |
| **PDF** | ReportLab (generation), pdfplumber (parsing) |
| **Auth** | Authlib (Google OAuth, Microsoft OAuth), Flask sessions |
| **Email** | SendGrid API, Gmail SMTP fallback |
| **Security** | Flask-WTF (CSRF), Flask-Limiter (rate limiting), Flask-Compress (gzip) |
| **Database** | SQLite (users, analysis history) |
| **Frontend** | Vanilla HTML/CSS/JS, Chart.js, responsive design |
| **Deploy** | Gunicorn, Nginx, GitHub Actions CI/CD |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Nginx (443/80)                   │
│              Reverse Proxy + SSL + Static            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               Gunicorn (WSGI Server)                 │
│              Workers: 2 × CPU + 1                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  Flask Application                   │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐ │
│  │ Analyze │ │ Compare  │ │  Builder  │ │  Auth  │ │
│  └────┬────┘ └────┬─────┘ └─────┬─────┘ └────┬───┘ │
│       │           │             │             │      │
│  ┌────▼───────────▼─────────────▼─────────────▼───┐ │
│  │   spaCy NLP · ATS Scorer · PDF Generator       │ │
│  │   Career Recommender · Email Sender             │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  SQLite (users.db) │
              └─────────────────┘
```

---

## Folder Structure

```
AI_Resume_Analyzer/
├── app.py                      # Main Flask application (routes, middleware, config)
├── database.py                 # SQLite connection and table creation
├── resume_parser.py            # PDF resume text extraction
├── skill_matcher.py            # NLP-based skill matching
├── ats_scorer.py               # ATS compatibility scoring engine
├── role_predictor.py           # ML-based role prediction
├── multi_role_predictor.py     # Multi-role career prediction
├── career_recommender.py       # Career path and roadmap generation
├── jd_matcher.py               # Job description matching
├── resume_builder.py           # AI resume builder logic and PDF generation
├── resume_insights.py          # Resume quality insights
├── resume_suggestions.py       # Improvement suggestions engine
├── pdf_generator.py            # Analysis report PDF generation
├── pdf_utils.py                # PDF helper utilities
├── compare_pdf_generator.py    # Comparison report PDF generation
├── email_sender.py             # SendGrid + SMTP email sender
├── cleanup.py                  # Scheduled file cleanup (APScheduler)
├── train_model.py              # ML model training script
├── gunicorn_config.py          # Gunicorn production configuration
├── nginx.conf                  # Nginx reverse proxy configuration
├── requirements.txt            # Pinned Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
│
├── templates/                  # Jinja2 HTML templates (12 pages)
│   ├── home.html
│   ├── login.html / register.html
│   ├── upload.html / result.html
│   ├── compare.html / compare_result.html
│   ├── resume_builder.html / resume_preview.html
│   ├── history.html
│   └── 404.html / 500.html
│
├── static/                     # CSS, JS, SVG assets
│   ├── style.css               # Full design system (dark/light modes)
│   ├── script.js / theme.js
│   └── favicon.svg / google.svg / resumeiq-logo.svg
│
├── data/                       # Static reference data
│   ├── skills.txt
│   ├── job_roles.json
│   └── career_paths.json
│
├── model/                      # Pre-trained ML models
│   ├── role_model.pkl
│   └── vectorizer.pkl
│
└── .github/workflows/
    └── deploy.yml              # CI/CD pipeline
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy language model
python -m spacy download en_core_web_sm

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your actual credentials

# 6. Run the application
python app.py
```

The app will be available at `http://localhost:5000`.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** (prod) | Flask session encryption key. **Must be set in production.** |
| `FLASK_ENV` | No | `development` (default) or `production` |
| `PORT` | No | Server port (default: `5000`) |
| `SENDGRID_API_KEY` | No | SendGrid API key for email delivery |
| `SENDGRID_FROM_EMAIL` | No | Sender email for SendGrid |
| `EMAIL_USER` | No | Gmail address for SMTP fallback |
| `EMAIL_PASS` | No | Gmail app password for SMTP fallback |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret |
| `MICROSOFT_CLIENT_ID` | No | Microsoft OAuth client ID |
| `MICROSOFT_CLIENT_SECRET` | No | Microsoft OAuth client secret |

---

## Deployment

### Production (Gunicorn + Nginx)

```bash
# 1. Install production dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Set SECRET_KEY, FLASK_ENV=production, and other secrets

# 3. Start Gunicorn
gunicorn -c gunicorn_config.py app:app

# 4. Configure Nginx
# Copy nginx.conf to /etc/nginx/sites-available/
# Update server_name and SSL certificate paths
# Enable the site and reload Nginx
```

### Render / Cloud Platforms

The app reads `PORT` from environment automatically:

```python
port = int(os.getenv("PORT", 5000))
app.run(host="0.0.0.0", port=port)
```

Gunicorn entry point: `app:app`

---

## Security Highlights

- **CSRF Protection** — All POST forms protected via Flask-WTF `CSRFProtect`
- **Rate Limiting** — `/analyze` (10/min), `/generate-resume` (5/min), `/compare-analyze` (5/min)
- **Session Security** — `HttpOnly`, `SameSite=Lax`, `Secure` (production)
- **Security Headers** — `X-Frame-Options`, `X-Content-Type-Options`, `CSP`, `HSTS`
- **Secret Management** — Environment variables via `.env`, no hardcoded secrets
- **File Cleanup** — Automated deletion of old uploads and reports (APScheduler)
- **Error Handling** — Custom 404/500 pages, no traceback leaks in production

---

## Screenshots

> _Screenshots coming soon_

<!-- 
![Home Page](screenshots/home.png)
![Analysis Result](screenshots/result.png)
![Resume Builder](screenshots/builder.png)
-->

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ by <strong>Rohit</strong>
</p>
