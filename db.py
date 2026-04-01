import mysql.connector
from datetime import datetime


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0909",
        database="unidex"
    )


def get_student(reg_no):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM students WHERE reg_no = %s"
    cursor.execute(query, (reg_no,))
    result = cursor.fetchone()

    conn.close()
    return result


def get_today_class(branch_code, semester, section):
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%A")

    query = """
    SELECT subject, room, time_slot
    FROM time_table
    WHERE branch_code=%s AND semester=%s AND section=%s AND day=%s
    ORDER BY time_slot
    """

    cursor.execute(query, (branch_code, semester, section, today))
    result = cursor.fetchall()

    conn.close()
    return result


def get_syllabus(subject, sem=None, unit=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM syllabus WHERE subject=%s"
    params = [subject]

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