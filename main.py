from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import detect_intent

from db import get_student, get_syllabus, get_classes_by_day
from utils import (
    parse_reg_no,
    calculate_sem,
    ask_llm,
    extract_day,
    parse_query,
    get_current_or_next_class
)

from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/student/{reg_no}/{section}")
def read_student(reg_no: str, section: str):
    student = get_student(reg_no)

    parsed = parse_reg_no(reg_no)
    sem = calculate_sem(parsed["year"])

    if student:
        return {
            "reg_no": student[0],
            "name": student[1],
            "branch": parsed["branch_code"],
            "year": parsed["year"],
            "semester": sem,
            "section": section.upper()
        }

    return {"error": "Student not found"}


@app.get("/ask")
def ask(query: str, reg_no: str, section: str):

    parsed_reg = parse_reg_no(reg_no)
    sem = calculate_sem(parsed_reg["year"])

    intent_data = detect_intent(query)

    intent = intent_data["intent"]
    subject = intent_data["subject"]
    unit = intent_data["unit"]

    # ---------------- TIMETABLE ----------------
    if intent == "timetable":
        day = extract_day(query)

        if not day:
            return {"response": "Specify a day like today, tomorrow, Monday etc."}

        classes = get_classes_by_day(
            branch_code=parsed_reg["branch_code"],
            sem=sem,
            section=section,
            day=day
        )

        if not classes:
            return {"response": "No classes found."}

        combined = "\n".join(
            [f"{c['time_slot']} - {c['subject']} ({c['room']})" for c in classes]
        )

        return {"response": combined}

    # ---------------- SYLLABUS ----------------
    elif intent == "syllabus":

        # ALL SUBJECTS CASE
        if subject is None:
            subjects = [
                "Communication Skills",
                "Engineering Mathematics-I",
                "Applied Physics"
            ]

            full_data = []

            for sub in subjects:
                data = get_syllabus(sub, sem=1)
                full_data.extend(data)

        else:
            full_data = get_syllabus(subject, sem=1, unit=unit)

        if not full_data:
            return {"response": "No syllabus found."}

        combined = "\n\n".join(
            [f"{row['subject']} - Unit {row['unit']}:\n{row['content']}" for row in full_data]
        )

        # explanation only if asked
        if "explain" in query.lower():
            answer = ask_llm(f"""
Explain this in simple terms:

{combined}
""")
            return {"response": answer}

        return {"response": combined}

    # ---------------- GENERAL ----------------
    else:
        return {"response": "Ask about timetable or syllabus."}