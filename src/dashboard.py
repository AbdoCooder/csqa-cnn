"""
Building a Streamlit Dashboard that acts as the "Manager's Office."
It doesn't classify images; it looks at what the classifier did and tells humans what to do.
"""

import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
DB_URL = os.environ.get("DB_API")
DB_KEY = os.environ.get("DB_SERVICE_ROLE_KEY")

def load_data():
    """
    Connect to Supabase and fetch all rows from the logs table
    """
    if DB_URL and DB_KEY:
        supabase: Client = create_client(DB_URL, DB_KEY)
    else:
        print("CRITICAL ERROR: Failed to Connect the database")
        sys.exit(1)
    try:
        response = (
            supabase.table("logs")
            .select("*")
            .execute()
        )
        json_data = response.data or None
        df = pd.DataFrame(json_data)
        print('Data loaded successfully')
        return df
    except (KeyError, ValueError) as e:
        print(f'Error fetching data: {e}')
        return None

if __name__ == '__main__':
    st.set_page_config(page_title="Harvest Manager", layout="wide")
    st.write("# Real-time monitoring of a Smart Harvest Sorting and Quality Analysis System")

    data = load_data()
    st.write(data)
    if data is not None:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    else:
        st.warning("No data found in the database.")
        st.stop()

    total_count = len(data)
    fresh_count = (data['prediction'].value_counts())['Fresh']
    dry_count = (data['prediction'].value_counts())['Dry']
    dry_percentage = (dry_count / total_count) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric(label='Total', value=total_count)
    col2.metric(label='Fresh', value=fresh_count)
    col3.metric(label='Dry', value=dry_count)

    prediction_counts = data['prediction'].value_counts().reset_index()
    prediction_counts.columns = ['prediction', 'count']
    fig = px.pie(
        prediction_counts,
        values='count',
        names='prediction',
        title='Fresh / Dry',
        hole=0
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig)

    st.file_uploader("Choose a file")
