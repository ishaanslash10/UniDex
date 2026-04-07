from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_semester
from datetime import datetime

from db import get_student, get_syllabus, get_classes_by_day
from utils import (
    parse_reg_no,
    calculate_sem,
    ask_llm,
    extract_day,
    detect_intent
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/student/{reg_no}/{section}")
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


@app.post("/ask")
def ask(query: str, reg_no: str, section: str):

    parsed_reg = parse_reg_no(reg_no)
    sem = calculate_sem(parsed_reg["year"])

    forced_sem = extract_semester(query)
    if forced_sem:
        sem = forced_sem

    q = query.lower()

    # -------- DATE --------
    if "date" in q:
        today = datetime.now().strftime("%d %B %Y")
        return {"response": f"Today's date is {today}."}

    # -------- TIME --------
    if "time" in q:
        now = datetime.now().strftime("%I:%M %p")
        return {"response": f"Current time is {now}."}

    if any(word in q for word in ["class", "classes", "timetable", "schedule"]) or \
        ("today" in q and any(word in q for word in ["class", "schedule"])):
        intent = "timetable"
        subject = None
        unit = None

    elif any(word in q for word in ["syllabus", "unit", "subject"]):
        intent_data = detect_intent(query)
        intent = "syllabus"
        subject = intent_data["subject"]
        unit = intent_data["unit"]

    else:
        intent_data = detect_intent(query)
        intent = intent_data["intent"]
        subject = intent_data["subject"]
        unit = intent_data["unit"]

    # -------- TIMETABLE --------
    if intent == "timetable":
        day = extract_day(query)

        if not day:
            return {"response": "Specify a day like today, tomorrow, Monday etc."}

        classes = get_classes_by_day(
            branch_code=parsed_reg["branch_code"],
            semester=sem,
            section=section,
            day=day
        )

        if not classes:
            return {"response": "No classes!!!."}

        formatted = []

        for i, c in enumerate(classes, 1):
            formatted.append(
                f"{i}. {c['time_slot']} → {c['subject']} in {c['room']} ({c['faculty']})"
            )

        combined = "Here is your schedule:\n\n" + "\n".join(formatted) + "\n\nGood luck for your classes!"

        return {"response": combined}

    # -------- SYLLABUS --------
    elif intent == "syllabus":
        print("DEBUG → subject:", subject)
        print("DEBUG → sem:", sem)
        print("DEBUG → unit:", unit)

        if subject is None:
            full_data = get_syllabus(None, sem=sem)

        else:
            full_data = get_syllabus(subject, sem=sem, unit=unit)

        if not full_data:
            return {"response": "No syllabus found."}

        combined = "\n\n".join(
            [f"{row['subject']} - Unit {row['unit']}:\n{row['content']}" for row in full_data]
        )

        if "explain" in query.lower():
            answer = ask_llm(f"""
            You are a helpful teacher.

            The following is syllabus content.

            IMPORTANT INSTRUCTIONS:
            - Do NOT explain unit-wise.
            - Break everything into individual topics.
            - For EACH topic, give a separate explanation.
            - Keep explanations simple and clear.
            - Format output like:

            Topic: <name>
            Explanation: <simple explanation>

            Now explain:

            {combined}
            """)
            return {"response": answer}
        print("FINAL SEM USED:", sem)
        return {"response": combined}

    return {"response": ask_llm(query)}