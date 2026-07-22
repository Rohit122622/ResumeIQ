<img width="1915" height="1127" alt="image" src="https://github.com/user-attachments/assets/d3929077-046d-4d99-8219-c63258a973f2" /><p align="center">
  <img src="frontend/static/nexuscv-logo.svg" alt="Nexus CV Logo" width="96" height="96">
</p>

<h1 align="center">Nexus CV</h1>

<p align="center">
  <strong>AI-Powered Resume Intelligence & Candidate Screening Platform</strong>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://flask.palletsprojects.com"><img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"></a>
  <a href="#"><img src="https://img.shields.io/badge/XGBoost-ML_Scoring-FF6600?style=flat-square" alt="XGBoost"></a>
  <a href="#"><img src="https://img.shields.io/badge/FAISS-Vector_Search-FF6F61?style=flat-square" alt="FAISS"></a>
  <a href="#"><img src="https://img.shields.io/badge/spaCy-NLP-09A3D5?style=flat-square" alt="spaCy"></a>
  <a href="#"><img src="https://img.shields.io/badge/RAG-BGE_large-8A2BE2?style=flat-square" alt="RAG"></a>
  <a href="#"><img src="https://img.shields.io/badge/LLM-6_Provider_Fallback-008080?style=flat-square" alt="LLM Fallback"></a>
  <a href="#"><img src="https://img.shields.io/badge/n8n-Workflow_Engine-EA4B71?style=flat-square&logo=n8n&logoColor=white" alt="n8n"></a>
  <a href="#"><img src="https://img.shields.io/badge/Auth-Google_OAuth-4285F4?style=flat-square&logo=google&logoColor=white" alt="OAuth"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-4CAF50?style=flat-square" alt="MIT License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status"></a>
</p>

<p align="center">
  Nexus CV is a modular, AI-powered platform for resume analysis, ATS scoring, semantic job-description matching, bulk candidate screening, and AI-assisted proposal generation — built on a 6-agent pipeline, hybrid ML scoring, and a resilient 6-provider LLM fallback chain.
</p>

<br>

## 🚀 Project Highlights

- 🤖 6-Agent AI Recruitment Pipeline
- 📄 AI Resume Analyzer with ATS Scoring
- 📊 Bulk Resume Screening & Candidate Ranking
- 🧠 Recruiter AI Copilot (Natural Language Q&A)
- 🔍 Semantic Resume–JD Matching using FAISS + BGE
- 📈 Hybrid ML Ranking (XGBoost + AI + RAG)
- 🔄 Resume Comparison Engine
- 📑 PDF, CSV & JSON Report Generation
- 🔐 Google OAuth Authentication
- ⚡ Multi-LLM Fallback Architecture

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [AI Pipeline](#ai-pipeline)
- [Multi-Agent System](#multi-agent-system)
- [Recruiter AI Copilot](#recruiter-ai-copilot)
- [Hybrid Scoring Engine](#hybrid-scoring-engine)
- [Bulk Resume Screening](#bulk-resume-screening)
- [Resume Comparison](#resume-comparison)
- [Resume Analysis](#resume-analysis)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Performance Notes](#performance-notes)
- [Security](#security)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

<br>

## Project Overview

Nexus CV addresses a real gap in resume tooling: most ATS tools are either pure keyword matchers or fragile single-prompt LLM wrappers. Nexus CV combines both approaches into a hybrid pipeline that is more reliable and analytically richer than either alone.

The platform is built around three core ideas:

**Hybrid scoring** — XGBoost ML predictions, TF-IDF keyword density, semantic BGE-large embeddings, and rule-based heuristics are combined into a single weighted ranking signal rather than relying on any one method.

**Multi-agent reasoning** — Six specialist agents (Skill, Experience, ATS, Decision, Behavioral, Platform Activity) each evaluate a distinct dimension of the candidate, then the Decision Agent synthesizes their outputs using a ReAct reasoning loop with direct evidence quotes from the resume.

**Resilient LLM infrastructure** — A 6-provider fallback chain (Gemini → Groq → OpenAI → Claude → DeepSeek → Qwen → local rules) with thread-safe throttling ensures AI features remain available even under quota exhaustion or API outages.

<br>

## Key Features

| Area | Feature |
|------|---------|
| **Analysis** | ATS Score Prediction, Semantic JD Matching, Role Prediction, Missing Skills Detection |
| **AI Agents** | 6-Agent Pipeline — Skill, Experience, ATS, Decision, Behavioral, Platform Activity |
| **Recruiter Tools** | Recruiter AI Copilot, Natural Language Candidate Q&A, Comparison Explanations |
| **Bulk Screening** | ZIP Upload, Multi-Agent Parallel Analysis, 7-Signal Hybrid Ranking, Shortlisting |
| **Resume Tools** | Resume Builder, Resume Comparison (diff + gap analysis), ATS-Optimized Rewriting |
| **Roadmap** | Career Roadmap Generation, Role Prediction, Improvement Suggestions |
| **Reports** | PDF Report Generation, CSV Export, JSON Export, Auto-Email via SendGrid |
| **LLM Stack** | Gemini, Groq, OpenAI, Claude, DeepSeek, Qwen, Local Rule Fallback |
| **Infrastructure** | n8n Workflow Orchestration, Google OAuth, Dark Mode UI, Dashboard Analytics |

<br>

# 🎥 Demo

## Live Demo

Coming Soon

---

## Demo Video

Coming Soon

---

## Screenshots

> Replace the placeholders below with screenshots after deployment.

## Screenshots

### Landing Page
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1915" height="1127" alt="Screenshot 2026-07-22 173424" src="https://github.com/user-attachments/assets/e01cfd72-745e-4d1f-a3b8-929e12b16a22" />



### Dashboard
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1135" alt="Screenshot 2026-07-22 173556" src="https://github.com/user-attachments/assets/f5a85246-536b-4107-8ced-499f8697b944" />


### Resume Analyzer
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1145" alt="Screenshot 2026-07-22 173735" src="https://github.com/user-attachments/assets/bbc72ee6-c2d7-4293-b19c-68d2b6b7e80a" />


### Eligibility / ATS Results
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1138" alt="Screenshot 2026-07-22 173828" src="https://github.com/user-attachments/assets/55d8da36-4c73-437a-aee2-e5b5c5f9f2a1" />


### Recruiter AI Copilot
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1135" alt="Screenshot 2026-07-22 174717" src="https://github.com/user-attachments/assets/27763f93-c0a8-4f4c-8abe-0f37b72a58be" />


### Bulk Screening Portal
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1132" alt="Screenshot 2026-07-22 174804" src="https://github.com/user-attachments/assets/961fd9f6-39a5-4a93-82bb-d6a80340e7db" />


### Resume Comparison
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1916" height="1146" alt="Screenshot 2026-07-22 174240" src="https://github.com/user-attachments/assets/16aa4aae-4cc4-4104-aae6-e21ea85de76d" />


### Career Roadmap
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1128" alt="Screenshot 2026-07-22 173948" src="https://github.com/user-attachments/assets/99c62d2a-57bb-44f9-829c-b825127527c1" />


### PDF Report
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1887" height="1142" alt="Screenshot 2026-07-22 174021" src="https://github.com/user-attachments/assets/d2c88b7f-b39b-45e9-ac18-c1a069fa23df" />


### n8n Workflow
<p align="center">
<img src="docs/screenshots/home.png" width="90%">
</p>

<img width="1917" height="1090" alt="Screenshot 2026-07-22 175751" src="https://github.com/user-attachments/assets/01b35b70-9322-40e1-86a3-c8cb8c7fc9d4" />


<br>

# Why Nexus CV?

Traditional resume screening systems rely heavily on keyword matching and often fail to understand the actual context of a candidate's experience.

Nexus CV combines Machine Learning, Retrieval-Augmented Generation (RAG), Semantic Search, Explainable AI, and a Multi-Agent Architecture to deliver recruiter-friendly insights rather than just ATS scores.

Instead of simply saying a candidate scored 78%, Nexus CV explains:

- Why the candidate received the score
- Missing skills
- Resume strengths
- ATS improvements
- Career recommendations
- Candidate ranking reasons
- Behavioral indicators
- Platform activity

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Presentation Layer                      │
│     Glassmorphic UI — HTML5, CSS3, JS, Chart.js         │
│     Dark Mode Toggle — LocalStorage-backed              │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTPS / REST
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│     Flask 3.x — Routing, Sessions, CSRF, Rate Limiting  │
│     Google OAuth 2.0 — Social Authentication            │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌────────────┐   ┌────────────────┐   ┌─────────────────┐
│ Auth /     │   │ Analysis /     │   │ Bulk Screening  │
│ User Mgmt  │   │ Resume Routes  │   │ + n8n Webhook   │
└────────────┘   └───────┬────────┘   └────────┬────────┘
                         │                      │
                         ▼                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Intelligence Layer                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │            6-Agent Pipeline                     │    │
│  │  Skill → Experience → ATS → Decision            │    │
│  │  Behavioral → Platform Activity                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │         LLM Fallback Chain                      │    │
│  │  Gemini → Groq → OpenAI → Claude                │    │
│  │  → DeepSeek → Qwen → Local Rules               │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    ML / RAG Layer                       │
│  XGBoost Regressor   BGE-large Embeddings               │
│  FAISS Vector Index  spaCy NLP   TF-IDF + RapidFuzz     │
│  BART-MNLI Zero-Shot Classifier                         │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               Database & Storage Layer                  │
│     SQLite (SQLAlchemy ORM) — Users, History, Scores    │
│     Local Disk — uploads/, reports/ (auto-pruned)       │
└─────────────────────────────────────────────────────────┘
```

<br>

## AI Pipeline

The AI pipeline processes every resume submission through a staged sequence before producing a final verdict.

```
Resume PDF + Job Description
          │
          ▼
┌─────────────────────┐
│   Resume Parser     │  pdfplumber — table-aware, multi-column extraction
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Semantic Chunker   │  Section-aware splitting (Experience, Skills, Projects)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Embedding Engine   │  BGE-large-en-v1.5 → 1024-dim vectors → FAISS Index
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│                  6-Agent Pipeline                       │
│                                                         │
│  [Skill Agent]        Keyword + semantic skill scoring  │
│  [Experience Agent]   Career progression + impact eval  │
│  [ATS Agent]          XGBoost structural scoring        │
│  [Decision Agent]     ReAct synthesis + evidence quotes │
│  [Behavioral Agent]   Soft skills + leadership signals  │
│  [Platform Agent]     Activity pattern analysis         │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  7-Signal Hybrid    │  Weighted composite score assembly
│  Ranking Engine     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Output Assembly    │  Dashboard + PDF Report + CSV/JSON Export
└─────────────────────┘
```

<br>

## Multi-Agent System

Six specialist agents collaborate under an `AgentController`. Each agent evaluates a distinct dimension; the Decision Agent synthesizes all signals into a final verdict.

### Agent Descriptions

**1. Skill Agent** *(Deterministic + Embedding)*
Evaluates technical and soft skill alignment. Uses BGE-large embeddings to capture semantic synonyms (e.g. "ML" → "Machine Learning") and RapidFuzz for fuzzy surface matching. No LLM calls — fully deterministic and fast. Returns a skill match score and a list of matched and missing skills.

**2. Experience Agent** *(LLM-Assisted)*
Analyzes career trajectory, role progression, and bullet point quality. Distinguishes responsibility-focused bullets ("Managed a team") from impact-focused ones ("Reduced latency by 40%"). Returns experience quality insights and highlighted achievement markers.

**3. ATS Agent** *(XGBoost ML)*
Extracts 7 structural features from the resume — section completeness, keyword density, formatting signals, quantification presence, and more — and feeds them into the pre-trained `ats_xgb.pkl` XGBoost regressor. Returns an ATS structural score (0–50).

**4. Decision Agent** *(ReAct Reasoning)*
The synthesis layer. Takes outputs from all other agents, executes a 2-iteration ReAct reasoning loop, extracts direct evidence quotes from the resume text, evaluates its own confidence (High / Medium / Low), and produces the final unified score and qualitative verdict.

**ReAct Loop Example:**
```
Thought 1:  Skill score is 44/50, Experience is Strong, ATS is 46/50.
            I need to verify whether the candidate's project work supports this.

Action 1:   Search FAISS index for project and leadership evidence.

Observation: "Led a team of 4 engineers to rebuild the analytics pipeline
              using Flask and XGBoost — reduced processing time by 60%."

Thought 2:  Direct evidence of leadership and relevant stack alignment found.
            Confidence: High. Formulating final verdict.

Action 2:   Deliver unified structured response.
```

**5. Behavioral Agent** *(LLM-Assisted)*
Analyses soft skill signals — communication clarity, leadership language, collaboration indicators, and problem-solving framing — extracted from resume text. Returns a behavioral profile summary and soft skill gap flags.

**6. Platform Activity Agent** *(Rule + LLM)*
Evaluates external platform signals where available — GitHub contribution patterns, LinkedIn activity indicators, and portfolio presence. Flags candidates with strong public technical footprints. Returns an activity signal score and observations.

### Agent Sequence Diagram

```
User ──► AgentController
              │
              ├──► Skill Agent        ──► Skill Score + Matches
              ├──► Experience Agent   ──► Career Insights
              ├──► ATS Agent          ──► XGBoost Structural Score
              ├──► Behavioral Agent   ──► Soft Skill Profile
              ├──► Platform Agent     ──► Activity Signals
              │
              └──► Decision Agent     ──► ReAct Loop
                        │                  ├─ Synthesizes all signals
                        │                  ├─ Extracts evidence quotes
                        │                  └─ Confidence: High/Med/Low
                        │
                        ▼
                Final Verdict + Score
```

<br>

## Recruiter AI Copilot

The Recruiter AI Copilot is a natural language interface built on top of the multi-agent pipeline, designed for recruiters to interrogate candidate data without writing queries or reading raw score breakdowns.

### Capabilities

**Natural Language Questions**
Recruiters can ask plain-English questions about any candidate or set of candidates:
- *"Why does Candidate A rank above Candidate B?"*
- *"What skills is this candidate missing for a senior backend role?"*
- *"Does this candidate show leadership experience?"*
- *"Explain the ATS score for Resume #3."*

**Candidate Comparison**
Side-by-side reasoning across two or more candidates. The Copilot explains score differentials by referencing specific evidence — skill gaps, experience quality differences, and behavioral signal contrasts — rather than just returning raw numbers.

**Missing Skills Analysis**
Given a target job description, the Copilot returns a structured breakdown of which required skills are present, partially matched, or absent — with semantic awareness (so "PyTorch" and "deep learning framework" are understood as related).

**Leadership Analysis**
The Behavioral Agent's output is surfaced through the Copilot to answer questions about leadership signals — team size, project ownership language, mentorship indicators, and decision-making framing in bullet points.

**ATS Explanation**
The Copilot can explain why a candidate received a particular ATS score in plain English, citing the specific structural factors (missing sections, low keyword density, lack of quantified achievements) that drove the result.

**LLM-First, Rule Fallback**
Responses are generated by the active LLM in the fallback chain. If all LLM providers are unavailable, the Copilot falls back to a structured rule engine that generates templated but accurate responses from the raw agent output data.

<br>

## Hybrid Scoring Engine

Every candidate receives a composite score assembled from **7 independent signals**. Each signal captures a different analytical dimension, making the final ranking more robust than any single method alone.

### The 7-Signal Formula

$$\text{Final Score} = w_1 S_{\text{semantic}} + w_2 S_{\text{ATS}} + w_3 S_{\text{agent}} + w_4 S_{\text{skill}} + w_5 S_{\text{xgb}} + w_6 S_{\text{behavioral}} + w_7 S_{\text{platform}}$$

| Signal | Weight | Description |
|--------|--------|-------------|
| **Semantic Similarity** | 0.25 | BGE-large cosine similarity between resume embeddings and target JD |
| **ATS Structural Score** | 0.20 | XGBoost-predicted structural quality from 7 engineered features |
| **Agent Verdict** | 0.20 | Decision Agent's synthesized score with evidence-backed confidence weighting |
| **Skill Registry Overlap** | 0.15 | TF-IDF + fuzzy keyword match rate against role-specific skill taxonomy |
| **XGBoost Adjustment** | 0.10 | Secondary XGBoost signal on completeness and formatting features |
| **Behavioral Score** | 0.05 | Soft skill signal quality from Behavioral Agent |
| **Platform Activity** | 0.05 | External presence signals (GitHub, LinkedIn, portfolio indicators) |

Weights are configurable per role profile in `data/job_roles.json`.

<br>

## Bulk Resume Screening

The bulk screening pipeline handles ZIP archives of up to 50 resumes, processing them concurrently through the full multi-agent stack and returning a ranked shortlist.

### Pipeline Flow

```
1. ZIP Upload
   └── File extension validation + safety filter
   └── Extraction to secure temp directory

2. Parsing Stage (Async per file)
   └── pdfplumber extraction (multi-column aware)
   └── Section header detection and metadata cataloging
   └── Semantic chunking by section boundaries
   └── BGE-large embedding generation

3. Analysis Stage (Parallel)
   └── 6-Agent pipeline per candidate
   └── 7-Signal hybrid score computation
   └── Per-candidate confidence rating

4. Ranking & Shortlisting
   └── Candidates sorted by composite score
   └── Top-N shortlist isolated
   └── Corrupt/unreadable files logged with placeholder, batch continues

5. Output
   └── Visual shortlist dashboard
   └── CSV export of ranked candidates
   └── JSON export for downstream integration
   └── Optional auto-email via SendGrid
```

### n8n Orchestration

Bulk processing is handled by an **11-node self-hosted n8n workflow** (`n8n/bulk_resume_workflow.json`):

```
Webhook Trigger
     │
     ▼
Auth Guard (API Key validation)
     │
     ▼
SplitInBatches (N=1, memory-safe loop)
     │
     ▼
Pipeline 1 (Extraction + Parsing)
     │
     ▼
Pipeline 2 (Agent Analysis + Scoring)     ◄── Error Handler Boundary
     │                                         (corrupt files logged,
     ▼                                          batch continues)
Ranking Script Node
     │
     ▼
Response Node (JSON payload → UI + optional CSV email)
```

When a ZIP is uploaded via the Bulk Screen page, Flask saves the file, validates the schema, and dispatches a background webhook request to n8n. The UI enters a loading state and polls for the final ranked response.

<br>

## Resume Comparison

The Resume Comparison feature performs a structured diff analysis between two versions of a resume — useful for tracking improvement between edits or comparing a tailored version against the original.

### What It Compares

**ATS Score Comparison**
Both versions are independently scored through the ATS Agent. The delta is displayed with a directional indicator (improved / regressed / unchanged).

**Skills Diff**
Tracks which skills were added and which were removed between versions. Categorized by skill type (technical, soft, tools) using the skill taxonomy.

**Gemini Analysis**
The active LLM evaluates the two versions qualitatively — identifying which changes were impactful, which were cosmetic, and which introduced new gaps.

**Improvement Suggestions**
Based on the diff and the target JD (if provided), the Copilot generates a prioritized list of remaining improvements the candidate should make to the newer version.

**Comparison Report**
A downloadable PDF summarizing the diff, score delta, skills changes, and AI suggestions — generated by `compare_pdf_generator.py` via ReportLab.

<br>

## Resume Analysis

Single-resume analysis is the core workflow. A candidate uploads their resume and optionally provides a target job description.

### What the Analysis Covers

**ATS Score**
The ATS Agent extracts 7 structural features and runs the XGBoost regressor to produce a score reflecting how well the resume is structured for automated parsing systems.

**Semantic JD Match**
BGE-large embeddings are generated for both the resume and the JD. Cosine similarity across FAISS-indexed chunks produces a semantic match percentage — capturing alignment that keyword matching misses.

**Role Prediction**
BART-large-MNLI performs zero-shot classification across a taxonomy of job roles, predicting the top candidate role fits without requiring explicit role input from the user.

**Career Roadmap**
Based on the predicted role, current skills, and detected experience level, the `career_recommender.py` module generates a structured progression roadmap — next roles, skills to acquire, and estimated timelines.

**Missing Skills**
The Skill Agent compares the candidate's skill set against the target role's required skill registry. Missing skills are ranked by importance weight from `skills_taxonomy.json`.

**Improvement Suggestions**
The active LLM generates structured, prioritized suggestions for improving the resume — covering content quality, quantification, section completeness, and keyword alignment.

<br>

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3 (Glassmorphic), JavaScript, Chart.js |
| **Backend** | Python 3.10+, Flask 3.x, SQLAlchemy ORM |
| **Database** | SQLite (local), structured via SQLAlchemy |
| **Authentication** | Google OAuth 2.0 (Authlib), Flask-Login, bcrypt |
| **AI — Primary** | Google Gemini 2.5 Flash / Flash Lite |
| **AI — Fallback** | Groq (Llama 3.3 70B), OpenAI, Claude, DeepSeek, Qwen |
| **AI — Local Fallback** | Rule-based heuristic engine (offline, no API required) |
| **ML Models** | XGBoost (XGBRegressor), BART-large-MNLI (zero-shot) |
| **NLP** | spaCy (en_core_web_sm), TF-IDF, RapidFuzz |
| **Embeddings** | BGE-large-en-v1.5 (Sentence Transformers, 1024-dim) |
| **Vector Search** | FAISS (L2 similarity index, memory-cached) |
| **PDF Processing** | pdfplumber (extraction), ReportLab (generation) |
| **Orchestration** | n8n (self-hosted, 11-node bulk workflow) |
| **Task Scheduling** | APScheduler (background cleanup daemon) |
| **Email** | SendGrid API |
| **Security** | Flask-WTF (CSRF), Flask-Limiter, input sanitization |
| **Exports** | CSV, JSON, PDF |

<br>

# 📊 Project Statistics

| Metric | Value |
|---------|------:|
| AI Agents | 6 |
| Hybrid Scoring Signals | 7 |
| LLM Providers | 6 |
| Flask Routes | 40+ |
| Python Modules | 35+ |
| ML Models | 3 |
| Vector Search | FAISS |
| Authentication | Google OAuth |
| Export Formats | PDF, CSV, JSON |
| Resume Formats | PDF |

## Folder Structure

```
Nexus-CV/
├── run.py                          # Flask entrypoint — starts server on localhost:5000
├── requirements.txt                # Project dependencies
├── .env.example                    # Environment variable template
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
│
├── backend/
│   ├── app.py                      # Flask app factory, routes, security middleware
│   ├── database.py                 # SQLite schema and SQLAlchemy session management
│   ├── agent_controller.py         # Orchestrates 6-agent pipeline execution
│   └── input_validator.py          # Request sanitization and injection prevention
│
├── frontend/
│   ├── static/
│   │   ├── style.css               # Glassmorphic stylesheet with dark mode
│   │   ├── script.js               # AJAX handling, dynamic UI updates
│   │   ├── theme.js                # LocalStorage-backed dark/light toggle
│   │   ├── favicon.svg
│   │   ├── nexuscv-logo.svg
│   │   └── google.svg
│   └── templates/
│       ├── base.html               # Master layout (nav, theme loaders)
│       ├── home.html
│       ├── dashboard.html
│       ├── upload.html
│       ├── result.html
│       ├── bulk_screen.html
│       ├── bulk_result.html
│       ├── resume_builder.html
│       ├── resume_preview.html
│       ├── compare.html
│       ├── compare_result.html
│       ├── history.html
│       ├── login.html
│       ├── register.html
│       ├── 404.html
│       └── 500.html
│
├── services/
│   ├── pipeline.py                 # 2-stage analysis workflow orchestrator
│   ├── ai/
│   │   ├── multi_llm.py            # 6-provider fallback chain with thread throttling
│   │   ├── gemini_agent.py         # Gemini-specific prompt formatting
│   │   ├── agent_reasoner.py       # ReAct loop management and output compilation
│   │   └── agents/
│   │       ├── skill_agent.py
│   │       ├── experience_agent.py
│   │       ├── ats_agent.py
│   │       ├── decision_agent.py
│   │       ├── behavioral_agent.py
│   │       └── platform_activity_agent.py
│   ├── ml/
│   │   ├── ats_scorer.py           # Base scoring algorithms and model loaders
│   │   ├── model_hub.py            # In-memory model cache (BGE-large, XGBoost)
│   │   ├── skill_registry.py       # Role-to-skill cluster mappings
│   │   └── embedding_cache.py      # Per-chunk embedding memoization
│   └── processing/
│       ├── resume_parser.py        # pdfplumber-based PDF extraction
│       ├── resume_builder.py       # Input-to-JSON resume normalization
│       ├── bulk_screener.py        # Concurrent multi-file evaluation
│       ├── semantic_chunker.py     # Section-boundary-aware text splitting
│       ├── career_recommender.py   # Role-based roadmap generation
│       ├── jd_matcher.py           # JD-to-resume vector comparison
│       ├── multi_role_predictor.py # BART-MNLI zero-shot role classification
│       ├── resume_insights.py      # Keyword strength and weakness extraction
│       ├── resume_suggestions.py   # Structural improvement recommendations
│       ├── pdf_generator.py        # ReportLab analysis PDF generation
│       ├── compare_pdf_generator.py
│       └── email_sender.py         # SendGrid email dispatch
│
├── model/
│   └── ats_xgb.pkl                 # Trained XGBRegressor artifact
│
├── data/
│   ├── career_paths.json
│   ├── job_roles.json
│   ├── skills.txt                  # 15,000+ normalized technical keywords
│   ├── skills_taxonomy.json
│   └── rag/
│       ├── resume_samples.json
│       └── jd_samples.json
│
├── utils/
│   ├── bias_filter.py              # PII anonymization for LLM prompts
│   ├── cleanup.py                  # APScheduler file pruning daemon
│   ├── json_utils.py               # Safe JSON parsing helpers
│   ├── pdf_utils.py                # ReportLab styling constants
│   ├── rag_store.py                # FAISS index management interface
│   └── skill_normalizer.py         # Skill surface form normalization
│
├── n8n/
│   └── bulk_resume_workflow.json   # 11-node bulk screening workflow blueprint
│
├── docs/
│   └── Nexus_CV_Project_Report.md
│
├── uploads/                        # Temp resume storage (gitignored, auto-pruned)
├── reports/                        # Generated PDF storage (gitignored, auto-pruned)
└── logs/                           # Application error logs (gitignored)
```

<br>

## Installation

### Prerequisites

- Python 3.10 or 3.11
- Git
- Node.js / npx (optional — only required for local n8n bulk screening)

### 1. Clone the Repository

```bash
git clone https://github.com/Rohit122622/Nexus-CV.git
cd Nexus-CV
```

### 2. Create and Activate a Virtual Environment

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download the spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys. See [Environment Variables](#environment-variables) below.

### 6. Run the Application

```bash
python run.py
```

Open `http://localhost:5000` in your browser.

### 7. Run n8n (Optional — Bulk Screening Only)

```bash
npx n8n
```

Open `http://localhost:5678`, click **Import from File**, select `n8n/bulk_resume_workflow.json`, save, and toggle the workflow to **Active**.

<br>

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Flask session and CSRF signing secret. Use a long random string. |
| `FLASK_ENV` | No | `development` or `production`. Controls debug output and reloading. |
| `GEMINI_API_KEY` | **Yes*** | Google Gemini API key. Primary LLM provider. |
| `GROQ_API_KEY` | **Yes*** | Groq API key. Secondary LLM fallback (Llama 3.3 70B). |
| `OPENAI_API_KEY` | No | OpenAI API key. Tertiary LLM fallback. |
| `CLAUDE_API_KEY` | No | Anthropic Claude API key. Fourth fallback. |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key. Fifth fallback. |
| `QWEN_API_KEY` | No | Qwen API key. Sixth fallback. |
| `NEXUS_API_KEY` | No | Shared secret for authenticating n8n → Flask webhook calls. |
| `GOOGLE_CLIENT_ID` | No | Google OAuth 2.0 client ID for social login. |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth 2.0 client secret. |
| `SENDGRID_API_KEY` | No | SendGrid key for automated PDF email delivery. |

> *At least one of `GEMINI_API_KEY` or `GROQ_API_KEY` is required to enable LLM features. If neither is set, the platform falls back to the local rule-based engine automatically.

> Never commit your `.env` file. It is excluded via `.gitignore`.

<br>

## API Endpoints

### Health Check

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/health` | Public | Returns database and ML model status |

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": "connected",
    "xgb_model": "loaded",
    "embedding_model": "ready"
  }
}
```

### Resume Scoring

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/score` | Session | Run full 6-agent + hybrid scoring on a resume |

**Request:**
```json
{
  "resume_text": "...",
  "job_description": "...",
  "role": "Backend Engineer",
  "run_agents": true
}
```

**Response:**
```json
{
  "status": "success",
  "ats_score": 88.5,
  "confidence_level": "High",
  "verdict": "Strong alignment with the target role...",
  "skill_matches": ["Python", "Flask", "XGBoost"],
  "missing_skills": ["Docker", "Kubernetes"],
  "evidence_quotes": ["Led backend development using Python and Flask"]
}
```

### Bulk Screening

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/bulk-rank` | Session | Submit ZIP for async n8n bulk processing |

**Request:** `multipart/form-data` — fields: `zip_file`, `job_description`

**Response:**
```json
{
  "task_id": "bulk_8f9e2b1",
  "status": "processing",
  "candidates_count": 14,
  "eta_seconds": 45
}
```

### Recruiter Copilot

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/copilot/query` | Session | Submit a natural language recruiter question |

**Request:**
```json
{
  "question": "Why does Candidate A rank above Candidate B?",
  "candidate_ids": ["cand_001", "cand_002"]
}
```

<br>

## Performance Notes

**Model Caching** — BGE-large and the XGBoost regressor are loaded once at startup and kept in memory via `model_hub.py`. Subsequent requests skip initialization overhead entirely.

**Embedding Memoization** — `embedding_cache.py` caches embeddings per resume chunk in memory. On consecutive edits to the same resume, previously embedded chunks are reused, reducing transformer calls significantly for common re-analysis patterns.

**Thread-Safe LLM Throttling** — A global lock (`_gemini_lock`) enforces a 1.5-second minimum interval between Gemini API calls. This prevents concurrent requests from triggering rate limits under normal multi-user load.

**Automatic File Pruning** — An APScheduler daemon runs every 6 hours, removing temporary files from `uploads/` and `reports/` to prevent disk accumulation without requiring manual intervention.

**Offline Fallback** — If no LLM API keys are configured, the platform runs entirely on local models (spaCy, TF-IDF, XGBoost, FAISS) and returns structured ATS results without any cloud dependency.

<br>

## Security

**PII Anonymization** — Before any resume text is sent to an LLM, `bias_filter.py` strips candidate names, precise locations, and personal contact details. This supports unbiased evaluation and reduces data exposure to third-party APIs.

**Rate Limiting** — Flask-Limiter restricts the `/api/v1/score` endpoint to 10 requests per minute per IP, mitigating automated scraping and abuse.

**Input Sanitization** — All string inputs are processed through `input_validator.py` before reaching service layers, guarding against HTML injection, SQL injection, and prompt injection patterns.

**CSRF Protection** — Flask-WTF CSRF tokens are required on all state-changing form submissions.

**No Credential Leakage** — All secrets are loaded from environment variables at runtime. Nothing is hardcoded or committed to version control. `.env` is explicitly gitignored.

**Secure Headers** — Response-level security headers are applied globally: XSS protection, HSTS, X-Frame-Options, and Content-Security-Policy.

<br>

# Repository Topics

AI • Resume Analyzer • ATS • Agentic AI • Machine Learning • NLP • RAG • Semantic Search • Flask • Python • FAISS • XGBoost • HRTech • Recruitment • LLM

## Future Improvements

- [ ] **Docker Compose Setup** — Single-command local deployment for Flask, n8n, and dependencies
- [ ] **Cloud Deployment Guides** — Railway, Render, and AWS EC2 deployment documentation
- [ ] **VectorDB Migration** — Adapters to swap FAISS for Qdrant or Pinecone at scale
- [ ] **Fine-Tuned Embeddings** — Domain-adapted BGE model trained on technical resume corpora
- [ ] **Multi-Tenant Recruiter Panel** — Separate corporate logins, custom JD templates, pipeline views
- [ ] **Email Notifications** — Automated alerts for bulk screening completion and score thresholds
- [ ] **Advanced Analytics Dashboard** — Score trend analysis, skill gap heatmaps, role prediction confidence tracking
- [ ] **Mobile-Responsive UI** — Full mobile layout optimization
- [ ] **Resume Version History** — Per-user versioned resume store with diff tracking over time
- [ ] **Expanded Role Taxonomy** — Broader BART-MNLI classification coverage across more job families

<br>

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for branch conventions, coding standards, and testing expectations before submitting a pull request.

**Quick start:**
```bash
git checkout -b feature/your-feature-name
# make your changes
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# open a Pull Request on GitHub
```

<br>

# Disclaimer

This project is intended for educational, research, and recruitment-assistance purposes.

Nexus CV is designed to assist recruiters by providing explainable insights into resumes and candidate profiles. Final hiring decisions should always involve human evaluation.

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

<br>

<p align="center">
  Built by <strong>Rohit Posimsetti</strong>
  <br>
  <a href="https://github.com/Rohit122622">GitHub</a> · rohit122622@gmail.com
  <br><br>
  <sub>Flask · XGBoost · Gemini · FAISS · spaCy · BGE-large · n8n · BART-MNLI</sub>
</p>
