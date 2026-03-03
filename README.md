# Intelligent SQL Copilot ✈️

An AI-powered natural language to SQL assistant for flight data analysis. Type a question in plain English — get back optimized SQL, real results, query plan analysis, and index suggestions.

![Stack](https://img.shields.io/badge/Python-FastAPI-009688?style=flat)
![Stack](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat)
![Stack](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat)
![Stack](https://img.shields.io/badge/AI-OpenAI%20GPT4-412991?style=flat)
![Stack](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat)
![Stack](https://img.shields.io/badge/Deploy-Docker-2496ED?style=flat)

## Features

- **Natural Language → SQL** — Schema-aware prompt engineering converts plain English to optimized PostgreSQL
- **EXPLAIN ANALYZE Parser** — Detects sequential scans, extracts node costs, flags expensive operations
- **Index Suggestion Engine** — AI-generated index recommendations with DDL you can copy-paste
- **Redis Caching** — Repeated queries return instantly with cached results
- **Query History** — Every query logged with execution time, row count, and performance metrics
- **React Dashboard** — SQL syntax highlighting, results table, query plan tree, optimization panel

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| AI | OpenAI GPT-4 / Ollama |
| Frontend | React, Vite, Zustand |
| Deploy | Docker Compose, nginx |

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Setup

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/intelligent-sql-copilot.git
cd intelligent-sql-copilot
```

2. Add your OpenAI key to `.env`:
```
OPENAI_API_KEY=your-key-here
```

3. Start everything:
```bash
docker compose up -d
```

4. Seed the database:
```bash
pip install -r requirements.txt
python -m app.db.seed
```

5. Start the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

6. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

7. Open http://localhost:5173

## Example Queries

- *"Which airlines have the highest average departure delay?"*
- *"What are the top 10 busiest routes by number of flights?"*
- *"Show me all cancelled flights in the last 30 days"*
- *"Which aircraft model is used most frequently?"*
- *"What is the average review rating per airline?"*

## Project Structure
```
intelligent-sql-copilot/
├── app/
│   ├── api/v1/          # FastAPI route handlers
│   ├── services/
│   │   ├── ai/          # NL→SQL, optimizer, validator, prompt builder
│   │   ├── database/    # Query executor, EXPLAIN parser, schema inspector
│   │   └── cache/       # Redis service
│   ├── models/          # SQLAlchemy ORM models
│   └── schemas/         # Pydantic request/response models
├── frontend/
│   └── src/
│       ├── components/  # React UI components
│       ├── store/       # Zustand state management
│       └── api/         # API client
├── sql/
│   └── schema.sql       # Database schema, indexes, views, triggers
└── docker-compose.yml
```
