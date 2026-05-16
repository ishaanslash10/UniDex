# UniDex

UniDex is an AI-powered academic assistant that combines structured database retrieval with Large Language Model (LLM) capabilities to provide intelligent and conversational access to academic information.

The system is designed to help students interact naturally with academic data instead of navigating traditional portals or static systems. UniDex can retrieve timetable and syllabus information, explain academic topics using AI, handle conversational interactions, and generate web-enhanced responses through integrated search capabilities.

---

## Features

### Intelligent Query Routing
- Intent-based query detection
- Dynamic routing between database retrieval and AI generation
- Support for timetable, syllabus, and general queries
- Context-aware conversational handling

### Timetable Management
- Day-wise timetable retrieval
- Section and semester-based filtering
- Natural language day extraction
- Follow-up query understanding using session memory

### Syllabus Management
- PDF syllabus extraction using PyMuPDF
- Regex-based unit parsing
- Structured MySQL storage
- Unit-wise syllabus retrieval
- Full semester syllabus support

### AI-Powered Assistance
- Gemini API integration
- Topic explanations and simplification
- Conversational AI responses
- Educational query handling

### Web Search Integration
- Tavily Search API integration
- AI-enhanced web responses
- Current information retrieval
- Conversational summarization

### Frontend Experience
- AI-inspired modern interface
- Dynamic loading states
- Interactive chat-based UI
- Session persistence
- Responsive design

---

## Example Queries

### Timetable Queries
- What are my classes today?
- Show Monday schedule
- Do I have classes tomorrow?

### Syllabus Queries
- Show syllabus of Compiler Construction
- Give Unit 3 of DAA
- Show full syllabus

### AI Queries
- Explain Dynamic Programming
- What is DBMS normalization?
- Explain Unit 2 of Operating Systems

---

## Tech Stack

### Backend
- FastAPI
- Python

### Database
- MySQL

### AI & NLP
- Gemini API
- Tavily Search API

### Frontend
- HTML
- CSS
- JavaScript

### PDF Processing
- PyMuPDF
- Regex Parsing

---

## System Workflow

1. User sends a query through the frontend
2. Backend performs intent detection
3. Query is dynamically routed
4. Database retrieval or AI processing occurs
5. Response is formatted conversationally
6. Final response is returned to the user

---

## Project Structure

```text
UniDex/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── main.py
├── utils.py
├── db.py
├── requirements.txt
├── .env
└── README.md

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=unidex
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/UniDex.git
cd UniDex
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend Server

```bash
uvicorn main:app --reload
```

---

## Future Improvements

- Authentication system
- Voice interaction
- Advanced conversational memory
- Multi-university support
- Advanced RAG integration
- Deployment infrastructure

---

## Conclusion

UniDex demonstrates how traditional academic systems can be transformed into intelligent conversational platforms using AI, structured databases, and modern web technologies.

By combining database retrieval, AI-generated explanations, conversational interaction, and web-enhanced responses, UniDex delivers a scalable and interactive academic assistant experience.