# src/reporting/gemini_reporter.py
import os
from google import genai  # pip install -U google-genai
from google.genai import types


class GeminiQCReporter:
    """
    Generates a QC (Quality Control) report from statistics (total/fresh/dry).
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
            return "CRITICAL"
        if reject_rate > 5:
            return "WARNING"
        return "OK"

    def generate_report(self, total: int, fresh: int, dry: int, time_period: str = "") -> str:
        if total <= 0:
            return "Cannot generate report: total = 0."
        if fresh < 0 or dry < 0 or (fresh + dry) > total:
            return "Cannot generate report: inconsistent statistics."

        reject_rate = (dry / total) * 100.0
        accept_rate = (fresh / total) * 100.0
        severity = self._severity(reject_rate)

        time_context = f"Time Period: {time_period}\n" if time_period else ""

        prompt = f"""
You are a Quality Control Manager in a date fruit processing facility.
Generate a CONCISE executive quality control report in Markdown format.

Context:
- Automated sorting classifies fruits as Fresh (accepted) or Dry (rejected).
- Dry = desiccation / moisture loss / fails premium quality standards.

Batch Data:
- {time_context}Total Processed: {total}
- Fresh (Accepted): {fresh} ({accept_rate:.1f}%)
- Dry (Rejected): {dry} ({reject_rate:.1f}%)
- Status: {severity} (OK ≤ 5%, WARNING 5-15%, CRITICAL > 15%)

Requirements:
- **Maximum 200 words** - managers need executive summaries, not essays
- **Data-first approach** - prioritize numbers, percentages, tables over prose
- **No invented data** - use only the provided statistics
- **Actionable insights only** - no generic advice

Mandatory Structure:

## Quality Control Report

### 📊 Key Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Total Processed | {total} | - |
| Fresh (Accepted) | {fresh} ({accept_rate:.1f}%) | ✓ |
| Dry (Rejected) | {dry} ({reject_rate:.1f}%) | {severity} |
| Loss Rate | {reject_rate:.1f}% | {severity} |

### 🎯 Status: **{severity}**

{{% if severity == "CRITICAL" %}}
**Immediate Action Required**: Loss rate exceeds 15% threshold.
{{% elif severity == "WARNING" %}}
**Attention Needed**: Loss rate above normal range (5-15%).
{{% else %}}
**Normal Operations**: Loss rate within acceptable limits.
{{% endif %}}

### ⚡ Top 3 Actions
1. [Most critical action based on severity]
2. [Second priority action]
3. [Third priority action]

### 🔍 Root Causes (2-3 max)
- [Probable cause 1]
- [Probable cause 2]

---
*Report generated on {time_context.strip() if time_context else 'current batch'}*
*Requires Quality Manager approval before distribution*

Keep it visual, data-heavy, and under 200 words of actual text content.
"""

        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=types.Part.from_text(text=prompt),
            config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.85,
            ),
        )
        return (resp.text or "").strip() or "Report generation failed (retry)."
