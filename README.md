# UniDex 

UniDex is an intelligent academic assistant that combines structured database queries with LLM capabilities to help students access timetable and syllabus information efficiently.

##  Features

  -  Timetable Query System  
  - Get schedule by day, section, or semester  

  -  Syllabus Management  
  - Automated extraction from PDF using PyMuPDF  
  - Unit-wise parsing using regex  
  - Stored in MySQL for fast retrieval  
  
  -  Intelligent Query Handling  
  - Intent-based routing (timetable / syllabus / general)  
  - LLM fallback for explanations  

##  Tech Stack

- FastAPI (Backend)
- MySQL (Database)
- PyMuPDF (PDF Parsing)
- Python (Core Logic)
- Gemini API (LLM)

##  How It Works

1. PDF syllabus → parsed using regex  
2. Data stored in structured DB  
3. User query → intent detection  
4. DB fetch or LLM response  

##  Example Queries

- "What is my timetable today?"
- "Give syllabus of AI"
- "Explain Unit 3 of Compiler Construction"

---

 Built as part of a smart academic assistant system (UniDex)