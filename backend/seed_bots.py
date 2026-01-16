#!/usr/bin/env python3
"""
Seed default bots into the database.
Run this ONCE to initialize the bot collection.

Usage:
    python -m backend.seed_bots
    
    OR from project root:
    python backend/seed_bots.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from backend.db import engine, init_db
from backend.models import Bot, User

# Initialize database schema
init_db()

db = Session(engine)

try:
    # Create a default system user if it doesn't exist
    system_user = db.exec(select(User)).first()
    
    if not system_user:
        print("ℹ️  No users found. Please register at least one user first.")
        print("   Visit: http://localhost:8000/docs → POST /auth/register")
        db.close()
        exit(1)
    
    # Check if bots already exist
    existing_bots = db.exec(select(Bot)).all()
    if existing_bots:
        print(f"ℹ️  Database already has {len(existing_bots)} bot(s). Skipping seed.")
        db.close()
        exit(0)


    OWNER_ID = 1
    # Define default bots
    bots_data = [
        {
            "owner_id": OWNER_ID,
            "name": "Support Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Helpful support assistant for customer service",
            "system_prompt": "You are a helpful support assistant. Answer customer questions clearly and provide solutions.",
            "temperature": 0.5,
        },
        {
            "owner_id": OWNER_ID,
            "name": "Tutor Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Patient teaching assistant for educational support",
            "system_prompt": "You are a patient and encouraging tutor. Explain concepts clearly with examples.",
            "temperature": 0.7,
        },
        {
            "owner_id": OWNER_ID,
            "name": "Fun Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Funny and friendly conversation partner",
            "system_prompt": "You are a funny and friendly assistant. Make conversations engaging and entertaining while being helpful.",
            "temperature": 0.9,
        },
    ]

    # Create bots - no owner_id means they're available to all users
    for bot_data in bots_data:
        bot = Bot(
            bot=Bot(**bot_data),  # Public bot - available to all users
            **bot_data
        )
        db.add(bot)
        print(f"✅ Created bot: {bot_data['name']}")

    db.commit()
    print(f"\n✅ Successfully seeded {len(bots_data)} bots to the database!")
    print(f"   Owner: {system_user.email}")

except Exception as e:
    print(f"❌ Error seeding bots: {e}")
    db.rollback()
    raise

finally:
    db.close()
