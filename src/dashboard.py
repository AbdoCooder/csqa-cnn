"""
Smart Harvest Quality Control Dashboard
Modern management interface for real-time quality monitoring and reporting.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from supabase import create_client, Client

# Import our custom modules
from reporting.data_fetcher import DataFetcher
from reporting.gemini_reporter import GeminiQCReporter
from reporting.pdf_generator import PDFGenerator

load_dotenv()
DB_URL = os.environ.get("DB_API")
DB_KEY = os.environ.get("DB_SERVICE_ROLE_KEY")


def init_session_state():
    """Initialize session state variables."""
    if 'generated_report' not in st.session_state:
        st.session_state.generated_report = None
    if 'report_stats' not in st.session_state:
        st.session_state.report_stats = None


def load_data():
    """
    Connect to Supabase and fetch all rows from the logs table.
    """
    if DB_URL and DB_KEY:
        supabase: Client = create_client(DB_URL, DB_KEY)
    else:
        st.error("⚠️ Database connection failed. Check environment variables.")
        sys.exit(1)
    try:
        response = supabase.table("logs").select("*").execute()
        json_data = response.data or []
        df = pd.DataFrame(json_data)
        return df
    except Exception as e:
        st.error(f'Error fetching data: {e}')
        return None


def create_gauge_chart(value: float, title: str, max_value: float = 100):
    """Create a gauge chart for metrics."""
    color = "#10b981" if value <= 5 else "#f59e0b" if value <= 15 else "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': '#e2e8f0'}},
        delta={'reference': 5, 'increasing': {'color': "#ef4444"}},
        number={'font': {'color': '#f1f5f9', 'size': 32}},
        gauge={
            'axis': {
                'range': [None, max_value],
                'tickwidth': 2,
                'tickcolor': "#64748b",
                'tickfont': {'color': '#e2e8f0'}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "rgba(30, 41, 59, 0.6)",
            'borderwidth': 2,
            'bordercolor': "#475569",
            'steps': [
                {'range': [0, 5], 'color': 'rgba(16, 185, 129, 0.2)'},
                {'range': [5, 15], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [15, max_value], 'color': 'rgba(239, 68, 68, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': 15
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(30, 41, 59, 0.4)",
        plot_bgcolor="rgba(30, 41, 59, 0.4)",
        font={'color': "#e2e8f0", 'family': "Arial"}
    )
    
    return fig


def create_time_series_chart(df: pd.DataFrame):
    """Create a time series chart showing quality trends."""
    if df is None or len(df) == 0:
        return None
    
    # Check for timestamp field (support both 'created_at' and 'timestamp')
    timestamp_field = None
    if 'created_at' in df.columns:
        timestamp_field = 'created_at'
    elif 'timestamp' in df.columns:
        timestamp_field = 'timestamp'
    
    if timestamp_field:
        df[timestamp_field] = pd.to_datetime(df[timestamp_field])
        df = df.sort_values(timestamp_field)
        
        # Group by hour and prediction
        df['hour'] = df[timestamp_field].dt.floor('H')
        hourly_counts = df.groupby(['hour', 'prediction']).size().reset_index(name='count')
        
        fig = px.line(
            hourly_counts,
            x='hour',
            y='count',
            color='prediction',
            title='Quality Trends Over Time (Hourly)',
            labels={'hour': 'Time', 'count': 'Count', 'prediction': 'Classification'},
            color_discrete_map={'Fresh': '#10b981', 'Dry': '#ef4444'}
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(30, 41, 59, 0.8)",
                font=dict(color="#e2e8f0")
            ),
            paper_bgcolor="rgba(30, 41, 59, 0.4)",
            plot_bgcolor="rgba(30, 41, 59, 0.4)",
            font=dict(color="#e2e8f0"),
            xaxis=dict(
                gridcolor="rgba(148, 163, 184, 0.2)",
                color="#e2e8f0"
            ),
            yaxis=dict(
                gridcolor="rgba(148, 163, 184, 0.2)",
                color="#e2e8f0"
            )
        )
        
        return fig
    
    return None


def render_report_generator():
    """Render the time-based report generator section."""
    st.markdown("---")
    st.header("📄 Generate Quality Control Report")
    
    # Check database connection first
    db_status_col1, db_status_col2 = st.columns([3, 1])
    with db_status_col1:
        report_type = st.radio(
            "Select Time Range:",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Date Range", "All Time"],
            horizontal=True
        )
    
    with db_status_col2:
        # Show database connection status
        db_url = os.environ.get("DB_API")
        db_key = os.environ.get("DB_SERVICE_ROLE_KEY")
        if db_url and db_key:
            st.success("🔗 Connected")
        else:
            st.error("❌ No DB Config")
    
    # Handle different report types
    stats = None
    error_msg = None
    
    try:
        fetcher = DataFetcher()
        
        if report_type == "Last 24 Hours":
            stats = fetcher.fetch_by_hours(24)
        elif report_type == "Last 7 Days":
            stats = fetcher.fetch_by_days(7)
        elif report_type == "Last 30 Days":
            stats = fetcher.fetch_by_days(30)
        elif report_type == "Custom Date Range":
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
            with col_end:
                end_date = st.date_input("End Date", datetime.now())
            
            if start_date and end_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                stats = fetcher.fetch_by_date_range(start_datetime, end_datetime)
            else:
                error_msg = "Please select both start and end dates"
        else:  # All Time
            stats = fetcher.fetch_all_data()
    
    except ValueError as e:
        error_msg = f"Configuration Error: {e}"
        st.error(f"⚠️ {error_msg}")
        st.info("💡 Make sure DB_API and DB_SERVICE_ROLE_KEY environment variables are set.")
    except Exception as e:
        error_msg = f"Database Error: {e}"
        st.error(f"❌ {error_msg}")
    
    # Always display summary metrics if we have stats
    if stats is not None:
        st.markdown("### 📊 Data Summary")
        metric_cols = st.columns(4)
        
        total = int(stats.get('total', 0))
        fresh = int(stats.get('fresh', 0))
        dry = int(stats.get('dry', 0))
        time_period = str(stats.get('time_period', 'Unknown'))
        
        reject_rate = (dry / total * 100) if total > 0 else 0
        accept_rate = (fresh / total * 100) if total > 0 else 0
        
        metric_cols[0].metric("Total Processed", f"{total:,}")
        metric_cols[1].metric("Fresh (Accepted)", f"{fresh:,}", f"{accept_rate:.1f}%")
        metric_cols[2].metric("Dry (Rejected)", f"{dry:,}", f"{reject_rate:.1f}%")
        
        status = "🟢 OK" if reject_rate <= 5 else "🟡 WARNING" if reject_rate <= 15 else "🔴 CRITICAL"
        metric_cols[3].metric("Status", status)
        
        st.caption(f"📅 Time Period: {time_period}")
        
        # Always show generate button
        st.markdown("---")
        col_btn, col_info = st.columns([1, 2])
        
        with col_btn:
            button_disabled = total == 0 or error_msg is not None
            button_label = "🤖 Generate AI Report" if not button_disabled else "⚠️ No Data to Report"
            
            if st.button(button_label, type="primary", disabled=button_disabled):
                with st.spinner("Generating report with AI... This may take 5-10 seconds"):
                    try:
                        reporter = GeminiQCReporter()
                        markdown_report = reporter.generate_report(
                            total=total,
                            fresh=fresh,
                            dry=dry,
                            time_period=time_period
                        )
                        st.session_state.generated_report = markdown_report
                        st.session_state.report_stats = stats
                        st.success("✅ Report generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating report: {e}")
                        st.info("💡 Make sure GEMINI_API_KEY environment variable is set.")
        
        with col_info:
            if total == 0:
                st.warning("⚠️ No data found for the selected time range. Try a different period.")
            elif total > 0:
                st.info(f"✅ Ready to generate report for {total:,} records")
    
    # Display generated report if available
    if st.session_state.generated_report:
        st.markdown("---")
        st.markdown("### 📝 Generated Report")
        
        # Display markdown preview
        with st.expander("📖 Preview Report", expanded=True):
            st.markdown(st.session_state.generated_report)
        
        # Download buttons
        st.markdown("### 💾 Download Options")
        col_pdf, col_md = st.columns(2)
        
        with col_pdf:
            if st.button("📥 Download as PDF", type="secondary"):
                try:
                    with st.spinner("Generating PDF..."):
                        pdf_gen = PDFGenerator()
                        pdf_path = pdf_gen.markdown_to_pdf(
                            st.session_state.generated_report,
                            filename=f"QC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                        
                        # Read the PDF file
                        with open(pdf_path, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        st.download_button(
                            label="💾 Save PDF",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )
                        
                        st.success(f"✅ PDF ready! Saved to: {pdf_path}")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {e}")
        
        with col_md:
            st.download_button(
                label="📄 Download Markdown",
                data=st.session_state.generated_report,
                file_name=f"QC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Smart Harvest Quality Control",
        page_icon="🫘",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Smart Harvest Quality Control Dashboard v2.0"
        }
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS for modern dark theme
    st.markdown("""
        <style>
        /* Dark theme base */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        
        [data-testid="stHeader"] {
            background-color: rgba(15, 23, 42, 0.8);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        }
        
        /* Main header card */
        .main-header {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .main-header h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .main-header p {
            font-size: 1.1em;
            opacity: 0.95;
            margin-top: 10px;
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.9em !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #f1f5f9 !important;
            font-size: 2em !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #10b981 !important;
        }
        
        /* Section headers */
        .stMarkdown h3 {
            color: #e2e8f0 !important;
            font-weight: 600 !important;
            padding-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
            margin-bottom: 20px;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
            transform: translateY(-2px);
        }
        
        /* Download buttons */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        /* Expander */
        [data-testid="stExpander"] {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        /* Info boxes */
        .stAlert {
            background: rgba(30, 41, 59, 0.8);
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        /* Dataframe */
        [data-testid="stDataFrame"] {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 12px;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stDateInput > div > div > input {
            background: rgba(30, 41, 59, 0.8);
            color: #f1f5f9;
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
        }
        
        /* Radio buttons */
        .stRadio > label {
            color: #e2e8f0 !important;
        }
        
        /* Divider */
        hr {
            border-color: rgba(148, 163, 184, 0.2);
            margin: 30px 0;
        }
        
        /* Sidebar text */
        .css-1d391kg, .st-emotion-cache-1d391kg {
            color: #e2e8f0;
        }
        
        /* Make all text readable */
        p, span, label, div {
            color: #e2e8f0;
        }
        
        /* Plotly chart background */
        .js-plotly-plot {
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🍇 Smart Harvest Quality Control Dashboard</h1>
            <p>Real-time monitoring and intelligent reporting for date fruit processing</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1e40af/ffffff?text=Smart+Harvest", use_column_width=True)
        st.markdown("### 🎛️ Dashboard Controls")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ System Info")
        st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Database connection status
        st.markdown("### 🔌 Connection Status")
        db_url = os.environ.get("DB_API")
        db_key = os.environ.get("DB_SERVICE_ROLE_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        
        if db_url and db_key:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Not Configured")
            with st.expander("🔧 Setup Instructions"):
                st.code("""
export DB_API="your_supabase_url"
export DB_SERVICE_ROLE_KEY="your_key"
                """)
        
        if gemini_key:
            st.success("✅ Gemini AI Connected")
        else:
            st.warning("⚠️ Gemini AI Not Configured")
            with st.expander("🔧 Setup Instructions"):
                st.code("""
export GEMINI_API_KEY="your_api_key"
                """)
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.markdown("View real-time quality metrics and generate comprehensive reports.")
    
    # Load data
    data = load_data()
    
    if data is None or len(data) == 0:
        st.warning("⚠️ No data found in the database.")
        st.stop()
    
    # Main metrics
    total_count = len(data)
    fresh_count = data['prediction'].value_counts().get('Fresh', 0)
    dry_count = data['prediction'].value_counts().get('Dry', 0)
    dry_percentage = (dry_count / total_count * 100) if total_count > 0 else 0
    
    # Top metrics row
    st.markdown("### 📈 Current Batch Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processed", f"{total_count:,}", help="Total items processed")
    with col2:
        st.metric("Fresh (Accepted)", f"{fresh_count:,}", f"{100-dry_percentage:.1f}%", delta_color="normal")
    with col3:
        st.metric("Dry (Rejected)", f"{dry_count:,}", f"{dry_percentage:.1f}%", delta_color="inverse")
    with col4:
        status = "🟢 OK" if dry_percentage <= 5 else "🟡 WARNING" if dry_percentage <= 15 else "🔴 CRITICAL"
        st.metric("Status", status)
    
    # Visualizations row
    st.markdown("---")
    viz_col1, viz_col2 = st.columns([1, 2])
    
    with viz_col1:
        st.markdown("### 🎯 Loss Rate Monitor")
        gauge_fig = create_gauge_chart(dry_percentage, "Rejection Rate (%)", 30)
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with viz_col2:
        st.markdown("### 📊 Distribution Analysis")
        prediction_counts = data['prediction'].value_counts().reset_index()
        prediction_counts.columns = ['prediction', 'count']
        
        pie_fig = px.pie(
            prediction_counts,
            values='count',
            names='prediction',
            title='Fresh vs Dry Classification',
            hole=0.4,
            color_discrete_map={'Fresh': '#10b981', 'Dry': '#ef4444'}
        )
        pie_fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(size=14, color='white', family='Arial')
        )
        pie_fig.update_layout(
            height=300,
            paper_bgcolor="rgba(30, 41, 59, 0.4)",
            plot_bgcolor="rgba(30, 41, 59, 0.4)",
            font=dict(color="#e2e8f0"),
            title_font=dict(color="#e2e8f0", size=16)
        )
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # Time series chart
    st.markdown("---")
    time_series_fig = create_time_series_chart(data)
    if time_series_fig:
        st.plotly_chart(time_series_fig, use_container_width=True)
    
    # Report generator section
    render_report_generator()
    
    # Data table (collapsible)
    st.markdown("---")
    with st.expander("🗂️ View Raw Data"):
        st.dataframe(data, use_container_width=True)


if __name__ == '__main__':
    main()
