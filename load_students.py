import pandas as pd
import mysql.connector

df = pd.read_excel("students.xlsx", header=None)

df = df.iloc[659:2595].copy()
df.columns = ["Roll Number", "Course Name", "Student Name"]

df = df.dropna(subset=["Roll Number"])
df["Roll Number"] = df["Roll Number"].astype(str).str.strip()
df["Student Name"] = df["Student Name"].astype(str).str.strip()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0909",
    database="unidex"
)

cursor = conn.cursor()

for _, row in df.iterrows():
    reg_no = row["Roll Number"]
    name = row["Student Name"]

    if not reg_no or reg_no.lower() == "nan":
        continue

    if "BCON" not in reg_no:
        continue

    branch_code = reg_no[2:6]
    joining_year = int(reg_no[:2])

    try:
        query = """
        INSERT INTO students (reg_no, name, branch_code, joining_year)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (reg_no, name, branch_code, joining_year))
    except:
        continue

conn.commit()
conn.close()

print("Students inserted successfully")