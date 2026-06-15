# Eluno OMS — Architecture Note

## Problem Statement

Eyewear orders are prescription-driven manufacturing workflows, not standard ecommerce SKUs. Each order carries sphere, cylinder, axis, lens type, index, coating, and frame details. Orders move through lab stages with variable turnaround times. QC failures trigger reorders. Operations teams need inventory-aware TAT, SLA visibility, proactive breach alerts, and an AI assistant that answers questions from live order data.

## System Design

**Monolithic architecture**: Streamlit frontend → FastAPI backend → SQLite database.

| Component | Responsibility |
|-----------|----------------|
| Inventory Service | Lens lookup by Rx + type + coating; In House (1 day) vs Vendor (4 days) TAT |
| Order Service | Full lifecycle with StatusHistory audit trail; QC failure loop |
| SLA Service | Elapsed/remaining time, Green/Yellow/Red health |
| Prediction Service | RandomForest breach probability per active order |
| Alert Service | Email + dashboard when probability > 70% |
| Copilot Service | Groq Llama with structured DB context |

### Order Workflow

```
Order Placed → Prescription Verified → Lens Allocated → Manufacturing
  → Quality Check → Dispatched → Delivered

Failure path: Quality Check → Quality Check Failed → Reorder Required
  → Manufacturing → Quality Check → ...
```

Every status change is recorded in `StatusHistory`.

### Database Tables

- **inventory** — lens stock by prescription attributes
- **orders** — customer, Rx, frame, status, SLA
- **status_history** — audit trail
- **predictions** — ML breach scores
- **alerts** — triggered notifications

## AI Components

### 1. SLA Breach Predictor (RandomForest)

- **Training data**: 1200+ synthetic historical orders with realistic delay patterns
- **Features**: lens_type, current_stage, days_elapsed, sla_days
- **Target**: delay_flag (binary)
- **Output**: breach_probability (0–1), mapped to Low / Medium / High risk

### 2. Operations Copilot (Groq Llama)

- Aggregates live DB context: active orders, breached SLAs, high-risk predictions, low stock, bottlenecks
- Answers natural-language ops questions with actionable summaries
- Rule-based fallback when Groq API is unavailable

## Why RandomForest?

- Works well on tabular features without heavy feature engineering
- Handles mixed categorical (lens type, stage) and numeric (days elapsed) inputs via OneHotEncoder pipeline
- Fast to train, interpretable, robust on small/medium datasets
- No GPU required — ideal for internal ops tooling MVP

## Why Groq Llama?

- Low-latency inference suitable for interactive ops chat
- Cost-effective for read-only Q&A over structured context
- Strong instruction-following for concise, actionable operational summaries

## Future Improvements

- Real ERP / lab system integrations (POS, manufacturing queue)
- Scheduled alert cron with retry queue
- Human-in-the-loop QC feedback for model retraining
- Role-based auth (store manager vs central ops)
- PostgreSQL for multi-store concurrency
- Real-time WebSocket updates on order status changes
