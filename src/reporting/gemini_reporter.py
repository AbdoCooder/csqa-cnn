# src/reporting/gemini_reporter.py
import os
from google import genai  # pip install -U google-genai
from google.genai import types


class GeminiQCReporter:
    """
    Génère un rapport QC (français) à partir de statistiques (total/fresh/dry).
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Put it in .env or export it.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    @staticmethod
    def _severity(reject_rate: float) -> str:
        if reject_rate > 15:
            return "CRITIQUE"
        if reject_rate > 5:
            return "WARNING"
        return "OK"

    def generate_report(self, total: int, fresh: int, dry: int) -> str:
        if total <= 0:
            return "Impossible de générer un rapport : total = 0."
        if fresh < 0 or dry < 0 or (fresh + dry) > total:
            return "Impossible de générer un rapport : statistiques incohérentes."

        reject_rate = (dry / total) * 100.0
        severity = self._severity(reject_rate)

        prompt = f"""
Tu es un ingénieur Qualité dans une usine de conditionnement de dattes.
Rédige un rapport de contrôle qualité professionnel en FRANÇAIS, en Markdown.

Contexte:
- Le tri classe les fruits en Fresh (acceptés) et Dry (rejetés).
- Dry = dessèchement / perte d'humidité / non conforme au standard premium.

Données du lot:
- Total traité : {total}
- Fresh (acceptés) : {fresh}
- Dry (rejetés) : {dry}
- Taux de rejet : {reject_rate:.2f} %
- Statut gravité : {severity} (OK ≤ 5%, WARNING 5–15%, CRITIQUE > 15%)

Contraintes:
- 250 à 450 mots
- Pas d'invention de chiffres
- Actions concrètes, applicables immédiatement

Structure obligatoire:
1) Résumé exécutif
2) Indicateurs du lot (liste à puces)
3) Analyse de gravité (1 paragraphe)
4) Hypothèses de causes probables (3 à 5 puces)
5) Actions correctives immédiates (3 à 5 puces)
6) Contrôles recommandés pour le prochain lot (2 à 4 puces)
7) Note qualité: "À valider par le responsable qualité."
"""

        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=types.Part.from_text(text=prompt),
            config=types.GenerateContentConfig(
                temperature=0.4,
                top_p=0.9,
            ),
        )
        return (resp.text or "").strip() or "Rapport vide (réessaye)."
