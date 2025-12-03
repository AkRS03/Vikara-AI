# database/db.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    summary = Column(Text)
    category = Column(String(50))
    severity = Column(String(20))
    known_issue = Column(String(10))
    related_issues = Column(JSON)
    next_step = Column(Text)
    assigned_agent = Column(String(100))   # <-- ADD THIS
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime)