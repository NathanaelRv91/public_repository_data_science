import pandas as pd
from langchain.agents import create_agent
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel,tool
from pydantic import BaseModel, Field

df_stat = pd.read_csv('all_time_statistics_postmerger.csv')
df = pd.read_csv('basic_player_list.csv')
df = pd.DataFrame(df)
# 2. Define the local Ollama model using the LiteLLM/OpenAI-compatible wrapper
# Ollama serves an OpenAI-compatible endpoint at localhost:11434/v1
model = LiteLLMModel(
    model_id="ollama/llama3.1",
    api_base="http://localhost:11434",
    api_key="fake-key-not-needed"
)

# 3. Create a custom tool for the agent to inspect the data frame
@tool
def review_data(df: pd.DataFrame) -> str:
    """A tool that returns the summary statistics and structure of the dataset.
    Use this tool when you need to determine the names and patterns of our player list.

    Args:
        df: A pandas Dataframe that includes the player ID, full name, first name, last name & whether
            or not the player is active.
    Returns: A strint summary about the dataframe columns shape and a preview of the data.
            """
    return f"Columns: {list(df.columns)}\nShape: {df.shape}\nFirst 5 rows:\n{df.head(5).to_string()}"

# 4. Initialize the agent with a data summary tool that uses the prompt to explore
agent = CodeAgent(
    tools =[review_data],
    model = model,
    additional_authorized_imports = ['pandas']
)

# 5. Query the agent against your dataset
prompt = (
    "Look at the dataset using your review_data tool. "
   "Use the DataFrame in the tool to return the list of players who have a first name that starts with the letter M."
    "Also report the number of players with is_active = 1."
)

response = agent.run(prompt)
print("\n--- Agent Final Answer ---")
print(response)
