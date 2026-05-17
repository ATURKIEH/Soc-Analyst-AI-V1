from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
import sqlite3


class SOCChatBot:
    def __init__(self, db_path: str = 'incidents.db'):
        self.db_path = db_path
        self.llm     = ChatOllama(model='llama3.2:1b', temperature=0)

    def _get_incidents(self) -> str:
        conn   = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 50')
        rows   = cursor.fetchall()
        conn.close()
        if not rows:
            return "No incidents in database."
        lines = []
        for row in rows:
            lines.append(
                f"Type:{row[1]} | Risk:{row[4]} | "
                f"Severity:{row[5]} | Time:{row[7]}"
            )
        return "\n".join(lines)

    def _is_database_question(self, message: str) -> bool:
        keywords = [
            "threat", "attack", "incident", "detected", "scan",
            "dos", "probe", "r2l", "u2r", "risk", "severity",
            "how many", "any", "found", "history", "recent",
            "critical", "high", "medium", "low", "score"
        ]
        message_lower = message.lower()
        return any(kw in message_lower for kw in keywords)

    def chat(self, message: str, session_id: str = "default") -> str:
        if self._is_database_question(message):
            incidents = self._get_incidents()
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a SOC analyst assistant.
Here is the EXACT incident database. Read it carefully:

{incidents}

IMPORTANT RULES:
- The attack type is shown after "Type:" in each line
- Report EXACTLY what Type: shows — do not change or interpret it
- If Type shows DoS, say DoS. If Type shows Probe, say Probe.
- Never change an attack type to something else
- Timestamps, Risk scores and Severity must also be reported exactly as shown
- Plain English only, no JSON"""),
                ("human", "{message}")
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a SOC analyst. Answer cybersecurity questions concisely in plain English."),
                ("human", "{message}")
            ])

        chain    = prompt | self.llm
        response = chain.invoke({"message": message})
        return response.content