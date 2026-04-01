import fitz
import re


def extract_units_from_pdf(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)

    text = ""

    for page in doc[start_page:end_page]:
        text += page.get_text()

    # normalize text
    text = text.replace("\n", " ")

    # stop before textbooks
    stop_keywords = ["Text Books", "Syllabus: Lab", "Lab"]

    for keyword in stop_keywords:
        if keyword in text:
            text = text.split(keyword)[0]
            break

    # improved UNIT regex (multi-digit + case insensitive)
    pattern = r'UNIT\s*(\d+)\s*(.*?)(?=UNIT\s*\d+|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    units = {}

    for unit_num, content in matches:
        clean_content = " ".join(content.split())

        clean_content = re.sub(r'\bL-T-P\b.*', '', clean_content, flags=re.IGNORECASE)
        clean_content = re.sub(r'\bCredits\b.*', '', clean_content, flags=re.IGNORECASE)

        units[int(unit_num)] = clean_content.strip()

    return units


def generate_sql(sem, subject, units):
    values = []

    for unit, content in units.items():
        content = content.replace("'", "''")
        values.append(f"({sem}, '{subject}', {unit}, '{content}')")

    sql = f"""
INSERT INTO syllabus (sem, subject, unit, content)
VALUES
{",\n".join(values)};
"""
    return sql


# CHANGE ONLY THESE
pdf_path = "syllabus.pdf"
semester = 2
subject_name = "Engineering Mathematics-II "

start_page = 30
end_page = 31


units = extract_units_from_pdf(pdf_path, start_page, end_page)

if units:
    sql_query = generate_sql(semester, subject_name, units)
    print(sql_query)
else:
    print("No units extracted. Adjust page range or check PDF format.")