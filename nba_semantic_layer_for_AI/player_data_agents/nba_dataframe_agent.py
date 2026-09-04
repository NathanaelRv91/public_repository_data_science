import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_ollama import ChatOllama
import nba_eda_functions as nba

## CLEAN DATA for feature Transformations ##
stats = nba.pull_player_data_view()
stats = pd.DataFrame(stats)
stats['FULL_NAME'] = stats['FIRST_NAME'] + ' ' + stats['LAST_NAME']
players = nba.pull_player_details()
players = pd.DataFrame(players)
players['FULL_NAME'] = players['FIRSTNAME'] + ' ' + players['LASTNAME']
stats['GM_SUBLABEL'] = stats['GM_SUBLABEL'].astype(str)
stats['GM_SUBLABEL'] = stats['GM_NUMBER'].astype(str)
stats['POINTS'] = stats['POINTS'].fillna(0)
players = players.dropna(subset ="NBAFLAG")
#print(stats.columns)

llm = ChatOllama(model = "llama3.2",temperature = .15)

agent = create_pandas_dataframe_agent(
    llm = llm,
    df = [players,stats],
    agent_type = "tool-calling",
    allow_dangerous_code = True,
    handle_parsing_errors = True,
    verbose = True
)

## Function to pull all players who are still playing in the NBA since 2022 ##
def season_stats_summary(df: pd.Dataframe, season: int) -> str:
    """
    Builds a summary report of the selected NBA season in the last 5 years.

        Args:
            season (int): Use this season to lookup all data in the dataframe (df) for statistics.
            df (pd.DataFrame): The full dataframe with

        Returns:
            summary (str) : The key statistics of that NBA season.
    """
    return f"During the {season} season: There were {df['GAME_ID'].nunique()} games played!"

response = agent.invoke("What players scored more than 200 points in a single season?")
print(response)
