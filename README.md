🤖 AI-Powered Customer Support System

An AI-powered customer support platform built using a multi-agent architecture.
The system intelligently routes user queries to specialized agents (Support, Order, Billing) and responds using AI with database-backed context.

🌐 Live Demo & Links

Frontend (Vercel):
👉 https://ai-customer-support-hlm9nfv36-jinxs-projects-b8a1ef07.vercel.app/

Backend API (Railway):
👉 https://web-production-b46fb.up.railway.app/

API Documentation (Swagger):
👉 https://web-production-b46fb.up.railway.app/docs

Health Check:
👉 https://web-production-b46fb.up.railway.app/api/health

✨ Key Features

Multi-Agent Architecture

Router Agent (classifies user intent)

Support Agent (FAQs & general help)

Order Agent (orders, tracking, cancellation)

Billing Agent (payments, invoices, refunds)

AI-Powered Query Routing

Each user message is analyzed and routed to the correct agent automatically.

Tool-Enabled Agents

Agents use structured tools to fetch data from the database (orders, payments, conversations).

Context-Aware Conversations

Maintains conversation history to give relevant and consistent responses.

Rate Limiting

Prevents API abuse using request limits.

Live Frontend UI

Real-time chat interface with typing indicators and agent labels.

🧠 How the System Works (High Level)

User sends a message from the frontend.

The Router Agent analyzes the message intent.

The message is delegated to the correct specialist agent.

The agent may use database tools if required.

AI generates a response using context + tools.

The response is stored and returned to the frontend.

🛠 Tech Stack
Backend

FastAPI – REST API

PostgreSQL – Database

SQLAlchemy (Async) – ORM

Groq AI (LLaMA 3) – LLM provider

SlowAPI – Rate limiting

Frontend

React

Vite

Axios

Lucide Icons

Deployment

Backend: Railway

Frontend: Vercel

📦 Project Structure
ai-customer-support/
├── app/
│   ├── agents/
│   ├── services/
│   ├── tools/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   └── main.py
├── frontend/
│   ├── src/
│   └── index.html
├── requirements.txt
└── README.md

⚙️ Setup Instructions
Prerequisites

Python 3.10+

Node.js 18+

PostgreSQL 15+

Groq API Key

🚀 Backend Setup
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python create_database.py
python create_tables.py
python seed_database.py

uvicorn app.main:app --reload


Backend runs at:
👉 http://127.0.0.1:8000

🎨 Frontend Setup
cd frontend
npm install
npm run dev


Frontend runs at:
👉 http://localhost:5173

🔐 Environment Variables

Create a .env file in the root directory:

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_support

AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

🔌 API Endpoints
Chat

POST /api/chat/messages – Send a message

GET /api/chat/conversations – List conversations

GET /api/chat/conversations/{id} – Get conversation details

Agents

GET /api/agents – List available agents

GET /api/agents/{agent}/capabilities – Agent capabilities

🧪 Example Query Flow

“Where is my order ORD-2024-002?” → Order Agent

“I want to check invoice INV-2024-004” → Billing Agent

“How do I reset my password?” → Support Agent

📌 Highlights

Clean separation of concerns using agents

Beginner-friendly architecture

Production-ready API

Fully deployed and accessible online
