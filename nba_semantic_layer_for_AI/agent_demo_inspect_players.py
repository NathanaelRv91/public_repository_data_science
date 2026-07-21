import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_ollama import ChatOllama


## CLEAN DATA for feature Transformations ##
stats = pd.read_csv('all_time_statistics_fcast_data.csv')
stats = pd.DataFrame(stats)
stats['FULL_NAME'] = stats['FIRST_NAME'] + ' ' + stats['LAST_NAME']
players = pd.read_csv('all_players_details.csv')
players = pd.DataFrame(players)
players['FULL_NAME'] = players['FIRSTNAME'] + ' ' + players['LASTNAME']
stats['GM_SUBLABEL'] = stats['GM_SUBLABEL'].astype(str)
stats['GM_SUBLABEL'] = stats['GM_NUMBER'].astype(str)
#print(stats.columns)

llm = ChatOllama(model = "llama3.2",temperature = .15)

agent = create_pandas_dataframe_agent(
    llm = llm,
    df = players,
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


#season_summary_2025 = season_stats_summary(df = stats, season = 2025)

response = agent.invoke("What players have the first name as Michael (FIRSTNAME = 'Michael'?")
print(response)
