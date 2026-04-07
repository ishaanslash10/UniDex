import mysql.connector
from datetime import datetime
import os
from urllib.parse import urlparse

url = urlparse(os.getenv("DATABASE_URL"))

def get_connection():
    return mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],
        port=url.port
    )


def get_student(reg_no):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM students WHERE reg_no = %s"
    cursor.execute(query, (reg_no,))
    result = cursor.fetchone()

    conn.close()
    return result


def get_syllabus(subject, sem=None, unit=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM syllabus WHERE 1=1"
    params = []

    if subject is not None:
        query += " AND subject=%s"
        params.append(subject)

    if sem is not None:
        query += " AND sem=%s"
        params.append(sem)

    if unit is not None:
        query += " AND unit=%s"
        params.append(unit)

    cursor.execute(query, tuple(params))
    result = cursor.fetchall()

    conn.close()
    return result


def get_classes_by_day(branch_code, semester, section, day):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT subject, room, time_slot
    FROM time_table
    WHERE branch_code=%s AND semester=%s AND section=%s AND day=%s
    ORDER BY time_slot
    """

    cursor.execute(query, (branch_code, semester, section, day))
    result = cursor.fetchall()

    conn.close()
    return result

def get_all_subjects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT subject FROM syllabus")
    result = [row[0] for row in cursor.fetchall()]

    conn.close()
    return result