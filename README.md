# Eluno OMS

AI-Powered Order Management System for **Eluno**, a fashion-first eyewear brand. Handles prescription-driven order lifecycle, lens inventory, SLA monitoring, ML-based breach prediction, automated alerts, and an AI operations copilot.

## Features

- **Lens Inventory Management** — CRUD + availability lookup (In House vs Vendor Procurement)
- **Order Lifecycle** — Full eyewear workflow with QC failure / reorder path
- **SLA Monitoring** — Green / Yellow / Red health with countdown
- **SLA Breach Prediction** — RandomForest classifier on synthetic historical data
- **Automated Alerts** — Dashboard + SMTP email when breach probability > 70%
- **AI Operations Copilot** — Groq Llama assistant grounded in live DB context

## Architecture

```
Streamlit UI  →  FastAPI REST API  →  SQLite (SQLAlchemy)
                      ↓
              RandomForest ML + Groq LLM + SMTP Alerts
```

Monolithic, single-repo, deployable MVP — no microservices.

## Setup

### 1. Clone and create virtual environment

```bash
cd eluno-oms
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` with your credentials:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI Chatbot |
| `SMTP_USER` / `SMTP_PASSWORD` | Email alerts (optional for demo) |
| `ALERT_TO_EMAIL` | Alert recipient |

### 3. Initialize database and seed data

```bash
python scripts/init_db.py
python scripts/seed_inventory.py
python scripts/seed_orders.py
python scripts/train_model.py
```

### 4. Run the application

**Terminal 1 — Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
streamlit run frontend/app.py
```

**Terminal 3 — Alert engine (optional, periodic):**
```bash
python scripts/run_alert_engine.py
```

- API docs: http://127.0.0.1:8000/docs
- Streamlit UI: http://localhost:8501

## Environment Variables

See `.env.example` for full list. Key variables:

```
DATABASE_URL=sqlite:///./data/eluno_oms.db
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
BREACH_ALERT_THRESHOLD=0.70
```

## Train ML Model

```bash
python scripts/train_model.py
```

Generates 1200+ synthetic records in `data/synthetic_orders.csv` and trains a RandomForest model saved to `data/models/sla_breach_model.joblib`.

## Run Alert Engine

```bash
python scripts/run_alert_engine.py
```

Scores all active orders, stores predictions, and triggers email alerts for high-risk orders.

## Groq Configuration

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Set `GROQ_API_KEY` in `.env`

The copilot falls back to rule-based answers if Groq is not configured.

## Project Structure

```
eluno-oms/
├── backend/          # FastAPI app, models, services, ML
├── frontend/         # Streamlit UI (6 pages)
├── scripts/          # DB init, seed, train, alerts
├── data/             # SQLite DB, synthetic data, ML model
├── README.md
└── ARCHITECTURE.md
```

## Demo Flow

1. Open **Orders** → create a Progressive lens order with out-of-stock Rx → see Vendor Procurement TAT
2. Advance order through workflow → trigger QC Failed → Reorder Required
3. Go to **SLA Monitoring** → Run Predictions → see breach probability
4. Check **Alerts** for high-risk notifications
5. Ask **AI Chatbot**: *"Which orders are at highest risk?"*

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/inventory` | Inventory CRUD |
| GET/POST | `/inventory/availability` | Lens availability check |
| GET/POST | `/orders` | Order CRUD |
| PATCH | `/orders/{id}/status` | Workflow status transition |
| GET | `/orders/{id}/sla` | SLA metrics |
| POST | `/predictions/run` | Run ML predictions |
| GET | `/predictions` | List predictions |
| GET | `/alerts` | List alerts |
| POST | `/copilot/chat` | AI Chatbot Q&A |

## License

Built as a hiring assignment MVP for Eluno.
