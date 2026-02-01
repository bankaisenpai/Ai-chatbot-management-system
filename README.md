🤖 AI Chatbot Platform

Full-Stack Multi-Bot Conversational Application

A production-ready, ChatGPT-style chatbot platform built with React, FastAPI, and Groq LLM, supporting multiple bots, persistent chat sessions, and secure authentication.

📌 Overview

This project is a full-stack multi-bot AI chat platform that allows users to:

Register & log in securely using JWT authentication

Chat with multiple specialized bots (Support, Tutor, Fun)

Create, switch, and delete chat sessions

Persist conversations across page refreshes

Experience a polished, ChatGPT-like UI

The system is designed with scalability, security, and clean architecture in mind.

✨ Key Features
🔐 Authentication

User Register & Login

JWT-based authentication

Protected routes

Secure password hashing (bcrypt)

🤖 Multi-Bot Support

Support Bot 🛠️

Tutor Bot 🎓

Fun Bot 🎉

Bot-specific chat isolation

Easy bot switching

💬 Chat Sessions

Create new chat sessions per bot

View previous sessions

Delete chats manually

Session-based message grouping

💾 Persistence

Messages & sessions stored in LocalStorage

Chat history restored after refresh

Backend database ready for full persistence

🎨 UI / UX

ChatGPT-style 3-column layout

Dark theme

Sticky input bar

Optimistic message rendering

Empty states & loading indicators

🧱 Tech Stack
Frontend

React 18 (Vite)

Axios

React Router

CSS (custom dark theme)

Backend

FastAPI

SQLModel (ORM)

SQLite (PostgreSQL ready)

JWT Authentication

Groq LLM (LLaMA 3.1)

🏗️ System Architecture
Browser (React)
 ├── Bot Sidebar
 ├── Session Sidebar
 └── Chat Window
        ↓
REST API (FastAPI + JWT)
        ↓
Database (SQLModel)
        ↓
Groq AI (LLM)

🧠 Application Flow

User registers or logs in

JWT token stored in localStorage

User selects a bot

Creates a new chat session

Sends messages (optimistic UI)

Bot responds via Groq API

Messages are saved locally

Chat history persists on refresh

🗂️ Folder Structure
chatbot/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat.jsx
│   │   │   ├── sidebar.jsx
│   │   │   ├── botsidebar.jsx
│   │   │   └── protectedroute.jsx
│   │   ├── pages/
│   │   │   ├── login.jsx
│   │   │   ├── register.jsx
│   │   │   └── dashboard.jsx
│   │   ├── api/
│   │   │   └── index.js
│   │   └── routes/
│   │       └── AppRoutes.jsx
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── crud.py
│   ├── db.py
│   ├── seed_bots.py
│   └── routes/
│       ├── auth.py
│       └── bots.py
│
└── README.md

🔌 API Overview
Authentication

POST /auth/register

POST /auth/login

GET /auth/verify

Bots & Sessions

GET /bots

POST /bots/{bot_id}/sessions

GET /bots/{bot_id}/sessions

POST /bots/{bot_id}/sessions/{session_id}/message

DELETE /sessions/{session_id}

🛠️ Local Setup
Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python seed_bots.py
uvicorn main:app --reload


Backend runs at:
http://127.0.0.1:8000

Frontend
cd frontend
npm install
npm run dev


Frontend runs at:
http://localhost:5173

🔐 Environment Variables
Backend .env
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=sqlite:///chatbot.db

Frontend .env
VITE_API_URL=http://127.0.0.1:8000

🚀 Future Improvements

Backend-stored chat history (remove LocalStorage dependency)

WebSocket real-time streaming

User-created custom bots

Markdown & code block rendering

Conversation export (PDF / Markdown)

Analytics dashboard

Mobile-friendly UI

🧠 Why This Project Matters

This project demonstrates:

Clean full-stack architecture

Secure authentication practices

Real-world state management

API-driven UI design

Scalable backend design

Production-ready thinking

It’s an excellent portfolio-level project for:

Full-Stack Developer

Frontend Engineer

Backend Engineer

AI Application Developer

📜 License

Proprietary – Educational & Portfolio Use

👨‍💻 Author: Rahul U
Full-Stack Developer | React | FastAPI | AI Integrations
