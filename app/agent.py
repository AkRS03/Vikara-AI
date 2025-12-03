# app/agent.py

import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# -------- Relative path to KB --------
# Relative path to KB, cross-platform safe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "app", "knowledge_base", "kb.json")

with open(KB_PATH, "r") as f:
    KB = json.load(f)
# -------- Groq LLM --------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("MODEL_NAME"),   # FIXED MODEL
    temperature=0.3
)

# -------- Simple KB search --------
def search_kb(query: str):
    q = query.lower()
    matches = []

    for item in KB:
        score = 0
        for word in item["symptoms"]:
            if word in q:
                score += 1
        if score > 0:
            matches.append((score, item))

    matches.sort(reverse=True, key=lambda x: x[0])
    return [m[1] for m in matches[:3]]


# -------- Structured Prompt --------
structured_prompt = PromptTemplate.from_template("""
You are a support triage agent.
User issue: "{question}"

1. Summarize the problem in 1–2 lines.
2. Categorize as one of: Bug, Billing, Login, Performance, How-To.
3. Severity must be: Low, Medium, High, Critical.

Respond ONLY in JSON:
{{
  "summary": "",
  "category": "",
  "severity": ""
}}
""")


# -------- Chatbot Prompt --------
chat_prompt = PromptTemplate.from_template("""
You are a friendly support assistant. Use the knowledge base results below to respond naturally and helpfully.

User question: "{question}"
Knowledge base matches: {kb_matches}

Instructions:
1. If you cannot answer the question due to lack of relevant data in the knowledge base, respond:
   "I can't help with this query. Please press NO on the 'issue resolved' button to get the customer support contact."
2. If you can answer the question with reference from the knowledge base, provide your answer clearly. 
   Then instruct the user: 
   - Press YES on the 'issue resolved' button if your answer solves the issue. 
   - Press NO if their issue is not resolved, and they will receive the contact of a customer support agent.
   
Respond in plain, concise text suitable for a chatbot.
""")



# -------- Structured agent logic --------
def run_agent(question: str):
    # ----- ASK LLM (structured) -----
    formatted = structured_prompt.format(question=question)
    response = llm.invoke(formatted)

    try:
        meta = json.loads(response.content)
    except:
        cleaned = response.content.strip().split("```")[-1]
        meta = json.loads(cleaned)

    # ----- SEARCH KB -----
    matches = search_kb(question)
    known_issue = len(matches) > 0

    # ------- NEXT ACTION -------
    if known_issue:
        next_step = "Attach related KB article and respond to user."
    elif meta["severity"] in ["High", "Critical"]:
        next_step = "Escalate to engineering team."
    else:
        next_step = "Ask user for more information."

    return {
        "summary": meta["summary"],
        "category": meta["category"],
        "severity": meta["severity"],
        "known_issue": known_issue,
        "related_issues": matches,
        "next_step": next_step
    }


# -------- Chatbot wrapper --------
def run_chat_agent(question: str):
    result = run_agent(question)

    kb_matches = [item.get("solution", "") for item in result["related_issues"]]
    formatted = chat_prompt.format(question=question, kb_matches=kb_matches)

    chat_response = llm.invoke(formatted).content

    result["chat_response"] = chat_response
    return result
