# Quality Control Dashboard - Implementation Updates

## 🎉 New Features Implemented

This update modernizes the Smart Harvest Quality Control system with AI-powered reporting and a professional management dashboard.

---

## 📋 Changes Made

### 1. **Enhanced Gemini Reporter** ([src/reporting/gemini_reporter.py](src/reporting/gemini_reporter.py))
- ✅ Translated all content from French to English
- ✅ Optimized AI prompt for concise, data-driven reports
- ✅ Emphasizes visual elements (tables, metrics) over lengthy text
- ✅ Maximum 200-word executive summaries
- ✅ Added time_period parameter support

**Key Improvements:**
- Reports now focus on actionable insights only
- Structured format with Key Metrics table, Status indicators, and Top Actions
- Temperature lowered to 0.3 for more consistent outputs

---

### 2. **Time-Based Data Fetcher** ([src/reporting/data_fetcher.py](src/reporting/data_fetcher.py))
New module for flexible data retrieval from Supabase database.

**Features:**
- `fetch_all_data()` - Get all historical records
- `fetch_by_hours(hours)` - Last N hours (e.g., 24h)
- `fetch_by_days(days)` - Last N days (e.g., 7 days, 30 days)
- `fetch_by_date_range(start, end)` - Custom date range
- `get_time_series_data(hours)` - For trend visualizations

**Returns:** Dictionary with `{total, fresh, dry, time_period}`

---

### 3. **PDF Generator** ([src/reporting/pdf_generator.py](src/reporting/pdf_generator.py))
Professional PDF export functionality with styled templates.

**Features:**
- Converts Markdown reports to beautifully formatted PDFs
- Company-branded header with timestamp
- Professional typography and color scheme
- Proper table formatting with alternating row colors
- Support for charts, lists, and blockquotes
- Automatic page numbering
- Saves to `/reports` folder with timestamped filenames

**Usage:**
```python
from reporting.pdf_generator import PDFGenerator

generator = PDFGenerator()
pdf_path = generator.markdown_to_pdf(markdown_content, "My_Report")
# Saves to: reports/My_Report.pdf
```

---

### 4. **Modernized Dashboard** ([src/dashboard.py](src/dashboard.py))
Complete UI overhaul with advanced management tools.

**New UI Elements:**
- 🎨 Modern gradient header with branding
- 📊 Enhanced metric cards with color-coded status indicators
- 🎯 Gauge chart for loss rate monitoring (green/yellow/red zones)
- 📈 Time-series line chart showing hourly quality trends
- 🔄 Professional sidebar with controls and system info

**New "Generate Quality Control Report" Section:**

#### Time Range Selection:
- **Last 24 Hours** - Real-time daily operations
- **Last 7 Days** - Weekly summary
- **Last 30 Days** - Monthly analysis
- **Custom Date Range** - Select any start/end dates
- **All Time** - Complete historical data

#### Report Generation Workflow:
1. Select time range → See preview statistics
2. Click "Generate AI Report" → AI creates Markdown report
3. Preview report in expandable section
4. Download as PDF or Markdown file
5. PDF automatically saved to `/reports` folder

**Visual Improvements:**
- Status badges: 🟢 OK (<5%), 🟡 WARNING (5-15%), 🔴 CRITICAL (>15%)
- Color-coded metrics (green for accepted, red for rejected)
- Donut chart for Fresh vs Dry distribution
- Collapsible raw data table

---

## 📦 New Dependencies

Added to [requirements.txt](requirements.txt):

```
streamlit==1.39.0          # Dashboard framework
pandas==2.2.2              # Data manipulation
plotly==5.24.0             # Interactive charts
google-genai==0.8.3        # Gemini AI integration
markdown==3.7              # Markdown parsing
weasyprint==62.3           # PDF generation
```

---

## 🚀 Getting Started

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Note: WeasyPrint requires system libraries. On Linux:
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

2. **Set up environment variables:**
Create a `.env` file with:
```env
DB_API=your_supabase_url
DB_SERVICE_ROLE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
```

3. **Run the dashboard:**
```bash
streamlit run src/dashboard.py
```

---

## 🎯 Usage Guide

### For Quality Managers

#### **Daily Monitoring:**
1. Open dashboard to see real-time metrics
2. Check loss rate gauge (should be green: <5%)
3. Review time-series chart for unusual patterns

#### **Weekly Reports:**
1. Navigate to "Generate Quality Control Report"
2. Select "Last 7 Days"
3. Click "Generate AI Report"
4. Review the AI-generated insights
5. Download PDF for distribution

#### **Custom Analysis:**
1. Select "Custom Date Range"
2. Choose start and end dates
3. Generate report for specific periods (harvest seasons, equipment changes, etc.)

#### **PDF Reports:**
- Automatically saved to `/reports` folder
- Filename format: `QC_Report_YYYY-MM-DD_HHMMSS.pdf`
- Professional formatting suitable for management presentations

---

## 📁 File Structure

```
src/
├── dashboard.py                    # Main Streamlit dashboard (UPDATED)
├── reporting/
│   ├── __init__.py
│   ├── gemini_reporter.py         # AI report generator (UPDATED)
│   ├── data_fetcher.py            # Time-range queries (NEW)
│   └── pdf_generator.py           # Markdown to PDF (NEW)

reports/                            # PDF reports saved here
├── .gitkeep
└── QC_Report_*.pdf                # Generated reports

requirements.txt                    # Updated dependencies
```

---

## 🔧 Technical Details

### Database Schema Assumptions
The code expects a Supabase `logs` table with:
- `timestamp` (datetime) - When the item was processed
- `prediction` (string) - Classification: "Fresh" or "Dry"

### AI Report Structure
Generated reports include:
1. **Key Metrics Table** - Total, Fresh, Dry, Loss Rate
2. **Status Assessment** - OK/WARNING/CRITICAL
3. **Top 3 Actions** - Prioritized recommendations
4. **Root Causes** - Probable issues based on severity
5. **Metadata** - Timestamp and approval note

### PDF Styling
- Color scheme: Blue theme (#1e40af primary)
- Typography: Segoe UI / Arial sans-serif
- Tables: Alternating row colors, hover effects
- Layout: A4 size with proper margins

---

## 🐛 Troubleshooting

### WeasyPrint Installation Issues
If PDF generation fails:
1. Check system libraries are installed (see Installation above)
2. Try alternative: `pip install reportlab` (requires code modification)

### Database Connection
If "No data found":
1. Verify `.env` file has correct credentials
2. Check Supabase table name is "logs"
3. Ensure database has records with 'timestamp' and 'prediction' columns

### Gemini API Errors
If report generation fails:
1. Verify `GEMINI_API_KEY` is set in `.env`
2. Check API quota at [Google AI Studio](https://makersuite.google.com/)
3. Review error message in terminal

---

## 🎨 Customization

### Change Color Scheme
Edit CSS in [src/dashboard.py](src/dashboard.py):
```python
# Search for hex colors like #1e40af and replace with your brand colors
```

### Modify Report Template
Edit the prompt in [src/reporting/gemini_reporter.py](src/reporting/gemini_reporter.py):
```python
# Line ~40: Update the `prompt` variable
```

### Adjust PDF Styling
Edit CSS in [src/reporting/pdf_generator.py](src/reporting/pdf_generator.py):
```python
# _get_css() method starting around line 90
```

---

## 📊 Screenshots & Examples

### Dashboard Features:
1. **Metric Cards** - Total/Fresh/Dry with percentages
2. **Gauge Chart** - Visual loss rate with color zones
3. **Pie Chart** - Fresh vs Dry distribution
4. **Time Series** - Hourly trends over time
5. **Report Generator** - Time-range selection and AI generation
6. **PDF Preview** - Markdown preview before download

### Sample Report Structure:
```markdown
## Quality Control Report

### 📊 Key Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Total Processed | 1,234 | - |
| Fresh (Accepted) | 1,100 (89.1%) | ✓ |
| Dry (Rejected) | 134 (10.9%) | WARNING |

### 🎯 Status: **WARNING**
Attention Needed: Loss rate above normal range (5-15%).

### ⚡ Top 3 Actions
1. Inspect drying process parameters
2. Review storage humidity levels
3. Analyze supplier batch quality
```

---

## 🚀 Future Enhancements (Not Implemented)

Potential additions for future versions:
- Email report scheduling
- Multi-language support (Arabic, Spanish)
- Real-time alerts for critical loss rates
- Supplier performance analytics
- Equipment efficiency tracking
- Mobile-responsive design
- Export to Excel/CSV

---

## 📝 Change Log

### Version 2.0 (February 13, 2026)
- ✅ Translated Gemini reporter to English
- ✅ Optimized AI prompt for concise reports
- ✅ Added time-based data fetching
- ✅ Implemented PDF generation
- ✅ Modernized dashboard UI
- ✅ Added report generator interface
- ✅ Updated dependencies

### Version 1.0
- Initial dashboard with basic metrics
- Simple pie chart visualization
- Manual data refresh

---

## 👥 Support

For issues or questions:
1. Check error messages in terminal
2. Review this documentation
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed

---

**Built with ❤️ for Smart Harvest Quality Control**
