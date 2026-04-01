import requests
import re
from datetime import datetime, timedelta


# -------------------- REG PARSER --------------------
def parse_reg_no(reg_no):
    year = int(reg_no[:2])
    branch_code = reg_no[2:6]
    roll = reg_no[6:]

    return {
        "year": year,
        "branch_code": branch_code,
        "roll": roll
    }


# -------------------- SEM CALCULATOR --------------------
def calculate_sem(joining_year):
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    full_year = 2000 + joining_year
    year_diff = current_year - full_year

    sem = year_diff * 2 + 1

    if current_month <= 6:
        sem -= 1

    return sem


# -------------------- SYLLABUS TYPE --------------------
def get_syllabus_type(section: str):
    section = section.upper()

    if section in ["SA", "SB", "SC"]:
        return "aiml_ibm"

    if len(section) == 1:
        return "core"

    return "unknown"


# -------------------- CLASS LOGIC --------------------
def get_current_or_next_class(classes):
    now = datetime.now().time()

    for c in classes:
        # supports BOTH tuple and dict
        if isinstance(c, dict):
            subject = c["subject"]
            room = c["room"]
            time_slot = c["time_slot"]
        else:
            subject, room, time_slot = c

        start, end = time_slot.split("-")

        start_time = datetime.strptime(start.strip(), "%H:%M").time()
        end_time = datetime.strptime(end.strip(), "%H:%M").time()

        if start_time <= now <= end_time:
            return f"You are currently in {subject} in {room} (till {end})"

        if now < start_time:
            return f"Your next class is {subject} in {room} at {start}"

    return "No more classes for today"


# -------------------- LLM (GEMINI) --------------------
from google import genai

client = genai.Client(api_key="AIzaSyBjkcyggzT3u0AmP7WOsJls2TY-0j2Ufvw")

def ask_llm(prompt: str):
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        return "AI is not responding right now."


# -------------------- SUBJECT MAP --------------------
SUBJECT_MAP = {
    "communication": "Communication Skills",
    "english": "Communication Skills",

    "math": "Engineering Mathematics-I",
    "maths": "Engineering Mathematics-I",
    "engineering mathematics": "Engineering Mathematics-I",

    "physics": "Applied Physics",
    "applied physics": "Applied Physics",
    "quantum": "Applied Physics",

    "daa": "Design and Analysis of Algorithms",
    "algorithm": "Design and Analysis of Algorithms",
}


# -------------------- QUERY PARSER --------------------
def parse_query(query: str):
    query = query.lower()

    unit_match = re.search(r'unit\s*(\d+)', query)
    unit = int(unit_match.group(1)) if unit_match else None

    subject = None
    for key in SUBJECT_MAP:
        if key in query:
            subject = SUBJECT_MAP[key]
            break

    if any(word in query for word in ["explain", "samjha", "understand"]):
        mode = "explain"
    else:
        mode = "fetch"

    return {
        "subject": subject,
        "unit": unit,
        "mode": mode
    }


# -------------------- DAY EXTRACTOR (UPGRADED) --------------------
def extract_day(query: str):
    query = query.lower()
    today = datetime.today()

    # TODAY
    if "today" in query:
        return today.strftime("%A")

    # TOMORROW
    if "tomorrow" in query:
        return (today + timedelta(days=1)).strftime("%A")

    # DAY NAMES
    days_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    for day in days_map:
        if day in query:
            return day.capitalize()

    # NEXT MONDAY
    match = re.search(r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", query)
    if match:
        target_day = days_map[match.group(1)]
        current_day = today.weekday()

        days_ahead = (target_day - current_day + 7) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead

        return (today + timedelta(days=days_ahead)).strftime("%A")

    # DATE (extract inside sentence)
    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]+|\d{1,2}/\d{1,2}(/\d{2,4})?)', query)

    if date_match:
        date_str = date_match.group(1)

        for fmt in ["%d %B %Y", "%d %B", "%d/%m/%Y", "%d/%m"]:
            try:
                date = datetime.strptime(date_str, fmt)
                if "%Y" not in fmt:
                    date = date.replace(year=today.year)
                return date.strftime("%A")
            except:
                continue

    return None

import json
import re

def detect_intent(query: str):
    prompt = f"""
ONLY return valid JSON. No explanation.

Classify the query into:
- timetable
- syllabus
- general

Also extract:
- subject
- unit

Format:
{{
  "intent": "...",
  "subject": "...",
  "unit": null
}}

Query: {query}
"""

    try:
        response = ask_llm(prompt)

        # CLEAN RESPONSE
        cleaned = re.sub(r"```json|```", "", response).strip()

        data = json.loads(cleaned)

        return {
            "intent": data.get("intent"),
            "subject": data.get("subject"),
            "unit": data.get("unit")
        }

    except Exception as e:
        print("Intent error:", e)
        return {
            "intent": "general",
            "subject": None,
            "unit": None
        }