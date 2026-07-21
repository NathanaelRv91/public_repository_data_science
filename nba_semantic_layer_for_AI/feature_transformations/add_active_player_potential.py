import pandas as pd
from dataclasses import dataclass
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel,tool
@dataclass
class DatasetContainer:
    """
    Report on custom business statistics direct into the data container.
         Args:
             name (str): Assigns the name to the data container.
             data (pd.DataFrame): A basic data frame with a Letter column and numeric (int) values
         Returns:
             summary (pd.Series): Returns the summary data for the dataframe (data).
    """
    name: str
    data: pd.DataFrame

    def get_summary(self) -> pd.Series:
        """ Report on custom business statistics direct into the data container.
         Args:
             name (str): Assigns the name to the data container.
             data (pd.DataFrame): A basic data frame with a Letter column and numeric (int) values
         Returns:
             summary (pd.Series): Returns the summary data for the dataframe (data).

                 """
        return self.data.describe()

@tool
def DatasetContainertool(name: str,data: pd.DataFrame) -> str:
    """
    Report on custom business statistics direct into the data container.
         Args:
             name (str): Assigns the name to the data container.
             data (pd.DataFrame): A basic data frame with a Letter column and numeric (int) values
         Returns:
             summary (pd.Series): Returns the summary data for the dataframe (data).
    """
    for i in range(len(data)):
        if data.loc[i,'isactive'] == 0:
            data.loc[i,'potential'] = 0
        else:
            data.loc[i, 'potential'] = .55
    return f"{data.iloc[2:]}"


model = LiteLLMModel(
    model_id="ollama/llama3.2",
    api_base="http://localhost:11434",
    api_key="fake-key-not-needed"
)
agent = CodeAgent(
    tools =[DatasetContainertool],
    model = model,
    additional_authorized_imports = ['pandas']
)

df = pd.read_csv('basic_player_list.csv')
df = pd.DataFrame(df)
container = DatasetContainertool(name="Players_2026", data=df)

print(container)
