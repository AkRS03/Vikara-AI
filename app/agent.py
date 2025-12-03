import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


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

# KB search function

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



chat_prompt = PromptTemplate.from_template("""
You are a friendly support assistant. Use the knowledge base results below to answer the user's question naturally and helpfully.

User question: "{question}"
Knowledge base matches: {kb_matches}

Guidelines:
1. If the knowledge base contains useful or partially relevant information, use it to craft a helpful, conversational answer. Do NOT default to saying you cannot help unless there is truly no relevant information at all.
2. Only if there is absolutely no relevant data in the knowledge base, respond briefly:
   "I can't help with this query using the available information. Please press NO on the 'issue resolved' button to get the customer support contact."
3. Whenever you provide an answer (even partial), end with a friendly line:
   "If this helped, please press YES on the 'issue resolved' button. If not, press NO and you'll receive the customer care contact."

Your tone should be warm, concise, supportive, and conversational.
Respond in plain text suitable for a chatbot.
""")


def run_agent(question: str):

    formatted = structured_prompt.format(question=question)
    response = llm.invoke(formatted)

    try:
        meta = json.loads(response.content)
    except:
        cleaned = response.content.strip().split("```")[-1]
        meta = json.loads(cleaned)


    matches = search_kb(question)
    known_issue = len(matches) > 0

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


def run_chat_agent(question: str):
    result = run_agent(question)

    kb_matches = [item.get("solution", "") for item in result["related_issues"]]
    formatted = chat_prompt.format(question=question, kb_matches=kb_matches)

    chat_response = llm.invoke(formatted).content

    result["chat_response"] = chat_response
    return result
