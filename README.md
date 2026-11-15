#  AI-Powered Customer Support System

An **AI-powered customer support platform** built using a **multi-agent architecture**. The system intelligently understands user intent, routes queries to specialized agents, and generates accurate responses using **LLMs + database-backed context**.

This project is designed to demonstrate **production-ready AI system design** with clean separation of concerns, async APIs, and real-world features like rate limiting and persistent conversations.

---

##  Live Demo & Links

* **Frontend (Vercel)**
   [https://ai-customer-support-hlm9nfv36-jinxs-projects-b8a1ef07.vercel.app/](https://ai-customer-support-hlm9nfv36-jinxs-projects-b8a1ef07.vercel.app/)

* **Backend API (Railway)**
   [https://web-production-b46fb.up.railway.app/](https://web-production-b46fb.up.railway.app/)

* **API Documentation (Swagger UI)**
   [https://web-production-b46fb.up.railway.app/docs](https://web-production-b46fb.up.railway.app/docs)

* **Health Check**
   [https://web-production-b46fb.up.railway.app/api/health](https://web-production-b46fb.up.railway.app/api/health)

---

##  Key Features

###  Multi-Agent Architecture

* **Router Agent** – Classifies user intent and routes queries
* **Support Agent** – Handles FAQs and general support queries
* **Order Agent** – Handles orders, tracking, and cancellations
* **Billing Agent** – Handles invoices, payments, and refunds

###  AI-Powered Query Routing

* User messages are automatically analyzed and routed to the correct agent
* No hardcoded rules — routing is handled via LLM-based intent classification

###  Tool-Enabled Agents

* Agents can access **structured tools** to fetch data from the database
* Example tools:

  * Order lookup
  * Payment & invoice retrieval
  * Conversation history fetch

###  Context-Aware Conversations

* Maintains full conversation history
* Ensures consistent, relevant, and human-like responses

###  Rate Limiting

* Prevents API abuse using request limits (SlowAPI)

###  Live Frontend UI

* Real-time chat interface
* Typing indicators
* Agent labels for transparency

---

##  How the System Works

1. User sends a message from the frontend UI
2. **Router Agent** analyzes the intent
3. Query is delegated to the appropriate specialist agent
4. Agent may call database tools if required
5. LLM generates a response using context + tool results
6. Response is stored and sent back to the frontend

---

##  Tech Stack

### Backend

* **FastAPI** – REST API framework
* **PostgreSQL** – Relational database
* **SQLAlchemy (Async)** – Async ORM
* **Groq AI (LLaMA 3)** – LLM provider
* **SlowAPI** – Rate limiting

### Frontend

* **React**
* **Vite**
* **Axios**
* **Lucide Icons**

### Deployment

* **Backend** – Railway
* **Frontend** – Vercel

---

##  Project Structure

```bash
ai-customer-support/
├── app/
│   ├── agents/        # Router & specialist agents
│   ├── services/      # Business logic layer
│   ├── tools/         # DB tools used by agents
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── core/          # Config, settings, utils
│   └── main.py        # FastAPI entry point
├── frontend/
│   ├── src/
│   └── index.html
├── scripts/           # Manual smoke-test scripts (config, AI, agents)
├── tests/             # Automated test suite (pytest)
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

---

##  Setup Instructions

### Prerequisites

* Python **3.10+**
* Node.js **18+**
* PostgreSQL **15+**
* Groq API Key

---

##  Backend Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

cp .env.example .env      # then edit the values

python create_database.py
python create_tables.py
python seed_database.py

uvicorn app.main:app --reload
```

Backend runs at:
 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
 [http://localhost:5173](http://localhost:5173)

---

##  Environment Variables

Copy `.env.example` to `.env` in the root directory and edit it:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_support
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
RATE_LIMIT_PER_MINUTE=20
CORS_ORIGINS=["http://localhost:5173"]
```

| Variable | Default | Notes |
| --- | --- | --- |
| `RATE_LIMIT_PER_MINUTE` | `20` | Chat requests per client IP per minute (HTTP 429 beyond that) |
| `CORS_ORIGINS` | localhost `3000`/`5173` | JSON list. **Add your deployed frontend URL** in production |
| `DEBUG` | `false` | When `true`, error responses include exception details |
| `DATABASE_ECHO` | `false` | Log all SQL statements |

The frontend reads the backend URL from `VITE_API_URL` (see `frontend/.env.example`).

---

##  Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use an in-memory SQLite database and a fake LLM client, so no Postgres instance or API key is needed.

Manual smoke tests against real services (need a configured `.env`):

```bash
python -m scripts.check_config
python -m scripts.check_ai
python -m scripts.check_agents
```

---

##  API Endpoints

### Chat

* `POST /api/chat/messages` – Send a message
* `GET /api/chat/conversations` – List conversations
* `GET /api/chat/conversations/{id}` – Get conversation details
* `DELETE /api/chat/conversations/{id}` – Delete a conversation

### Agents

* `GET /api/agents` – List available agents
* `GET /api/agents/{agent}/capabilities` – Agent capabilities

---

##  Example Query Flow

| User Query                             | Routed Agent  |
| -------------------------------------- | ------------- |
| "Where is my order ORD-2024-002?"      | Order Agent   |
| "I want to check invoice INV-2024-004" | Billing Agent |
| "How do I reset my password?"          | Support Agent |

---



