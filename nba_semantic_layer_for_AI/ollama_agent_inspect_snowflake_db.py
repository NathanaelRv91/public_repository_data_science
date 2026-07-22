import pandas as pd
import io
from snowflake.snowpark import session
from langchain_snowflake import SnowflakeQueryTool
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
import snowflake.connector
import os
from langchain.agents import create_agent
from langchain_classic.agents import create_tool_calling_agent,AgentExecutor


@tool
def query_snowflake(sql_query: str) -> str:
    """
    Executes a SQL query against the Snowflake data warehouse and returns the results as a string.
    Use this tool whenever you need to fetch data about customers, sales, or inventory from Snowflake.

    Args:
        sql_query (str): Write a simple query to pull
    """
    try:
        # Establish connection to Snowflake
        conn = snowflake.connector.connect(
            user='**********6858841',
            password='*********2027!',
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


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

tools = [query_snowflake]
llm_with_tools = llm.bind_tools(tools)

# Create a prompt instructing the agent on its behavior
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful data analyst assistant. You have access to a Snowflake database (NBA_DB) to look up NBA statistics and player information."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# Run the agent with a natural language prompt
response = agent_executor.invoke({
    "input": "How many distinct PERSONID are in the NBA_DB.PLAYER_DATA.PLAYER_DETAILS table in the database? Generate the query and provide the count of distinct PERSONIDs."
})

print("\nFinal Answer:\n", response["output"])
