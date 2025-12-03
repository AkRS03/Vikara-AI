# app/api.py

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime
import random
from sqlalchemy.orm import Session
from app.agent import run_chat_agent  # Updated import

from database.db import SessionLocal
from database.db import Ticket  # Your DB model

ap = FastAPI(title="Triage API with DB")

# Table-free support staff
support_staff = [
    {"name": "Rahul", "phone": "1800-111-222"},
    {"name": "Aditi", "phone": "1800-333-444"},
    {"name": "Vikram", "phone": "1800-555-666"},
]

# -------------------------
# DB Session Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Request Models
# -------------------------
class CreateTicketRequest(BaseModel):
    username: str
    question: str

class ResolveTicketRequest(BaseModel):
    ticket_id: int
    resolved: bool


# -------------------------
# Create Ticket
# -------------------------
@ap.post("/tickets/create")
def create_ticket(req: CreateTicketRequest, db: Session = Depends(get_db)):

    result = run_chat_agent(req.question)
    agent = random.choice(support_staff)

    ticket = Ticket(
        username=req.username,
        question=req.question,
        summary=result["summary"],
        category=result["category"],
        severity=result["severity"],
        known_issue=result["known_issue"],
        related_issues=result["related_issues"],
        next_step=result["next_step"],
        status="open",
        created_at=datetime.utcnow(),
        assigned_agent=agent["name"]
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ticket_id": ticket.id,
        "response": result,        # contains chat_response
        "assigned_to": agent["name"]
    }


# -------------------------
# Resolve Ticket
# -------------------------
@ap.post("/tickets/resolve")
def resolve_ticket(req: ResolveTicketRequest, db: Session = Depends(get_db)):

    ticket = db.query(Ticket).filter(Ticket.id == req.ticket_id).first()

    if not ticket:
        return {"error": "Ticket not found"}

    if req.resolved:
        ticket.status = "resolved"
        ticket.resolved_at = datetime.utcnow()
        db.commit()
        return {"message": "Ticket resolved successfully"}

    agent = random.choice(support_staff)

    return {
        "message": "Please contact support",
        "agent_name": agent["name"],
        "phone": agent["phone"]
    }
