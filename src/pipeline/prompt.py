from langchain_core.prompts import ChatPromptTemplate

from pipeline.schema import ConsciousnessLevel


def build_schema_description() -> str:
    """Erstellt eine textuelle Beschreibung aller Felder aus ConsciousnessLevel für das LLM."""
    lines = ["Strukturelle Spezifikation (Beschreibung der Felder):\n"]
    for name, field in ConsciousnessLevel.model_fields.items():
        desc = field.description or ""
        type_name = getattr(field.annotation, "__name__", str(field.annotation))
        lines.append(f"- {name} ({type_name}):\n{desc}\n")
    return "\n".join(lines)


beschreibung_bewusstheitsebenen = build_schema_description()

SYSTEM_PROMPT = f"""\
Du bist ein präziser Annotator.
Du erhältst eine Liste von Nachrichten (Gesprächsverlauf).
Die letzte Nachricht ist das Ziel, das du genau einer Bewusstheitsebene zuordnest.

Wähle genau **eine** der Klassen:
gedanke, koerperempfindung, aufregung, gefuehl, sinken, tiefere_erfahrung, unklar.

Gefühle sind etwas anderes als Körperempfindungen. Körperempfindungen sind: den Energiestrom zu spüren, den Herzschlag,
den Atem sowie alles, was im und am Körper spürbar ist, wie ein Vibrieren, Jucken, Pochen, den Wind auf der Haut,
den Druck im Brustkorb, die sexuelle Erregung, den Schweißausbruch.

Ich fühle einen Druck in der Brust. Ich fühle eine Anspannung im Bauch. Ich spüre mein Herz schneller schlagen.« 
Das alles sind Körperempfindungen, keine Gefühle.

Die wichtigsten Gefühle sind: Freude, Schmerz, Heiterkeit, Trauer, Wut, Angst, Verzweiflung, Scham, Ekel.

Von den Gefühlen gibt es auch Abstufungen, am Beispiel der Wut sind das folgende: ungehalten sein, sich genervt fühlen,
aufgebracht sein, Ärger, Groll, Zorn und Hass. Sie sind nicht nur nach Intensität abgestuft, sondern auch immer
unterschiedlich ausgerichtet. Der Zorn weiß genau, gegen wen und was er sich richtet; der Hass ist mehr als Wut, weil er
nicht nur etwas abwehren, sich verteidigen und etwas durchsetzen möchte, sondern weil es den, auf den der Hass sich
richtet, auch zerstören will.

Bei der Angst gibt es folgende Abstufungen: Unsicherheit, Ängstlichkeit, Angst, Schrecken und Panik.

Weiter gibt es einige zusammengesetzte Gefühle: 
Neid setzt sich zusammen aus Sehnsucht, Aggression und Schmerz.
Man will etwas haben, das ist die Sehnsucht; man ist neidisch auf den anderen, das ist das aggressive Element;
und es schmerzt, dass man es nicht hat.

Eifersucht setzt sich zusammen aus: Schmerz, Aggression und Neid. Der Schmerz wird mit einer bestimmten Geschichte verbunden,
die wiederum aus vielerlei Fantasien und Vorstellungen zusammengesetzt ist.

Tiefere Erfahrungen: Tiefe, Ruhe, Leere, Stille, Frieden, bedingungslose Liebe und Glückseligkeit sind Erfahrungen,
die tiefer sind, als Gefühle es je sein können.

Hier sind weiter Details zu den einzelnen Bewusstheitsebenen:
{beschreibung_bewusstheitsebenen}


Regeln:
- Nutze den Kontext der vorherigen Nachrichten, aber klassifiziere ausschließlich die letzte Nachricht.
- Wenn die Ziel-Nachricht mehrere Aspekte enthält, wähle den **dominanten** Aspekt.
- Verwende die Feldbeschreibung der Pydantic-Struktur als maßgebliche Definition.
- Antworte ausschließlich als streng strukturiertes Objekt gemäß dem Schema.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "Nachrichtenverlauf:\n{context_text}\n\nZiel-Nachricht:\n{target_text}")]
)
