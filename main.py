from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import (
    get_classes_by_day,
    get_student,
    get_syllabus
)

from utils import (
    ask_llm,
    calculate_sem,
    detect_intent,
    extract_day,
    extract_semester,
    is_small_talk,
    parse_reg_no,
    web_search
)

# ============================================================
# FastAPI Application Setup
# ============================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# In-Memory Conversation Storage
# ============================================================

conversation_memory = {}

session_memory = {}


# ============================================================
# Request Models
# ============================================================

class QueryRequest(BaseModel):
    query: str
    reg_no: str
    section: str


# ============================================================
# Session Utilities
# ============================================================

def save_session(reg_no, query, intent):

    session_memory[reg_no] = {
        "last_query": query,
        "last_intent": intent
    }


# ============================================================
# Student Endpoint
# ============================================================

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


# ============================================================
# Main Chat Endpoint
# ============================================================

@app.post("/ask")
def ask(data: QueryRequest):

    query = data.query
    reg_no = data.reg_no
    section = data.section

    if reg_no not in conversation_memory:
        conversation_memory[reg_no] = []

    # ========================================================
    # Session Context
    # ========================================================

    session = session_memory.get(
        reg_no,
        {
            "last_query": None,
            "last_intent": None
        }
    )

    parsed_reg = parse_reg_no(reg_no)

    sem = calculate_sem(parsed_reg["year"])

    forced_sem = extract_semester(query)

    if forced_sem:
        sem = forced_sem

    q = query.lower()

    # ========================================================
    # Context Merge For Timetable Follow-Ups
    # ========================================================

    if session["last_intent"] == "timetable":

        if (
            session["last_query"]
            and any(
                word in q
                for word in [
                    "today",
                    "tomorrow",
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday"
                ]
            )
        ):

            if len(query.split()) <= 2:

                query = session["last_query"] + " " + query

                q = query.lower()

    # ========================================================
    # Date Queries
    # ========================================================

    if "date" in q:

        today = datetime.now().strftime("%d %B %Y")

        save_session(reg_no, query, "general")

        return {
            "response": f"Today's date is {today}."
        }

    # ========================================================
    # Time Queries
    # ========================================================

    if "time" in q:

        now = datetime.now().strftime("%I:%M %p")

        save_session(reg_no, query, "general")

        return {
            "response": f"Current time is {now}."
        }

    # ========================================================
    # Small Talk
    # ========================================================

    if is_small_talk(query):

        response = ask_llm(f"""
        You are UniDex AI.

        Respond naturally and casually to the user's message.

        Keep it short and conversational.

        User:
        {query}
        """)

        return {"response": response}

    # ========================================================
    # Intent Detection
    # ========================================================

    if (
        any(
            word in q
            for word in [
                "class",
                "classes",
                "timetable",
                "schedule"
            ]
        )
        or (
            "today" in q
            and any(
                word in q
                for word in [
                    "class",
                    "schedule"
                ]
            )
        )
    ):

        intent = "timetable"

        subject = None

        unit = None

    elif any(
        word in q
        for word in [
            "syllabus",
            "unit",
            "subject"
        ]
    ):

        intent_data = detect_intent(query)

        intent = "syllabus"

        subject = intent_data["subject"]

        unit = intent_data["unit"]

        # ====================================================
        # Prevent General Subject Conversations
        # From Triggering Syllabus Intent
        # ====================================================

        if intent == "syllabus" and subject is None:

            syllabus_keywords = [
                "syllabus",
                "show syllabus",
                "full syllabus",
                "semester syllabus"
            ]

            if not any(
                keyword in q
                for keyword in syllabus_keywords
            ):

                intent = "general"

    else:

        intent_data = detect_intent(query)

        intent = intent_data["intent"]

        subject = intent_data["subject"]

        unit = intent_data["unit"]

    # ========================================================
    # Timetable Queries
    # ========================================================

    if intent == "timetable":

        day = extract_day(query)

        if not day:

            save_session(reg_no, query, intent)

            return {
                "response": (
                    "Specify a day like today, "
                    "tomorrow, Monday etc."
                )
            }

        classes = get_classes_by_day(
            branch_code=parsed_reg["branch_code"],
            semester=sem,
            section=section,
            day=day
        )

        if not classes:

            save_session(reg_no, query, intent)

            return {
                "response": "No classes!!!."
            }

        formatted = []

        for i, c in enumerate(classes, 1):

            formatted.append(
                f"{i}. "
                f"{c['time_slot']} → "
                f"{c['subject']} in "
                f"{c['room']} "
                f"({c['faculty']})"
            )

        combined = (
            "Here is your schedule:\n\n"
            + "\n".join(formatted)
            + "\n\nGood luck for your classes!"
        )

        save_session(reg_no, query, intent)

        return {"response": combined}

    # ========================================================
    # Syllabus Queries
    # ========================================================

    elif intent == "syllabus":

        if subject is None:

            full_data = get_syllabus(
                None,
                sem=sem
            )

            if not full_data:

                full_data = get_syllabus(None)

        else:

            full_data = get_syllabus(
                subject,
                sem=sem,
                unit=unit
            )

            if not full_data:

                full_data = get_syllabus(
                    subject,
                    unit=unit
                )

        if not full_data:

            save_session(reg_no, query, intent)

            return {
                "response": "No syllabus found."
            }

        subject_name = full_data[0]["subject"]

        combined = f"{subject_name}\n\n"

        for row in full_data:

            combined += (
                f"Unit {row['unit']}:\n"
                f"{row['content']}\n\n"
            )

        # ====================================================
        # Explanation Mode
        # ====================================================

        if "explain" in query.lower():

            answer = ask_llm(f"""
            You are a helpful teacher.

            The following is syllabus content.

            IMPORTANT INSTRUCTIONS:
            - Do NOT explain unit-wise.
            - Break everything into individual topics.
            - For EACH topic, give a separate explanation.
            - Keep explanations simple and clear.

            Now explain:

            {combined}
            """)

            save_session(reg_no, query, intent)

            return {"response": answer}

        save_session(reg_no, query, intent)

        return {"response": combined}

    # ========================================================
    # General Queries
    # ========================================================

    history = "\n".join(
        conversation_memory[reg_no][-4:]
    )

    save_session(reg_no, query, intent)

    web_data = web_search(query)

    prompt = f"""
    You are UniDex AI.

    Answer the user's question naturally and briefly using the web data.

    Do NOT copy full articles.
    Do NOT give unnecessary details.
    Keep the answer clean and conversational.
    Do NOT copy URLs.
    Do NOT dump articles.
    Keep the answer short and clean.

    Use the conversation history to understand context.

    CONVERSATION HISTORY:
    {history}

    WEB DATA:
    {web_data}

    QUESTION:
    {query}
    """

    answer = ask_llm(prompt)

    conversation_memory[reg_no].append(
        f"User: {query}"
    )

    conversation_memory[reg_no].append(
        f"Assistant: {answer}"
    )

    return {"response": answer}