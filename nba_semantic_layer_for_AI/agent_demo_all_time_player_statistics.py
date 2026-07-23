import pandas as pd
import io
from snowflake.snowpark import session
from langchain_snowflake import ChatSnowflake,SnowflakeQueryTool, SnowflakeCortexAnalyst
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool,tool
import snowflake.connector
import os
from langchain.agents import create_agent
from langchain_classic.agents import initialize_agent, create_tool_calling_agent,AgentExecutor,AgentType

def query_snowflake(sql_query: str) -> str:
    """
    Executes a SQL query against the Snowflake data warehouse and returns the results as a string.
    Use this tool whenever you need to fetch data about players,season, or individual statistics from the NBA_DB Database in Snowflake.

    Args:
        sql_query (str): Write a simple query to pull data

    Return:

    """
    try:
        # Establish connection to Snowflake
        conn = snowflake.connector.connect(
            user='janderson6858841',
            password='JamesRVandNcr2027!',
            account='MNZAVFE-MM97348',
            warehouse='COMPUTE_WH',
            database='NBA_DB',
            schema='REPORTS'
        )

        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()

        # Format columns and rows for the LLM
        columns = [desc[0] for desc in cursor.description]
        formatted_results = [dict(zip(columns, row)) for row in results]

        cursor.close()
        conn.close()

        return str(formatted_results)

    except Exception as e:
        return f"Error executing query: {str(e)}"

# 2. Wrap the function as a LangChain Tool
snowflake_tool = Tool(
    name="SnowflakeDB",
    func=query_snowflake,
    description="Use to pull information from the NBA_DB Snowflake database. Input should be a valid SQL query."
)

llm = ChatOllama(model="llama3.2", temperature= .15)
# 4. Create the Agent
tools = [snowflake_tool]
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

response = agent.invoke({"input": "List all of the distinct PLAYER_TEAM_NAME fields in the NBA_DB.REPORTS.ALL_TIME_PLAYERS_STATISTICS table."})

