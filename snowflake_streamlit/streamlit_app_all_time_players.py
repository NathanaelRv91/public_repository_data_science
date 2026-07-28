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
@st.cache_data(ttl="10m")
def fetch_dashboard_data_stats():
    """Executes SQL query against Snowflake and caches result for 10 minutes."""

    # Establish the connection
    conn = snowflake.connector.connect(
        user='janderson6858841',
        password='JamesRVandNcr2027!',
        account='MNZAVFE-MM97348',
        warehouse='COMPUTE_WH',
        database='NBA_DB',
        schema='REPORTS',
        role='ACCOUNTADMIN'
    )

    cursor = conn.cursor()

    SQL_stats = """ SELECT * FROM NBA_DB.REPORTS.ALL_TIME_PLAYERS_STATISTICS WHERE YEAR_INT >= 2021"""
    try:
        cursor.execute(SQL_stats)
        one_row_player_stats = cursor.fetchall()
        print("Successfully loaded data!:", one_row_player_stats[100])
    finally:
        cursor.close()
        conn.close()

    df_stats = pd.DataFrame(one_row_player_stats)

    ## SEASON STATS Fct Table ##
    df_stats.columns = ['INDEX', 'FIRST_NAME', 'LAST_NAME', 'PLAYER_ID', 'GAME_ID', 'GAME_DATE', 'PLAYER_TEAM_CITY',
                        'PLAYER_TEAM_NAME', 'OPP_TEAM_CITY', 'OPP_TEAM_NAME', 'SEASON_TYPE', 'GM_LABEL', 'GM_SUBLABEL',
                        'GM_NUMBER', 'WIN', 'HOME', 'MIN_PLAYED', 'POINTS', 'ASSISTS', 'BLOCKS', 'STEALS', 'FGA', 'FGM',
                        'FG_PCT', 'PT3_ATT', 'PT3_FGM', 'PT3_PCT', 'FTA', 'FTM', 'FT_PCT', 'DRB', 'ORB', 'TRB', 'PF',
                        'TOS', 'PLUS_MINUS', 'PLAYER_TEAM_ID', 'OPP_TEAM_ID', 'COMMENT', 'POS', 'GAME_TIMESTAMP',
                        'YEAR_INT']
    return df_stats
    #df_stats.to_csv('all_player_season_statistics_training.csv')

def fetch_dashboard_data_players():
    """Executes SQL query against Snowflake and caches result for 10 minutes."""

    # Establish the connection
    conn = snowflake.connector.connect(
        user='janderson6858841',
        password='JamesRVandNcr2027!',
        account='MNZAVFE-MM97348',
        warehouse='COMPUTE_WH',
        database='NBA_DB',
        schema='REPORTS',
        role='ACCOUNTADMIN'
    )

    cursor = conn.cursor()

    SQL_players = """ SELECT * FROM NBA_DB.PLAYER_DATA.PLAYER_DETAILS """
    try:
        cursor.execute(SQL_players)
        one_row_players = cursor.fetchall()
        print("Successfully loaded data!:", one_row_players[100])
    except ValueError as e:
        print(f"error {e}")
    df_players = pd.DataFrame(one_row_players)
    ## PLAYER DETAILS LIST ##
    df_players.columns = ['PERSONID', 'FIRSTNAME', 'LASTNAME', 'BIRTHDATE', 'SCHOOL', 'COUNTRY', 'HEIGHTINCHES',
                          'BODYWEIGHTLBS', 'JERSEY', 'GUARD', 'FORWARD', 'CENTER', 'DLEAGUEFLAG', 'NBAFLAG',
                          'GAMESPLAYEDFLAG', 'DRAFTYEAR', 'DRAFTROUND', 'DRAFTNUMBER', 'FROMYEAR', 'TOYEAR']

    return df_players

def fetch_dashboard_career_list():
    """Executes SQL query against Snowflake and caches result for 10 minutes."""

    # Establish the connection
    conn = snowflake.connector.connect(
        user='janderson6858841',
        password='JamesRVandNcr2027!',
        account='MNZAVFE-MM97348',
        warehouse='COMPUTE_WH',
        database='NBA_DB',
        schema='REPORTS',
        role='ACCOUNTADMIN'
    )

    cursor = conn.cursor()

    SQL_stats = """ SELECT * FROM NBA_DB.REPORTS.PLAYER_CAREER_ACCOLADES """
    try:
        cursor.execute(SQL_stats)
        one_row_player_list = cursor.fetch_pandas_all()
        print("Successfully loaded data!:")
    finally:
        cursor.close()
        conn.close()

    df_list = pd.DataFrame(one_row_player_list)

    return df_list


df_list = fetch_dashboard_career_list()
st.write("### DATAFRAME COLUMNS:")
for col in range(len(df_list)):
#    if df_players.loc[col,'FIRSTNAME'] == 'Michael':
        st.write(f"{df_list.loc[col,:]}")

# ----------------------------------------------------
# Sidebar Controls Layout
# ----------------------------------------------------
with st.sidebar:
    st.title("⚙️ Dashboard Controls")
    st.markdown("Use the filters below to refine the remote database query.")

    # User Input Filter
    limit_rows = st.slider("Select maximum rows to pull:", min_value=10, max_value=250, value=25)
    team_filter = st.multiselect("Select:", df_list, default = df_list)

    st.divider()
    st.info("💡 Connection Context Status: **Active**")

# ----------------------------------------------------
# Main Layout & Visualizations
# ----------------------------------------------------
st.title("📊 Enterprise Analytics Engine")
st.subheader("Real-time NBA charting analytics and reporting driven by Snowflake Data Cloud")


if not df_list.empty:
    # Row 1 Layout: KPI Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Records Retrieved", value=len(df_list))
    with col2:
        # Assuming a numerical metric column exists (e.g., 'revenue' or 'cost')
        numeric_val = df_list.select_dtypes(include='number').columns[0] if len(
            df_list.select_dtypes(include='number').columns) > 0 else None
        st.metric(label="Avg Metric Value", value=round(df_list[numeric_val].mean(), 2) if numeric_val else "N/A")
    with col3:
        st.metric(label="Cache Lifespan (TTL)", value="10 Mins")

    st.divider()

    # Row 2 Layout: Data View & Graphical Insights
    left_chart_col, right_data_col = st.columns([2, 3])

    with left_chart_col:
        st.markdown("### 📈 Visual Distribution")
        if numeric_val:
            st.bar_chart(df_list[numeric_val].head(25))
        else:
            st.warning("No numeric columns found in table structure to map a bar chart.")

    with right_data_col:
        st.markdown("### 📋 Remote NBA ALl-Time Registry")
        st.dataframe(df_list, use_container_width=True)
