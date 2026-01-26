from sqlmodel import Session, select
from backend.db import engine, init_db
from backend.models import Bot, User

init_db()
db = Session(engine)

try:
    existing_bots = db.exec(select(Bot)).all()
    if existing_bots:
        print(f"ℹ️ {len(existing_bots)} bots already exist. Skipping seed.")
        exit(0)

    # Create bots as system bots (owner_id=None) so all users can access them
    bots_data = [
        {
            "owner_id": None,
            "name": "Support Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Helpful support assistant",
            "system_prompt": "You are a helpful support assistant.",
            "temperature": 0.5,
        },
        {
            "owner_id": None,
            "name": "Tutor Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Teaching assistant",
            "system_prompt": "You are a patient tutor.",
            "temperature": 0.7,
        },
        {
            "owner_id": None,
            "name": "Fun Bot",
            "model": "llama-3.1-8b-instant",
            "description": "Fun conversational bot",
            "system_prompt": "You are funny and friendly.",
            "temperature": 0.9,
        },
    ]

    for bot_data in bots_data:
        bot = Bot(**bot_data)
        db.add(bot)
        print(f"✅ Created bot: {bot_data['name']}")

    db.commit()
    print("✅ Bot seeding completed")

except Exception as e:
    db.rollback()
    raise

finally:
    db.close()
