from imbalance.over_sampling import SMOTE
import snowflake.snowpark.functions as F
import snowflake.snowpark.types as T
from snowflake.ml.modeling.preprocessing import *
import pandas as pd 
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector as sconn

from snowflake.snowpark.context import get_active_session
session = get_active_session()

def feature_scaling_nba(session:Session,
                        ordinal_cols: list,
                        scaled_cols: list,
                        minmax_cols: list | None) -> T.Variant:
                          
  df_players = session.table('NBA_DB.REPORTS.PLAYER_STATS_VIEW')
  df_players = df_players.fillna(value='2025', subset=['last_season'])
  ordinal_cols = 'PLAYER_NAME'
  scaled_cols = ['rebounds','wins']
  ## Use Ordinal Encoding for Player Names
  my_ordinal_encoder = OrdinalEncoder(input_cols=ordinal_cols, output_cols=ordinal_cols + 'S')
  my_ordinal_encoder.fit(df_players)
  df_players = my_ordinal_encoder.transform(df_players)
                          
  ## USE Standard Scaling for Player Rebounds & Season Wins so the high values don't drive up our Points Forecasts ## 
  my_scaler = StandardScaler(input_cols=scaled_cols, output_cols=scaled_cols)
  my_scaler.fit(df_players)
  df_players = my_scaler.transform(df_players)
  df_players = df_players.to_pandas()
  ## USE MinMax Scaling for YEAR of Season ## 
  model_scaler = MinMaxScaler()
  df_players[minmax_cols] = model_scaler.fit_transform(pd.DataFrame(df_players[minmax_cols]))

  print(f"Sucessfully Transformed Features: {df_players.head(5)}")
  session.write_pandas(df_players, table_name='PLAYERS_STATS_SCALED', auto_create_table=True)




  








  
  
  
  
  
                        
