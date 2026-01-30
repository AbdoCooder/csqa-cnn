"""
Quality Control Reporting Module
Generates QC reports using open-source models from Hugging Face
"""

from dataclasses import dataclass
from transformers import pipeline

@dataclass
class QualityStats:
    """
    Data class to store production batch quality metrics.

    Attributes:
        total (int): Total number of fruits processed
        fresh (int): Count of Grade 1 (Fresh) fruits
        rotten (int): Count of Grade 3 (Rotten) fruits
    """
    total: int
    fresh: int
    rotten: int

    @property
    def loss_rate(self) -> float:
        """
        Calculate the loss rate as percentage of rejected fruits.

        Returns:
            float: Loss rate in percentage [0-100], or 0 if no fruits processed
        """
        return (self.rotten / self.total * 100) if self.total > 0 else 0.0


class QualityManager:
    """
    Generates professional Quality Control reports using open-source models from Hugging Face.

    This class uses the Hugging Face Transformers library with free, locally-run models
    to create detailed QC reports that analyze production data and suggest corrective actions
    for date sorting.
    """

    def __init__(self):
        """
        Initialize the Quality Manager with a Hugging Face text generation model.

        Note:
            First initialization will download the model (~1-2 GB) from Hugging Face Hub.
            Subsequent runs will use the cached model.
        """
        # Use a lightweight open-source model from Hugging Face
        # distilgpt2 is small (~82MB), fast, and runs locally without API keys
        try:
            self.pipeline = pipeline(
                "text-generation",
                model="distilgpt2",
                device=-1  # Use CPU (set to 0 for GPU if available)
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to load Hugging Face model: {str(e)}\n"
                f"Make sure 'transformers' is installed: pip install transformers"
            ) from e

    def generate_report(self, stats: dict) -> str:
        """
        Generate a professional QC incident report from production statistics.

        The report is contextualized for date fruit sorting in an industrial setting,
        including severity assessment, root cause analysis, and recommended actions.

        Args:
            stats (dict): Dictionary with keys 'total', 'fresh', 'rotten'

        Returns:
            str: Markdown-formatted QC report, or informative message if generation fails
        """
        # Convert raw stats dict to typed data class
        data = QualityStats(
            total=stats['total'],
            fresh=stats['fresh'],
            rotten=stats['rotten']
        )

        # Classify severity based on industrial standards for dates
        # Industry threshold: >15% loss is critical due to market value
        if data.loss_rate > 15:
            severity = "CRITICAL"
        elif data.loss_rate > 5:
            severity = "WARNING"
        else:
            severity = "ACCEPTABLE"

        # Construct a detailed prompt for the text generation model
        prompt = f"""Quality Control Report for Date Packaging Co.

PRODUCTION BATCH DATA:
- Product: Premium Dates
- Total Units Processed: {data.fresh + data.rotten} units
- Grade 1 (Fresh/Acceptable): {data.fresh} units
- Grade 3 (Rejected/Rotten): {data.rotten} units
- Loss Rate: {data.loss_rate:.2f}%
- Severity Status: {severity}

EXECUTIVE SUMMARY:
This production batch processed {data.fresh + data.rotten} units with a {data.loss_rate:.2f}% rejection rate. The severity is classified as {severity} based on industrial quality standards.

ROOT CAUSE ANALYSIS:
Probable causes for rejections include:
1. Insect infestation or pest contamination during storage
2. Humidity and temperature variations causing fermentation
3. Mechanical damage during harvest or handling

CORRECTIVE ACTIONS:
Immediate steps to improve quality:
1. Increase temperature and humidity monitoring in storage facilities
2. Implement more careful handling procedures during harvest
3. Conduct pest control and storage facility inspections

RECOMMENDATIONS:
Monitor quality metrics continuously and adjust processing parameters accordingly."""

        try:
            # Generate text using the Hugging Face model
            output = self.pipeline(
                prompt,
                max_length=800,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

            # Extract the generated text
            generated_text = output[0]['generated_text']

            # Return only the generated continuation (remove the prompt)
            # Extract the part after the prompt
            if prompt in generated_text:
                report = generated_text.split(prompt)[1].strip()
            else:
                report = generated_text

            return report if report else self._generate_fallback_report(data, severity)

        except Exception as e:
            # Graceful fallback if model generation fails
            print(f"⚠️ Model generation error: {str(e)}")
            return self._generate_fallback_report(data, severity)

    def _generate_fallback_report(self, data: 'QualityStats', severity: str) -> str:
        """
        Generate a template-based report when AI model generation fails.

        Args:
            data (QualityStats): Production statistics
            severity (str): Severity classification

        Returns:
            str: Markdown-formatted fallback report
        """
        return f"""# Quality Control Incident Report

## Executive Summary
This production batch processed {data.fresh + data.rotten} units with a {data.loss_rate:.2f}% rejection rate. The severity is classified as **{severity}** based on industrial quality standards for date production.

## Severity Analysis
- **Rejection Rate**: {data.loss_rate:.2f}%
- **Severity Level**: {severity}
- **Fresh Units**: {data.fresh} ({(data.fresh/(data.fresh+data.rotten)*100) if (data.fresh+data.rotten) > 0 else 0:.1f}%)
- **Rejected Units**: {data.rotten}

## Root Cause Diagnosis
Probable technical causes for date fruit rejection:

1. **Pest Contamination**: Insect infestation or mold during storage
2. **Environmental Factors**: Humidity and temperature fluctuations causing fermentation
3. **Mechanical Damage**: Physical damage during harvest, transport, or processing

## Immediate Corrective Actions

1. **Environmental Control**: Increase monitoring of storage temperature and humidity levels
2. **Handling Procedures**: Implement more careful fruit handling during harvest and processing
3. **Facility Inspection**: Conduct thorough pest control and storage facility sanitization

---
*Report generated on: {data.__class__.__name__}*
*All recommendations should be reviewed by production management.*"""
