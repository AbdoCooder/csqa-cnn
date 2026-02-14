# src/reporting/pdf_generator.py
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import markdown

try:
    from weasyprint import HTML, CSS
except ImportError:
    HTML = None  # type: ignore
    CSS = None  # type: ignore


class PDFGenerator:
    """
    Converts Markdown reports to styled PDF documents.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the PDF generator.
        
        Args:
            output_dir: Directory where PDFs will be saved (relative to project root)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def markdown_to_pdf(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """
        Convert Markdown content to PDF and save it.
        
        Args:
            markdown_content: The Markdown text to convert
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated PDF file
        """
        if HTML is None:
            raise ImportError("weasyprint is required for PDF generation. Install it with: pip install weasyprint")
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"QC_Report_{timestamp}"
        
        # Ensure .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        output_path = self.output_dir / filename
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Wrap in full HTML document with styling
        full_html = self._create_styled_html(html_content)
        
        # Generate PDF
        if HTML is None or CSS is None:
            raise ImportError("weasyprint is required for PDF generation")
        
        HTML(string=full_html).write_pdf(output_path, stylesheets=[CSS(string=self._get_css())])
        
        return str(output_path)

    def _create_styled_html(self, body_content: str) -> str:
        """
        Wrap HTML content in a full document with header and footer.
        
        Args:
            body_content: HTML body content
            
        Returns:
            Complete HTML document string
        """
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Control Report</title>
</head>
<body>
    <div class="header">
        <h1>Smart Harvest Quality Control System</h1>
        <p class="date">Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
    
    <div class="content">
        {body_content}
    </div>
    
    <div class="footer">
        <p>Confidential - For Internal Use Only</p>
        <p class="page-number">Page <span class="page"></span></p>
    </div>
</body>
</html>
"""

    def _get_css(self) -> str:
        """
        Get CSS styling for the PDF document.
        
        Returns:
            CSS string
        """
        return """
@page {
    size: A4;
    margin: 2cm 1.5cm;
    
    @top-center {
        content: '';
    }
    
    @bottom-center {
        content: 'Page ' counter(page) ' of ' counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    font-size: 11pt;
}

.header {
    text-align: center;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 15px;
    margin-bottom: 30px;
}

.header h1 {
    color: #1e40af;
    font-size: 24pt;
    margin: 0 0 5px 0;
}

.header .date {
    color: #666;
    font-size: 10pt;
    margin: 0;
}

.content {
    margin: 20px 0;
}

h2 {
    color: #1e40af;
    font-size: 18pt;
    margin-top: 25px;
    margin-bottom: 15px;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 5px;
}

h3 {
    color: #2563eb;
    font-size: 14pt;
    margin-top: 20px;
    margin-bottom: 10px;
}

h4 {
    color: #3b82f6;
    font-size: 12pt;
    margin-top: 15px;
    margin-bottom: 8px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th {
    background-color: #2563eb;
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    font-size: 10pt;
}

td {
    padding: 10px 12px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 10pt;
}

tr:nth-child(even) {
    background-color: #f9fafb;
}

tr:hover {
    background-color: #f3f4f6;
}

ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
    line-height: 1.5;
}

strong {
    color: #1e40af;
    font-weight: 600;
}

em {
    color: #4b5563;
}

code {
    background-color: #f3f4f6;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

blockquote {
    border-left: 4px solid #2563eb;
    padding-left: 15px;
    margin: 15px 0;
    color: #4b5563;
    font-style: italic;
}

hr {
    border: none;
    border-top: 1px solid #d1d5db;
    margin: 20px 0;
}

.footer {
    margin-top: 40px;
    padding-top: 15px;
    border-top: 1px solid #d1d5db;
    text-align: center;
    font-size: 9pt;
    color: #6b7280;
}

.page-number {
    margin-top: 5px;
}

/* Status badge styling */
p:contains("CRITICAL") {
    color: #dc2626;
    font-weight: bold;
}

p:contains("WARNING") {
    color: #f59e0b;
    font-weight: bold;
}

p:contains("OK") {
    color: #10b981;
    font-weight: bold;
}
"""

    def generate_from_stats(self, total: int, fresh: int, dry: int, 
                           time_period: str = "", filename: Optional[str] = None) -> str:
        """
        Generate a PDF report directly from statistics using GeminiQCReporter.
        
        Args:
            total: Total items processed
            fresh: Number of fresh items
            dry: Number of dry items
            time_period: Description of the time period
            filename: Optional custom filename
            
        Returns:
            Path to the generated PDF file
        """
        from .gemini_reporter import GeminiQCReporter
        
        reporter = GeminiQCReporter()
        markdown_content = reporter.generate_report(total, fresh, dry, time_period)
        
        return self.markdown_to_pdf(markdown_content, filename)
