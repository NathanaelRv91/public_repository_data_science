import streamlit as st
import requests
from snowflake.snowpark import Session

# Establish connection via Streamlit secrets
def get_snowflake_session():
    if "snowpark_session" not in st.session_state:
        st.session_state.snowpark_session = Session.builder.configs(st.secrets["snowflake"]).create()
    return st.session_state.snowpark_session


st.title("💬 Local Snowflake Cortex Analyst")


# Initialize Session
session = get_snowflake_session()

# User input text box
user_question = st.chat_input("Ask a question about your structured data:")

if user_question:
    # 1. Target the REST API endpoint inside your Snowflake region
    account_host = st.secrets["snowflake"]["account"] + ".snowflakecomputing.com"
    api_url = f"https://{account_host}/api/v2/cortex/analyst/message"

    # 2. Package request with reference to your semantic model file
    # Ensure you upload your YAML file to a Snowflake stage first (e.g., @MY_STAGE/revenue_timeseries.yaml)
    payload = {
        "semantic_model_file": "@NBA_DB.REPORTS.NBA_STAGE/nba_stat_models.yml",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_question
                    }
                ]
            }
        ]
    }

    # 3. Retrieve authentication token via current snowpark session
    conn = session._conn._conn
    token = st.secrets["snowflake"]["token"]
    st.write("Token exists:", token is not None)
    st.write("Token length:", len(token) if token else 0)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 4. Fire the request locally to the remote Cortex API
    with st.spinner("Cortex Analyst is thinking..."):
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()

            # Extract generated SQL query string
            generated_sql = None

            for item in result["message"]["content"]:
                if item["type"] == "sql":
                    generated_sql = item["statement"]
                    break

            if generated_sql is None:
                st.warning("Cortex Analyst did not return SQL.")
                st.json(result)
                st.stop()
            st.subheader("Generated SQL Query:")
            st.code(generated_sql, language="sql")

            # Execute the generated SQL query directly against your database
            df_results = session.sql(generated_sql).to_pandas()
            st.subheader("Results:")
            st.dataframe(df_results)
        else:
            st.error(f"Error {response.status_code}: {response.text}")
