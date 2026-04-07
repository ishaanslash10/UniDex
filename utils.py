import requests
import re
from datetime import datetime, timedelta
import os
import json
from difflib import get_close_matches
from db import get_all_subjects

#  GLOBAL CACHE (PUT HERE)
subjects_cache = None


def match_subject(user_input: str):
    global subjects_cache

    # load only once
    if subjects_cache is None:
        subjects_cache = get_all_subjects()

    subject_map = {s.lower(): s for s in subjects_cache}

    match = get_close_matches(user_input.lower(), subject_map.keys(), n=1, cutoff=0.4)

    if match:
        return subject_map[match[0]]

    return None

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


# -------------------- CLASS LOGIC --------------------
def get_current_or_next_class(classes):
    now = datetime.now().time()

    for c in classes:
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

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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


# -------------------- DAY EXTRACTOR --------------------
def extract_day(query: str):
    query = query.lower()
    today = datetime.today()

    if "today" in query:
        return today.strftime("%A")

    if "tomorrow" in query:
        return (today + timedelta(days=1)).strftime("%A")

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

    match = re.search(r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", query)
    if match:
        target_day = days_map[match.group(1)]
        current_day = today.weekday()

        days_ahead = (target_day - current_day + 7) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead

        return (today + timedelta(days=days_ahead)).strftime("%A")

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


# -------------------- INTENT DETECTOR --------------------
def detect_intent(query: str):
    prompt = f"""
ONLY return valid JSON.

Classify into:
- timetable
- syllabus
- general

Also extract subject and unit.

Query: {query}

Format:
{{
  "intent": "...",
  "subject": "...",
  "unit": null
}}
"""

    try:
        response = ask_llm(prompt)
        cleaned = re.sub(r"```json|```", "", response).strip()
        data = json.loads(cleaned)

        return {
            "intent": data.get("intent"),
            "subject": data.get("subject"),
            "unit": data.get("unit")
        }

    except:
        return {
            "intent": "general",
            "subject": None,
            "unit": None
        }
    

def extract_semester(query: str):
    q = query.lower()

    sem_map = {
        "1": 1, "1st": 1, "first": 1,
        "2": 2, "2nd": 2, "second": 2,
        "3": 3, "3rd": 3, "third": 3,
        "4": 4, "4th": 4, "fourth": 4,
        "5": 5, "5th": 5, "fifth": 5,
        "6": 6, "6th": 6, "sixth": 6,
        "7": 7, "7th": 7, "seventh": 7,
        "8": 8, "8th": 8, "eighth": 8,
    }

    for key, val in sem_map.items():
        if f"{key} sem" in q or f"{key} semester" in q:
            return val

    return None


def match_subject(user_input: str):
    user_input = user_input.lower()

    subjects = get_all_subjects()  #  dynamic now
    subject_map = {s.lower(): s for s in subjects}

    match = get_close_matches(user_input, subject_map.keys(), n=1, cutoff=0.4)

    if match:
        return subject_map[match[0]]

    return None