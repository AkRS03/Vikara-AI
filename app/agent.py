# app/agent.py

import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# -------- Load KB --------
with open(r"C:/Users/Lenovo/Desktop/Vikara AI/knowledge_base/kb.json") as f:
    KB = json.load(f)

# -------- Groq LLM --------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv('MODEL_NAME'),   # FIXED MODEL
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


# -------- Prompt (ESCAPED JSON) --------
prompt = PromptTemplate.from_template("""
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


# -------- Main Agent Logic --------
def run_agent(question: str):

    # ----- ASK LLM -----
    formatted = prompt.format(question=question)
    response = llm.invoke(formatted)

    try:
        meta = json.loads(response.content)
    except:
        # fallback if model adds text
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
