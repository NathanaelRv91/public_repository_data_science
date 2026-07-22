from snowflake.snowpark import Session
from langchain_snowflake import SnowflakeCortexAgent
import json

connection_parameters = {
    "account": "MNZAVFE-MM97348",
    "user": "********6858841",
    "password": "**********2027!",
    "role": "cortex_user_role",
    "warehouse": "COMPUTE_WH",
    "database": "NBA_DB",
    "schema": "REPORTS"
}

# 2. Establish the Snowpark session
session = Session.builder.configs(connection_parameters).create()

agent = SnowflakeCortexAgent(
    name="NBA_DB.REPORTS.NBA_CORTEX_AGENT",
    database="NBA_DB",
    schema="REPORTS",
    session=session
)

try:
    # 3. Define your target agent and the natural language prompt
    agent_name = "NBA_DB.REPORTS.NBA_CORTEX_AGENT"
    user_prompt = "What are the columns of NBA_DB.REPORTS.PLAYER_DETAILS_SOURCE?"

    # Construct the SQL query utilizing DATA_AGENT_RUN
    # It requires the agent name and a JSON payload containing the message history
    sql_query = f"""
        SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
            '{agent_name}',
            '{{"messages": [{{"role": "user", "content": [{{"type": "text", "text": "{user_prompt}"}}]}}]}}'
        ) AS agent_response;
    """

    # 4. Execute the query and retrieve the results
    result_df = session.sql(sql_query).collect()
    raw_json_response = result_df[0]['AGENT_RESPONSE']

    # 5. Parse and print the formatted response
    parsed_response = json.loads(raw_json_response)
    print(json.dumps(parsed_response, indent=2))

finally:
    # Always clean up and close the session
    session.close()
