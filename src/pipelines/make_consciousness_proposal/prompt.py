from langchain_core.prompts import ChatPromptTemplate

from pipelines.schema import ConsciousnessProposal, Bewusstheitsebene, TimePeriod, BEWUSSTHEITSEBENEN_BESCHREIBUNG


def build_schema_description() -> str:
    lines = ["Strukturelle Spezifikation (Beschreibung der Felder):\n"]
    for name, field in ConsciousnessProposal.model_fields.items():
        desc = field.description or ""
        type_name = getattr(field.annotation, "__name__", str(field.annotation))
        lines.append(f"- {name} ({type_name}):\n{desc}\n")
    return "\n".join(lines)


beschreibung_bewusstheitsvorschlaege = build_schema_description()


DOMINANZ_REGELN_VORSCHLAG = (
    "Dominanz-Regeln (für Auswahl des passendsten Vorschlags):\n"
    "1) Der Vorschlag muss zu dem zuletzt gesagten des Users passen.\n"
    f"2) Es sollte bei Möglichkeit vermieden werden einen Vorschlag, der in einer der beiden letzten Runden gemacht "
    f"wurde zu wiederholen. Generell ist es aber erlaubt Vorschläge aus älteren Runden zu wiederholen, wenn diese "
    f"besonders gut passen für die aktuelle Runde.\n"
    f"3) Der Vorschlag sollte die definierten Tiefe-Regeln befolgen."
    "Reihenfolge der Priorisierung: (1) passend > (2) Wiederholung > (3) Tiefe-Regel."
)


SYSTEM_PROMPT = f"""\
Du machst einen neuen Vorschlag, wessen sich der User noch bewusst sein kann.
Du erhältst als Input eine Liste an Nachrichten aus einem Gesprächsverlauf zwischen dem User und dem Assistenten.
Der Gesprächsverlauf folgt einer klaren Struktur. Er ist unterteilt in mehrere Runden, wobei eine Runde immer aus drei
Nachrichten besteht. Hier ist ein Beispiel für einen Runde:
[{{"role": "user", "content": "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht."}},
{{"role": "assistant", "content": "koerperempfindung"}},
{{"role": "assistant", "content": "e1-2: Und du brauchst nichts damit zu tun."}}]
Die erste Nachricht ist der Input des Users, der berichtet, wessen er sich in dem Moment bewusst ist.
Die zweite Nachricht ist das Klassifikationsergebnis eines vorherigen KI Modells, welches für die Nachricht des Users
die dominante Bewusstheitsebene ermittelt. 
Die dritte Nachricht ist der Vorschlag an den User, wessen er/sie sich noch bewusst sein kann. Wenn die dritte Nachricht
im Gesprächsverlauf vorkommt, bedeutet dies, dass diese Runde bereits abgeschlossen wurde und in der Vergangenheit liegt.

Du bekommst eine Liste von Vorschlägen, die jeweils eine ID zugeordnet haben. 
Wähle aus dieser Liste die maximal drei passendsten Vorschläge aus.
Berücksichtige dabei die vergangenen Vorschläge. Du solltest keinen Vorschlag machen, den du in einer der beiden 
Runden zuvor gemacht hast.
Außerdem erhältst du die Information, ob sich die Übung am {TimePeriod.ANFANG.value}, in der {TimePeriod.MITTE.value} 
oder am {TimePeriod.ENDE.value} befindet. 
Anhand des Gesprächsverlaufs siehst du bereits, in welche Bewusstheitsebene zuletzt klassifiziert wurde. 
Wenn zuletzt in die Ebene {Bewusstheitsebene.AUFREGUNG.value}, {Bewusstheitsebene.SINKEN.value}, 
{Bewusstheitsebene.TIEFERE_ERFAHRUNG.value} oder {Bewusstheitsebene.UNKLAR.value} klassifiziert wurde, 
bist du frei in der Auswahl der nächsten Vorschlaege, d.h. es gibt keine Tiefe-Regel.

Wenn zuletzt in die Ebene {Bewusstheitsebene.GEDANKE.value} klassifiziert wurde, gilt folgende Tiefe-Regel:
- Wenn sich die Übung am {TimePeriod.ANFANG.value} befindet, wählst du einen Vorschlag aus, der die Ebene beibehält, d.h.
du wählst einen Vorschlag aus, der auf die Bewusstheitsebene {Bewusstheitsebene.GEDANKE.value} abzielt. 
- Wenn sich die Übung in der {TimePeriod.MITTE.value} befindet, wählst du einen Vorschlag aus, der eine Ebene tiefer geht,
d.h. du wählst einen Vorschlag aus der Bewusstheitsebene {Bewusstheitsebene.KOERPEREMPFINDUNG.value} aus.
- Wenn sich die Übung in der {TimePeriod.ENDE.value} befindet, wählst du einen Vorschlag aus, der zwei Ebenen tiefer geht,
d.h. du wählst einen Vorschlag aus der Bewusstheitsebene {Bewusstheitsebene.GEFUEHL.value} aus.

Wenn zuletzt in die Ebene {Bewusstheitsebene.KOERPEREMPFINDUNG.value} klassifiziert wurde, gilt folgende Tiefe-Regel:
- Wenn sich die Übung am {TimePeriod.ANFANG.value} befindet, wählst du einen Vorschlag aus, der die Ebene beibehält, d.h.
du wählst einen Vorschlag aus Bewusstheitsebene {Bewusstheitsebene.KOERPEREMPFINDUNG.value} aus. 
- Wenn sich die Übung in der {TimePeriod.MITTE.value} oder am {TimePeriod.ENDE.value} befindet,
wählst du einen Vorschlag aus, der eine Ebene tiefer geht,
d.h. du wählst einen Vorschlag aus der Bewusstheitsebene {Bewusstheitsebene.GEFUEHL.value} aus.

Wenn zuletzt in die Ebene {Bewusstheitsebene.GEFUEHL.value} klassifiziert wurde, gilt folgende Tiefe-Regel:
- Wenn sich die Übung am {TimePeriod.ANFANG.value} befindet, wählst du einen Vorschlag aus, der die Ebene beibehält, d.h.
du wählst einen Vorschlag aus Bewusstheitsebene {Bewusstheitsebene.GEFUEHL.value} aus. 
- Wenn sich die Übung in der {TimePeriod.MITTE.value} oder am {TimePeriod.ENDE.value} befindet,
wählst du einen Vorschlag aus, der eine Ebene tiefer geht,
d.h. du wählst einen Vorschlag aus der Bewusstheitsebene {Bewusstheitsebene.TIEFERE_ERFAHRUNG.value} aus.

Wähle nur Vorschläge aus, die auch passend sind. Z.B. wenn der User als letztes davon berichtet, dass er sich
einer Freude bewusst ist, dann ist ein Vorschlag "Und du kannst vielleicht der Freude den ganzen Raum geben" passend,
wohingegen ein Vorschlag "Und du kannst vielleicht wahrnehmen, wie sich die Wut in dir ausbreitet" unpassend ist.
Wenn mehrere Vorschläge passend sind, wähle einen davon aus. 

Berücksichtige insbesondere die folgenden Dominanz-Regeln:
{DOMINANZ_REGELN_VORSCHLAG} 

Hier ist eine Übersicht zu den Bewusstheitsebenen:
{BEWUSSTHEITSEBENEN_BESCHREIBUNG}

Hier ist beschrieben, wie der Output für die Bewusstheitsvorschläge aussehen sollte:
{beschreibung_bewusstheitsvorschlaege}


Regeln:
- Nutze den Kontext der vorherigen Nachrichten, aber mache ausschließlich Vorschläge für die letzte User-Nachricht.
- Mache ausschließlich sehr gut passende Vorschläge. Mache maximal drei Vorschläge. Wenn kein Vorschlag passt, gib eine
leere Liste zurück. Wenn nur ein oder zwei Vorschläge passend sind, gib auch nur einen bzw. zwei Vorschläge zurück.
Sortiere die Liste der Vorschläge mit dem am besten passendsten Vorschlag am Anfang der Liste.
- Verwende die Feldbeschreibung der Pydantic-Struktur als maßgebliche Definition.
- Antworte ausschließlich als streng strukturiertes Objekt gemäß dem Schema.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "Nachrichtenverlauf:\n{context_text}\n\nZiel-Nachricht:\n{target_text}")]
)
