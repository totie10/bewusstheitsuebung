import re
import warnings
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class Bewusstheitsebene(str, Enum):
    GEDANKE = "gedanke"
    KOERPEREMPFINDUNG = "koerperempfindung"
    AUFREGUNG = "aufregung"
    GEFUEHL = "gefuehl"
    SINKEN = "sinken"
    TIEFERE_ERFAHRUNG = "tiefere_erfahrung"
    UNKLAR = "unklar"


MAPPING_BEWUSSTHEITSEBENE = {
    "Denken und Sinne": Bewusstheitsebene.GEDANKE,
    "Koerpergefuehl": Bewusstheitsebene.KOERPEREMPFINDUNG,
    "Unruhe/ Ruhe": Bewusstheitsebene.AUFREGUNG,
    "Gefuehl": Bewusstheitsebene.GEFUEHL,
    "Fallen": Bewusstheitsebene.SINKEN,
    "tiefere Erfahrung": Bewusstheitsebene.TIEFERE_ERFAHRUNG,
    "nichts": Bewusstheitsebene.UNKLAR,
}


BEWUSSTHEITSEBENE_BEISPIELE: Dict[str, List[str]] = {
    Bewusstheitsebene.GEDANKE: [
        "Gedanke",
        "Denken",
        "Vorstellung",
        "Erinnerung",
        "Bild",
        "Traum",
        "innere Sätze",
        "Stimmen",
    ],
    Bewusstheitsebene.KOERPEREMPFINDUNG: [
        "Druck",
        "Spannung",
        "Härte",
        "Kribbeln",
        "Vibrieren",
        "Taubheit",
        "Hitze",
        "Atem",
        "Zittern",
        "Widerstand",
        "Zähigkeit",
        "Nebel",
        "Schleier",
        "Beklemmung",
        "Schmerz",
        "Klopfen",
        "Herz",
        "Kontraktion",
        "Krampf",
        "Müdigkeit",
    ],
    Bewusstheitsebene.AUFREGUNG: [
        "Aufregung",
        "Unruhe",
        "Ruhe",
        "Nervosität",
        "Energie",
        "Beben",
        "Strömen",
    ],
    Bewusstheitsebene.GEFUEHL: [
        "Schmerz",
        "Angst",
        "Sehnsucht",
        "Melancholie",
        "Stolz",
        "Hass",
        "Ärger",
        "Trauer",
        "Wehmut",
        "Wut",
        "Neid",
        "Hilflosigkeit",
        "Panik",
        "Verzweiflung",
        "Scham",
        "Unsicherheit",
        "Bestürzung",
        "Zorn",
        "Leid",
        "Qual",
        "Schreck",
        "Furcht",
        "Ekel",
        "Abscheu",
        "Mulmigkeit",
        "Resignation",
        "Mutlosigkeit",
        "Hoffnungslosigkeit",
        "Euphorie",
        "Lust",
        "Gier",
        "Ungeduld",
        "Begeisterung",
        "Herzschmerz",
        "Triumph",
        "Gefühl",
        "Einsamkeit",
        "Ohnmacht",
        "Erschöpfung",
        "Wohligkeit",
        "Heiterkeit",
        "Freude",
        "Verzweiflung",
    ],
    Bewusstheitsebene.SINKEN: [
        "Sinken",
        "Rutschen",
        "Wanken",
        "Schlittern",
        "Torkeln",
        "Schleudern",
        "Abgrund",
        "Loch",
        "Schmelzen",
        "Enge",
        "Loslassen",
        "Gleiten",
        "Sog",
    ],
    Bewusstheitsebene.TIEFERE_ERFAHRUNG: [
        "(bedingungslose) Liebe",
        "Glückseligkeit",
        "Frieden",
        "Leere",
        "Weite",
        "Glück",
        "Tiefe Freude",
        "Heiterkeit",
        "Raum",
        "Stille",
        "Unendlichkeit",
        "Grenzenlosigkeit",
        "Geborgenheit",
        "Zuhause",
        "Nichts",
        "Schwärze",
        "Dunkelheit",
        "Fülle",
        "Freiheit",
        "Tiefe",
        "Sanftheit",
        "tiefe Ruhe",
    ],
}

TIEFE_PRIORITAET: List[Bewusstheitsebene] = [
    Bewusstheitsebene.TIEFERE_ERFAHRUNG,  # am tiefsten
    Bewusstheitsebene.SINKEN,
    Bewusstheitsebene.GEFUEHL,
    Bewusstheitsebene.AUFREGUNG,
    Bewusstheitsebene.KOERPEREMPFINDUNG,
    Bewusstheitsebene.GEDANKE,  # am "höchsten"/kognitivsten
]


BEWUSSTHEITSEBENEN_BESCHREIBUNG = (
    f"- gedanke: Kognitive Inhalte, innere Sätze, Bewertungen, Planen, Vorstellungen oder Erinnerungen. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.GEDANKE])}\n"
    f"- koerperempfindung: Wahrnehmbare körperliche Empfindungen und Signale. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.KOERPEREMPFINDUNG])}\n"
    f"- aufregung: Erhöhte innere Aktivierung, Nervosität oder energetisches Aufgewühltsein. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.AUFREGUNG])}\n"
    f"- gefuehl: Emotionale Zustände wie Freude, Schmerz, Heiterkeit, Trauer, Wut, Angst, Verzweiflung, Scham oder Ekel. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.GEFUEHL])}\n"
    f"- sinken: Erleben von in die Tiefe sinken, Fallen, Absacken, Abwärtsbewegung, nicht-körperliche Enge oder Schwere. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.SINKEN])}\n"
    f"- tiefere_erfahrung: Existenzielle oder spirituelle Qualitäten wie Tiefe, Ruhe, Leere, Stille, Frieden, "
    f"bedingungslose Liebe, Glückseligkeit, Weite oder Verbundenheit. "
    f"Beispiel-Keywords: {', '.join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.TIEFERE_ERFAHRUNG])}"
    f"- unklar: Die komplette Beschreibung ist so ungenau oder unverständlich, dass die Klassifikation in eine"
    f"der sechs oberen Bewusstheitsebenen nicht möglich ist. "
)

DOMINANZ_REGELN_KLASSIFIKATION = (
    "Dominanz-Regeln (für Auswahl der einen dominanten Ebene):\n"
    "1) Zuletzt Gesagtes hat höchstes Gewicht.\n"
    f"2) Tiefere Ebene hat höheres Gewicht als eine höhere Ebene (Tiefe-Hierarchie: "
    f"Die höchste Bewusstheitsebene sind die Gedanken. Die tiefste Bewusstheitsebene sind die tieferen Erfahrungen. "
    f"Somit gilt für die Priorität: {' > '.join(e.value for e in TIEFE_PRIORITAET)}).\n"
    "3) Häufigkeit/Umfang: Die Ebene, aus der der größte Teil des Gesagten stammt, wiegt stärker.\n"
    "Reihenfolge der Priorisierung: (1) zuletzt > (2) Tiefe > (3) Häufigkeit."
)


class ConsciousnessLevel(BaseModel):
    """
    Klassifikation der letzten Nachricht, basierend auf dem Gesprächskontext.
    Genau EIN Wert im Enum 'Bewusstheitsebene' -> dominante Ebene.
    Zusätzlich:
      - begruendung: kurze Begründung für Wahl der dominaten Ebene
    """

    bewusstheitsebene: Bewusstheitsebene = Field(
        description=(
            f"Genau eine der sieben Klassen (dominant, siehe Dominanz-Regeln unten):\n"
            f"{BEWUSSTHEITSEBENEN_BESCHREIBUNG}"
            f"{DOMINANZ_REGELN_KLASSIFIKATION}"
        )
    )

    begruendung: str = Field(
        description=(
            "Kurze Erläuterung (1–3 Sätze), wie die dominante Ebene bestimmt wurde. "
            "Dabei soll erkennbar sein, welche Textstellen zur Zuordnung geführt haben "
            "(z. B. 'Ich bin wütend' → Bewusstheitsebene gefuehl: Wut). "
            "Beziehe dich, falls mehrere Ebenen erkannt werden, auch auf (1) das zuletzt Gesagte, "
            "(2) die Tiefe-Hierarchie und (3) die Häufigkeit."
        )
    )


class ConsciousnessMessage(BaseModel):
    text: str
    vorhergesagte_bewusstheitsebene: Bewusstheitsebene


class ConsciousnessSample(BaseModel):
    username: str
    timestamp: str
    consciousness_messages: List[ConsciousnessMessage]


class ConsciousnessPrediction(ConsciousnessMessage):
    username: str
    timestamp: str
    context: List[str]
    vorhergesagte_bewusstheitsebene_dev: ConsciousnessLevel


VORSCHLAG_PATTERN = re.compile(r"^e[1-9]-\d+$")


class ConsciousnessProposal(BaseModel):
    vorschlaege: List[str] = Field(
        description=(
            "Liste der IDs der passendsten Vorschläge. "
            "Jede ID muss das Format eX-Y haben (X=1–9, Y=positive Zahl). "
            "Maximal drei Vorschläge sind erlaubt – falls mehr übergeben werden, "
            "werden sie abgeschnitten."
        )
    )
    begruendung: str = Field(description="Kurze Erläuterung (1–3 Sätze), wieso diese Vorschläge gewählt wurden.")

    @field_validator("vorschlaege")
    def validate_and_truncate_vorschlaege(cls, v: List[str]) -> List[str]:
        # Regex check
        for item in v:
            if not VORSCHLAG_PATTERN.match(item):
                raise ValueError(f"Ungültige Vorschlags-ID '{item}', erwartet Format eX-Y (z.B. e3-5).")
        # Truncate with warning if too long
        if len(v) > 3:
            warnings.warn(
                f"Zu viele Vorschläge ({len(v)} erhalten) – die Liste wird auf die ersten 3 gekürzt.",
                UserWarning,
                stacklevel=2,
            )
            v = v[:3]
        return v


class TimePeriod(str, Enum):
    ANFANG = "anfang"
    MITTE = "mitte"
    ENDE = "ende"
