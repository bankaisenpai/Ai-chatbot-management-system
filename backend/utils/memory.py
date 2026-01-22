import re
from typing import Dict, Tuple, List


def extract_user_memory(message: str) -> Tuple[Dict[str, str], List[str]]:
    """
    Returns:
    - memory_to_save: { key: value }
    - memory_to_delete: [keys]
    """

    memory_to_save = {}
    memory_to_delete = []

    text = message.lower().strip()

    # ─────────────────────────────
    # FORGET INTENT
    # ─────────────────────────────
    if "forget my name" in text:
        memory_to_delete.append("name")

    if "forget my city" in text:
        memory_to_delete.append("city")

    if "forget my age" in text:
        memory_to_delete.append("age")

    # ─────────────────────────────
    # NAME (OVERWRITES AUTOMATICALLY)
    # ─────────────────────────────
    name_match = re.search(
        r"(my name is|i am|i'm)\s+([a-zA-Z]+)",
        text,
    )
    if name_match:
        memory_to_save["name"] = name_match.group(2).capitalize()

    # ─────────────────────────────
    # CITY
    # ─────────────────────────────
    city_match = re.search(
        r"(i live in|i am from)\s+([a-zA-Z ]+)",
        text,
    )
    if city_match:
        memory_to_save["city"] = city_match.group(2).strip().title()

    # ─────────────────────────────
    # AGE
    # ─────────────────────────────
    age_match = re.search(
        r"(i am|i'm)\s+(\d{1,3})\s*(years old|yo)?",
        text,
    )
    if age_match:
        memory_to_save["age"] = age_match.group(2)

    return memory_to_save, memory_to_delete
