from enum import Enum
from typing import ClassVar, Dict, List
from pydantic import BaseModel, Field


class Bewusstheitsebene(str, Enum):
    GEDANKE = "gedanke"
    KOERPEREMPFINDUNG = "koerperempfindung"
    AUFREGUNG = "aufregung"
    GEFUEHL = "gefuehl"
    SINKEN = "sinken"
    TIEFERE_ERFAHRUNG = "tiefere_erfahrung"


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


class ConsciousnessProposal(BaseModel):
    """
    Klassifikation der letzten Nachricht, basierend auf dem Gesprächskontext.
    Genau EIN Wert im Enum 'Bewusstheitsebene'.
    """

    bewusstheitsebene: Bewusstheitsebene = Field(
        description=(
            "Genau eine der sechs Klassen:\n"
            "- gedanke: Kognitiver Inhalt/Selbstgespräch, Bewertungen, Planen, Analysieren "
            "(z. B. „Ich schaffe das nicht“, „Das war dumm“, „Morgen muss ich früh raus“). "
            "Beispiel-Keywords: " + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.GEDANKE]) + "\n"
            "- koerperempfindung: Unmittelbare körperliche Sensationen (Druck, Enge, Wärme/Kälte, "
            "Kribbeln, Herzklopfen, Zittern, Anspannung) ohne Bewertung. "
            "Beispiel-Keywords: " + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.KOERPEREMPFINDUNG]) + "\n"
            "- aufregung: Erhöhte innere Aktivierung/Erregung als Zustand (z. B. Nervosität, "
            "Getriebensein, hektische Unruhe). Fokus auf dem **Erregungsniveau**, nicht auf einem "
            "spezifischen Gefühl. Beispiel-Keywords: "
            + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.AUFREGUNG])
            + "\n"
            "- gefuehl: Emotionale Zustände (Traurigkeit, Freude, Angst, Wut, Scham, Schuld, "
            "Erleichterung...). Meist als einzelnes Wort/kurze Wortgruppe. "
            "Beispiel-Keywords: " + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.GEFUEHL]) + "\n"
            "- sinken: Abnehmende Aktivierung/Absacken/Schwere/Leere/„Down“-Gefühl (z. B. Erschöpfung, "
            "inneres Wegsacken). Fokus auf **Niedrig-Arousal**. Beispiel-Keywords: "
            + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.SINKEN])
            + "\n"
            "- tiefere_erfahrung: Grundlegende Erlebnisqualität/Werte/Sinn/Verbundenheit/Präsenz "
            "(z. B. Weite, Stille, Vertrauen, Dankbarkeit als Grundhaltung, Gefühl von Sinn). "
            "Beispiel-Keywords: " + ", ".join(BEWUSSTHEITSEBENE_BEISPIELE[Bewusstheitsebene.TIEFERE_ERFAHRUNG])
        )
    )
