import pandas as pd
#from langchain.tools import BaseTool,tool
from langchain.agents import create_agent
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel,tool
from pydantic import BaseModel, Field
from langchain import agents
import snowflake_data as snow

#df_stat = pd.read_csv('all_time_statistics_postmerger.csv')
df_players = snow.pull_player_list()
df_players = pd.DataFrame(df_players)
# 2. Define the local Ollama model using the LiteLLM/OpenAI-compatible wrapper
# Ollama serves an OpenAI-compatible endpoint at localhost:11434/v1
model = LiteLLMModel(
    model_id="ollama/llama3.2",
    api_base="http://localhost:11434",
    api_key="fake-key-not-needed"
)

# 3. Create a custom tool for the agent to inspect the data frame
@tool
def review_data(df_players: pd.DataFrame) -> str:
    """A tool that returns the summary statistics and structure of the dataset for NBA players.
    Use this tool when you need to determine the names and patterns of our player list.

    Args:
        df_players (pd.DataFrame): A pandas Dataframe that includes the player ID, full name, first name, last name & whether
            or not the player is active.
        isactive (int): a binary indicator of whether or not the player is currently active.
        fullname (str): A player's Full Name for each id.
        firstname (str): A player's first name for each id.
        lastname (str): A player's last name for each id.
        id (int): A unique numeric identifier associated with each NBA Player.
    Returns: A string ARRAY with full player names of the filtered dataframe about the players who's name starts with the letter searched.
            """
    return f"Columns: {list(df_players.columns)}\nShape: {df_players.shape}\nFirst 10 rows:\n{df_players.head(10).to_string()}"

#my_tools = [review_data]
# 4. Initialize the agent with tool
agent = CodeAgent(
    tools =[review_data],
    model = model,
    additional_authorized_imports = ['pandas']
)

# 5. Query the agent against the dataset
prompt = (
    "Look at the dataframe of NBA players in this function. "
   "Use the review_data tool to return the list of players who have a firstname that starts with the letter J."
    "Also report the number of players with isactive = 1 from the df_players dataframe."
)

response = agent.run(prompt)
print("\n--- Agent Final Answer ---")
print(response)
