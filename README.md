 
# AI-Powered Customer Support System

Multi-agent AI system for intelligent customer support.

## Features
- Multi-Agent Architecture (Router + 3 specialist agents)
- 9 AI-powered tools
- REST API with FastAPI
- React frontend
- PostgreSQL database

## Tech Stack
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Groq AI  
**Frontend:** React, Vite, Axios

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Groq API key

### Backend Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python create_database.py
python create_tables.py
python seed_database.py
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
Create `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_support
GROQ_API_KEY=your_key_here
AI_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
```

## API Endpoints
- POST `/api/chat/messages` - Send message
- GET `/api/chat/conversations` - List conversations
- GET `/api/agents` - List available agents
