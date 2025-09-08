from enum import Enum
from pydantic import BaseModel, Field


class Bewusstheitsebene(str, Enum):
    GEDANKE = "gedanke"
    KOERPEREMPFINDUNG = "koerperempfindung"
    GEFUEHL = "gefuehl"
    TIEFERE_ERFAHRUNG = "tiefere_erfahrung"


class ConsciousnessProposal(BaseModel):
    """
    Klassifikation der letzten Nachricht, basierend auf dem Gesprächskontext.
    """

    bewusstheitsebene: Bewusstheitsebene = Field(
        description=(
            "Genau eine der vier Klassen:\n"
            "- gedanke: Kognitiver Inhalt/Selbstgespräch, Bewertungen, Planen, Analysieren "
            "(z. B. „Ich schaffe das nicht“, „Das war dumm“, „Morgen muss ich früh raus“).\n"
            "- koerperempfindung: Unmittelbare körperliche Sensationen (Druck, Enge, Wärme/Kälte, "
            "Kribbeln, Herzklopfen, Zittern, Anspannung).\n"
            "- gefuehl: Emotionale Zustände (Traurigkeit, Freude, Angst, Wut, Scham, Schuld, "
            "Erleichterung...).\n"
            "- tiefere_erfahrung: Grundlegende Erlebnisqualität/Werte/Sinn/Verbundenheit/Präsenz "
            "(z. B. Weite, Stille, Vertrauen, Dankbarkeit als Grundhaltung, Gefühl von Sinn)."
        )
    )
