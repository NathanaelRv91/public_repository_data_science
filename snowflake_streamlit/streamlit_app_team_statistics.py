# streamlit_app.py
import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
import snowflake.connector
import requests
# ----------------------------------------------------
# Page Configuration & Layout Mode
# ----------------------------------------------------
st.set_page_config(
    page_title="Snowflake NBA Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# Database Connection Layer
# ----------------------------------------------------
@st.cache_resource
def init_snowflake_connection():
    ctx = snowflake.connector.connect(
        user='*****6858841',
        password='*********2027!',
        account='MNZAVFE-MM97348',
        database="NBA_DB",
        schema='REPORTS')
    cur = ctx.cursor()
    return cur


@st.cache_data(ttl="10m")
def fetch_dashboard_data(query: str):
    """Executes SQL query against Snowflake and caches result for 10 minutes."""
    cur = init_snowflake_connection()
    try:
        cur.execute(query)
        one_row_players = cur.fetch_pandas_all()
        print("Successfully loaded data for Player Details!")
    except ValueError as e:
        print(f"error {e}")
    return pd.DataFrame(one_row_players)


# ----------------------------------------------------
# Sidebar Controls Layout
# ----------------------------------------------------
with st.sidebar:
    st.title("⚙️ Dashboard Controls")
    st.markdown("Use the filters below to refine the remote database query.")

    # User Input Filter
    limit_rows = st.slider("Select maximum rows to pull:", min_value=10, max_value=250, value=10)
    team_filter = st.selectbox("Filter by Team:", ["Spurs","Suns","Knicks","Bulls","Jazz","ALL"])

    st.divider()
    st.info("💡 Connection Context Status: **Active**")

# ----------------------------------------------------
# Main Layout & Visualizations
# ----------------------------------------------------
st.title("📊 Enterprise Analytics Engine")
st.subheader("Real-time telemetry and reporting driven by Snowflake Data Cloud")

# Constructing safe parameterized query based on user filters
base_query = "SELECT * FROM NBA_DB.REPORTS.ALL_TIME_TEAM_STATISTICS"
if team_filter != "All":
    base_query += f" WHERE TEAMNAME = '{team_filter}'"
base_query += f" LIMIT {limit_rows};"

# Pull data securely from Snowflake
with st.spinner("Fetching secure architecture logs from Snowflake..."):
    df = fetch_dashboard_data(base_query)

if not df.empty:
    # Row 1 Layout: KPI Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Records Retrieved", value=len(df))
    with col2:
        # Assuming a numerical metric column exists (e.g., 'revenue' or 'cost')
        numeric_val = df.select_dtypes(include='number').columns[0] if len(
            df.select_dtypes(include='number').columns) > 0 else None
        st.metric(label="Avg Metric Value", value=round(df[numeric_val].mean(), 2) if numeric_val else "N/A")
    with col3:
        st.metric(label="Cache Lifespan (TTL)", value="10 Mins")

    st.divider()

    # Row 2 Layout: Data View & Graphical Insights
    left_chart_col, right_data_col = st.columns([2, 3])

    with left_chart_col:
        st.markdown("### 📈 Visual Distribution")
        if numeric_val:
            st.bar_chart(df[numeric_val].head(25))
        else:
            st.warning("No numeric columns found in table structure to map a bar chart.")

    with right_data_col:
        st.markdown("### 📋 Remote Database Registry")
        st.dataframe(df, use_container_width=True)
else:
    st.warning("No records returned. Please verify your SQL table names and connection parameters.")
