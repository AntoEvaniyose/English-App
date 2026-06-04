# FastAPI English Learning Platform

An AI-powered English Learning Platform built with FastAPI, PostgreSQL, SQLAlchemy, Gemini AI, ChromaDB Memory, JWT Authentication, and MCP (Model Context Protocol).

---

## Features

### Authentication

* User Registration
* User Login
* JWT Authentication
* Refresh Token Support
* Email Verification
* Password Management
* Role-Based Access Control

### User Management

* User Profile Management
* Profile Image Upload
* Update Personal Information
* Account Status Management
* Soft Delete Support

### Admin Panel

* User Listing
* User Details
* Block / Unblock Users
* User Monitoring

### Learning Content

* Learning Packages
* Package Listing
* Package Details
* Package Recommendations
* Search Functionality

### AI Assistant

Powered by Google Gemini.

Capabilities:

* English Learning Assistance
* Grammar Help
* Vocabulary Help
* Speaking Practice Guidance
* Package Recommendations
* Personalized Responses

### Long-Term Memory

Powered by ChromaDB.

Capabilities:

* Conversation Memory
* Context Retention
* Semantic Search
* Follow-Up Question Understanding

Example:

User:

> Show me available packages

AI:

> Spoken English Beginner
> Grammer Beginner

User:

> Tell me more about the first one

AI understands that "first one" refers to the previous package recommendation.

### MCP (Model Context Protocol)

Integrated MCP tools:

* User Tools
* Content Tools

Provides AI-accessible interfaces to application data and services.

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic

### Authentication

* JWT
* Refresh Tokens

### AI

* Google Gemini
* ChromaDB

### MCP

* FastMCP

### Storage

* PostgreSQL
* ChromaDB

### File Handling

* Static Files
* Media Uploads

---

## Project Structure

```text
app/
│
├── api/
│   └── v1/
│
├── core/
│   ├── config.py
│   ├── logger.py
│   └── exception_handler.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── admin.py
│       ├── user.py
│       └── content.py
│
├── middleware/
│
├── schemas/
│
├── services/
│   ├── admin/
│   ├── user/
│   └── ai/
│       ├── chat_service.py
│       ├── memory_service.py
│       └── tools.py
│
├── mcp/
│   ├── server.py
│   ├── user_tools.py
│   └── content_tools.py
│
├── utils/
│
├── static/
├── media/
└── tests/
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>

cd FASTAPI-SAMPLE-ENGLISH-APP
```

### Create Virtual Environment

```bash
python -m venv english_venv
```

### Activate Environment

Windows:

```bash
english_venv\Scripts\activate
```

Linux/Mac:

```bash
source english_venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
APP_NAME=FastAPI English App
DEBUG=True

DATABASE_URL=postgresql://username:password@localhost:5432/english_db

SECRET_KEY=your_secret_key

GROQ_API_KEY=your_GROQ_api_key
```

---

## Database Migration

Generate migration:

```bash
alembic revision --autogenerate -m "initial migration"
```

Apply migrations:

```bash
alembic upgrade head
```

---

## Running the Application

```bash
uvicorn main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## AI Chat Example

Request:

```json
{
  "message": "Show me available packages"
}
```

Response:

```json
{
  "reply": "Here are the available packages..."
}
```

Follow-Up:

```json
{
  "message": "Tell me more about the first one"
}
```

The AI uses ChromaDB memory to understand the context of the previous conversation.

---

## Logging

Application logs include:

* User Messages
* Gemini Requests
* Gemini Responses
* Tool Calls
* Memory Operations
* Errors

Example:

```text
[USER_MESSAGE]
[TOOL_CALL]
[TOOL_RESULT]
[GEMINI_CALL]
[GEMINI_RESPONSE]
[MEMORY_SAVED]
```

---

## MCP Endpoints

Mounted at:

```text
/mcp
```

Provides AI tools for:

* Users
* Packages
* Learning Content
