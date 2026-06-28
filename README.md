# AI Trust Validator

**Universal AI Agent Validation and Trust Assessment Platform for Supply Chain Management**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)

---

## Overview

AI Trust Validator is a customer-facing SaaS platform that validates SCM AI agents using a **deterministic-first scoring engine** across 6 trust dimensions. The same agent + same rules = the same score, always.

Live Link- https://ai-trust-validator-frontend.onrender.com

### Key Features

- **Deterministic Trust Score** — 18 rule-based checks, 6 weighted dimensions, reproducible results
- **Interactive Results Dashboard** — the dashboard IS the report; no file downloads needed
- **Multiple Input Methods** — GitHub/GitLab URL, ZIP upload, or individual file upload
- **Security Audit** — hardcoded secret detection, eval/exec detection, subprocess shell injection
- **Actionable Recommendations** — every finding comes with implementation-ready code examples
- **Optional LLM Insights** — opt-in AI-powered business risk commentary (OpenAI)
- **Validation History** — track all runs, compare scores over time

---

## Trust Score Dimensions

| Dimension | Weight | What is checked |
|---|---|---|
| Specification Completeness | 20% | README, docstrings, entry points |
| Input/Output Clarity | 15% | Type hints, Pydantic schemas, I/O docs |
| Reliability & Error Handling | 20% | try/except, retry logic, timeouts, deps |
| Security Hygiene | 20% | Secrets, eval/exec, subprocess safety, env vars |
| Observability / Logging | 10% | Logging framework, structured logs |
| SCM Readiness / Business Fit | 15% | Domain vocabulary, config, tests, Docker |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git (for repository URL validation)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API docs available at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

### 3. Docker Compose (recommended)

```bash
cp backend/.env.example backend/.env
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Optional: LLM Insights

To enable AI-powered business risk insights, set in `backend/.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
LLM_ENABLED=true
OPENAI_MODEL=gpt-4o-mini
```

Then toggle "Enable AI Insights" on the submission form. LLM insights are **never** used for the official trust score — only for supplemental commentary.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Next.js Frontend                     │
│  /submit  →  /validating/[id]  →  /results/[id]         │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│  POST /submit/url    GET /validations/{id}/status       │
│  POST /submit/files  GET /validations/{id}/results      │
│  GET  /history       DELETE /validations/{id}           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Validation Engine Pipeline                  │
│  1. RepoIngestor  →  2. StaticAnalyzer                  │
│  3. RuleEngine    →  4. ScoringEngine                   │
│  5. EvidenceBuilder  6. RecommendationBuilder           │
│  7. LLMInsights (optional)                              │
└──────────────────────┬──────────────────────────────────┘
                       │
              SQLite + Local Storage
```

### Upgrade Path

| Component | MVP | Production |
|---|---|---|
| Database | SQLite | PostgreSQL (swap connection string) |
| Storage | Local filesystem | S3 / GCS |
| Queue | FastAPI BackgroundTasks | Celery + Redis |
| Auth | None | Auth0 / Clerk |
| Deploy | Docker Compose | Kubernetes |

---

## Project Structure

```
ai-trust-validator/
├── frontend/          # Next.js 14 + TypeScript + Tailwind
│   ├── app/
│   │   ├── submit/    # New validation form
│   │   ├── validating/[id]/  # Progress view
│   │   ├── results/[id]/     # Results dashboard
│   │   └── history/          # Validation history
│   └── lib/           # API client + TypeScript types
│
├── backend/           # FastAPI
│   ├── engine/        # Validation engine modules
│   │   ├── repo_ingestor.py
│   │   ├── static_analyzer.py
│   │   ├── rule_engine.py       # 18 deterministic rules
│   │   ├── scoring_engine.py    # Weighted trust scoring
│   │   ├── evidence_builder.py
│   │   ├── recommendation_builder.py
│   │   └── llm_insights.py      # Optional LLM layer
│   ├── routers/
│   ├── models.py
│   └── main.py
│
└── docker-compose.yml
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
