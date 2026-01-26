🔁 AI Provider Failure & Model Switching Guide
Purpose

This document explains how to handle AI service failures in this project and how to switch to a different LLM provider or API (OpenAI, Gemini, Claude, local models, etc.) with minimal code changes.

This ensures:

Business continuity

Zero frontend changes

Fast recovery from API bans, outages, or pricing changes

🚨 When Do You Need This?

You should follow this guide if:

❌ Groq API is down

❌ LLaMA model is deprecated

❌ API key is revoked or banned

❌ Rate limits are exceeded

❌ Pricing becomes unaffordable

❌ You want to upgrade models (GPT-4, Claude, Gemini)

❌ You want to run a local LLM

🧠 Current AI Architecture
Current Setup
Frontend (React)
     ↓
FastAPI Backend
     ↓
AI Client Wrapper (groq_client.py)
     ↓
Groq API (LLaMA 3.1)


Important:
👉 The frontend is completely AI-agnostic
👉 All AI logic lives in one backend file

This design makes switching models safe and easy.

📍 Single Point of Change (Critical)

All AI calls are isolated in:

backend/ai/groq_client.py


This file:

Receives conversation messages

Sends them to the AI model

Returns the AI response text

⚠️ DO NOT spread AI logic across routes
⚠️ Always keep one AI client file

🔄 Strategy for Switching AI Providers
Step 1: Keep the Interface the Same

All AI clients must expose the same function:

def generate_reply(messages: list[str]) -> str:
    ...


As long as this function returns a string, nothing else breaks.

🔁 Option 1: Switch to OpenAI (GPT-4 / GPT-3.5)
Install Dependency
pip install openai

Create New Client
backend/ai/openai_client.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_reply(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": m} for m in messages],
        temperature=0.7,
    )
    return response.choices[0].message.content

Switch Import (1 line change)
# from ai.groq_client import generate_reply
from ai.openai_client import generate_reply

🔁 Option 2: Switch to Google Gemini
Install Dependency
pip install google-generativeai

Client File
backend/ai/gemini_client.py

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def generate_reply(messages):
    prompt = "\n".join(messages)
    response = model.generate_content(prompt)
    return response.text

🔁 Option 3: Switch to Anthropic Claude
pip install anthropic

from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_reply(messages):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": "\n".join(messages)}],
        max_tokens=500
    )
    return response.content[0].text

🖥️ Option 4: Use a Local LLM (Ollama)
Install Ollama

👉 https://ollama.com

ollama pull llama3

Local Client
backend/ai/local_llm.py

import requests

def generate_reply(messages):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": "\n".join(messages),
            "stream": False
        }
    )
    return response.json()["response"]


✅ No API keys
✅ No internet needed
⚠️ Slower than cloud models

🛡️ Failover Strategy (Recommended)

You can implement automatic fallback:

def generate_reply(messages):
    try:
        return groq_generate(messages)
    except Exception:
        return openai_generate(messages)


This ensures:

Zero downtime

Graceful degradation

Production reliability

⚠️ Common Failure Scenarios & Fixes
Problem	Cause	Solution
401 Unauthorized	API key revoked	Replace key
429 Rate Limit	Too many requests	Add retry / fallback
503 Service Down	Provider outage	Switch provider
Empty responses	Model deprecated	Update model name
High latency	Model overload	Reduce temperature / tokens
🔐 Environment Variable Switching
.env Example
AI_PROVIDER=groq
GROQ_API_KEY=xxxx
OPENAI_API_KEY=xxxx
GEMINI_API_KEY=xxxx


You can dynamically choose provider:

provider = os.getenv("AI_PROVIDER")

if provider == "openai":
    from ai.openai_client import generate_reply
elif provider == "gemini":
    from ai.gemini_client import generate_reply
else:
    from ai.groq_client import generate_reply

✅ Best Practices (Important)

✔ Always isolate AI logic
✔ Never hardcode API keys
✔ Keep frontend unaware of AI provider
✔ Log AI errors clearly
✔ Add retry + timeout
✔ Design for replacement, not dependency

📌 Final Note

This project is AI-provider independent by design.

If any AI model fails, you can:

Replace it in under 10 minutes

Without touching frontend code

Without breaking existing users

This is production-grade engineering.
