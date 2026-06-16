# Eluno OMS – AI-Powered Order Management System

AI-powered Order Management System built for Eluno Eyewear.

## Live Demo

### Product URL
https://eluno-oms-1.onrender.com/

### Backend API
https://eluno-oms-6tn5.onrender.com/

### API Documentation
https://eluno-oms-6tn5.onrender.com/docs

---

# Overview

Eluno OMS digitizes the eyewear order lifecycle and adds AI-powered operational intelligence.

The system supports:

- End-to-end order workflow management
- Inventory visibility and lens availability checks
- SLA breach prediction using Machine Learning
- Automated alert generation
- AI Operations Copilot
- Complete order audit trail

---

# Features

## Order Workflow Management

Supported workflow:

```
New
 ↓
Frame Allocated
 ↓
Lens Allocated
 ↓
Manufacturing
 ↓
Quality Check
 ↓
Ready To Ship
 ↓
Delivered
```

Workflow enforcement rules:

- Orders can only move to the next valid stage
- Full status history tracking
- Reorder support for QC failures

---

## Inventory Availability Engine

Inventory lookup API:

```http
POST /inventory/availability
```

Example:

```json
{
  "sphere": -2,
  "cylinder": -1,
  "axis": 180,
  "lens_type": "Single Vision",
  "coating": "Anti-Reflective"
}
```

Possible outcomes:

- In-House Inventory Available
- Vendor Procurement Required
- Estimated Turnaround Time (TAT)

---

## SLA Breach Prediction

Machine Learning model predicts potential SLA violations.

Features used:

- Order age
- Inventory status
- Procurement requirements
- Workflow stage
- Historical fulfillment patterns

Outputs:

- Risk score
- High-risk order identification
- Operational recommendations

---

## Alert Engine

Automatically generates alerts for:

- Potential SLA breaches
- Delayed orders
- Workflow bottlenecks

---

## AI Copilot

Natural language operations assistant.

Example questions:

- Which orders are likely to breach SLA?
- Show delayed manufacturing orders.
- What is causing bottlenecks today?
- Which orders require procurement?

---

# Architecture

```text
Orders
   ↓
Workflow Engine
   ↓
Inventory Engine
   ↓
ML Prediction Layer
   ↓
Alert Engine
   ↓
AI Copilot
   ↓
Dashboard
```

---

# Tech Stack

## Backend

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Machine Learning

- Scikit-Learn
- Pandas
- Joblib

## Frontend

- Streamlit
- Plotly

## AI

- Groq LLM
- Rule-Based Fallback Engine

## Deployment

- Render 

---

# Project Structure

```text
backend/
├── routers/
├── services/
├── schemas/
├── models/
├── ml/
└── database/

frontend/
├── pages/
├── api_client.py
└── app.py

data/
├── eluno_oms.db
├── models/
└── synthetic_orders.csv

scripts/
├── init_db.py
├── seed_inventory.py
├── seed_orders.py
└── train_model.py
```

---

# API Endpoints

## Orders

```http
GET    /orders
POST   /orders
PATCH  /orders/{id}/status
GET    /orders/{id}/history
```

## Inventory

```http
GET    /inventory
POST   /inventory/availability
GET    /inventory/summary
```

## Predictions

```http
POST   /predictions/run
GET    /predictions
```

## Alerts

```http
GET    /alerts
```

## AI Copilot

```http
POST   /copilot/chat
```

---

# Assignment Validation

### Completed Scenarios

✅ Full Order Lifecycle → Delivered

✅ QC Failure → Reorder Workflow

✅ Inventory Availability Lookup

✅ SLA Risk Prediction

✅ Alert Generation

✅ Frontend Dashboard

✅ Backend API

✅ Cloud Deployment

# Extra Assignment Validation


✅ AI Copilot

---

# Sample Results

### Inventory Lookup

Input:

```json
{
  "sphere": -2,
  "cylinder": -1,
  "axis": 180,
  "lens_type": "Single Vision",
  "coating": "Anti-Reflective"
}
```

Output:

```text
Vendor Procurement Required
Estimated TAT: 4 Days
```

### SLA Monitoring

```text
Scored 10 Orders
3 High-Risk Orders
0 Alerts Sent
```

---

# Local Setup

## Clone Repository

```bash
git clone https://github.com/KiranBiju/eluno-oms.git
cd eluno-oms
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Backend

```bash
uvicorn backend.main:app --reload
```

## Run Frontend

```bash
streamlit run frontend/app.py
```

---

# Author

Kiran Biju

AI Engineer | Machine Learning | Generative AI | Agentic Systems
