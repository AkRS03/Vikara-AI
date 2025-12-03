# Vikara AI – Support Ticket Agent

This project is an end-to-end AI-powered support assistant capable of answering user queries, creating tickets, assigning agents, and storing all activity in a PostgreSQL database. It provides:

A FastAPI backend with a reasoning agent.

A lightweight knowledge base.

A Streamlit frontend.

Docker support for both frontend and backend.

A PostgreSQL database with ticket logging.

## Project Structure
Vikara AI/ <br>
│<br>
├── app/<br>
│   ├── api.py                # FastAPI backend<br>
│   ├── agent.py              # LangChain agent logic<br>
│   ├── Dockerfile            # Backend Dockerfile<br>
│   │<br>
│   └── knowledge_base/<br>
│       └── kb.json           # Domain Knowledge Base<br>
│<br>
├── database/<br>
│   ├── db.py                 # SQLAlchemy engine + session<br>
│   ├── db_init.py            # Script to initialize new DB tables<br>
│<br>
├── frontend/<br>
│   ├── app.py                # Main Streamlit interface<br>
│   ├── streamlit.py          # Testing file (kept intentionally)<br>
│   └── Dockerfile            # Frontend Dockerfile<br>
│<br>
├── requirements.txt          # Python dependencies<br>
├── database_view.py          # Utility script to inspect tickets (snippet added below)<br>
│<br>
└── README.md                 # Project documentation<br>

# Features
* Backend (FastAPI)

* Receives user questions.

* Summarizes the issue and categorizes it.

* Associates relevant KB items.

* Creates structured support tickets.

* Stores all tickets in PostgreSQL.

* Exposes endpoints for ticket creation and retrieval.

* Knowledge Base

* Simple JSON file (kb.json) inside app/knowledge_base/.

* Loaded by the agent to cross-reference similar issues.

* Frontend (Streamlit)

* Clean interface for inputting queries.

* Displays agent responses and summaries.

* Sends ticket data to the backend API.

# Database

PostgreSQL schema created by running database/db_init.py.

Stores:

* username

* question

* category

* summary

* severity

* known_issue flag

* related issues (JSON)

* next steps

* assigned agent

* timestamps
## A view of the database:
   id                username  ...                      created_at                        resolved_at<br>
0   1       Shashank Raj  ... 2025-12-03 06:29:13.026699 2025-12-03 06:29:29.944066<br>
1   2     Ravindra Kumar  ... 2025-12-03 06:35:12.049820                        NaT<br>
2   3  Akshat Raj Sharma  ... 2025-12-03 09:44:25.597374 2025-12-03 09:44:38.118552<br>
3   4     Ravindra Kumar  ... 2025-12-03 12:02:29.012427                        NaT<br>
4   5      Swati Prakash  ... 2025-12-03 12:52:50.708414                        NaT<br>
5   6    Usha Rani Singh  ... 2025-12-03 13:04:04.789265                        NaT<br>
<br>
[6 rows x 13 columns]

These entries were obtained upon testing and sharing the project with my family, I can share an excel of these reports if asked for, I encourage the team of Vikara AI to send in their own queries as well and I can show those entries too in the aforementioned excel sheet.
