import snowflake.connector
from langchain_core.tools import tool
from langchain_classic.memory import ConversationBufferMemory
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

# Connect to Snowflake
conn = snowflake.connector.connect(
    user="******91",
    password="********2029!",
    account="*******-AJ89853",
    warehouse="COMPUTE_WH",
    database="NBA_DB",
    schema="REPORTS"
)

# Define a tool for the agent to query Snowflake
@tool
def query_snowflake(sql: str) -> str:
    """Executes a SQL query against the Snowflake database and returns results."""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetch_pandas_all()
        return rows
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cur.close()

# Initialize local Ollama model (make sure `ollama serve` is running)
llm = ChatOllama(model="qwen2.5:7b", temperature=0.15)

tools = [query_snowflake]

# Create the agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to a Snowflake database. Use the query_snowflake tool to answer user questions.")
])

agent = create_react_agent(model=llm,
                     tools=tools)

# Run a test query
response = agent.invoke(
    {"messages": [{"role": "user", "content": "What are the names of the tables in the NBA_DB.REPORTS Schema?"}]},
)
print(response)
for key, value in response.items():
    print(f"{key}: {value}")
    

