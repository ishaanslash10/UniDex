import os
from datetime import datetime

import mysql.connector

# ============================================================
# Database Connection
# ============================================================

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# ============================================================
# Student Queries
# ============================================================

def get_student(reg_no):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    SELECT *
    FROM students
    WHERE reg_no = %s
    """

    cursor.execute(query, (reg_no,))

    result = cursor.fetchone()

    conn.close()

    return result


# ============================================================
# Syllabus Queries
# ============================================================

def get_syllabus(subject, sem=None, unit=None):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM syllabus
    WHERE 1=1
    """

    params = []

    if subject is not None:

        query += " AND subject = %s"

        params.append(subject)

    if sem is not None:

        query += " AND sem = %s"

        params.append(sem)

    if unit is not None:

        query += " AND unit = %s"

        params.append(unit)

    cursor.execute(query, tuple(params))

    result = cursor.fetchall()

    conn.close()

    return result


# ============================================================
# Timetable Queries
# ============================================================

def get_classes_by_day(
    branch_code,
    semester,
    section,
    day
):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        subject,
        room,
        time_slot,
        faculty
    FROM time_table
    WHERE branch_code = %s
    AND semester = %s
    AND section = %s
    AND day = %s
    ORDER BY time_slot
    """

    cursor.execute(
        query,
        (
            branch_code,
            semester,
            section,
            day
        )
    )

    result = cursor.fetchall()

    conn.close()

    return result


# ============================================================
# Subject Utilities
# ============================================================

def get_all_subjects():

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    SELECT DISTINCT subject
    FROM syllabus
    """

    cursor.execute(query)

    result = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return result