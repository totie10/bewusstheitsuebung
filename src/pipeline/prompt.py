from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """\
Du bist ein präziser Annotator.
Du erhältst eine Liste von Nachrichten (Gesprächsverlauf).
Die letzte Nachricht ist das Ziel, das du genau einer Bewusstheitsebene zuordnest.

Regeln:
- Nutze den Kontext der vorherigen Nachrichten, aber klassifiziere ausschließlich die letzte Nachricht.
- Gib **nur** eine der vier Klassen als strukturiertes Feld im bereitgestellten Schema zurück.
"""

system_prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "Nachrichtenverlauf:\n{context_text}\n\nZiel-Nachricht:\n{target_text}")]
)
