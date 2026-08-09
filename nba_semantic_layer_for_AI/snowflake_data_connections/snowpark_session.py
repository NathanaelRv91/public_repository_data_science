from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import ModelRegistry

session = get_active_session()

registry = ModelRegistry(session=session, database_name = "NBA_DB", schema_name = "REPORTS")

model = registry.get_model("player_forecast_main").version("v1")

lakers_player_data = session.sql("SELECT * FROM NBA_DB.REPORTS.ALL_TIME_PLAYER_STATISTICS WHERE PLAYER_TEAM_NAME = "Lakers" AND 
      YEAR_INT >= 1976 ")


predicted_df = model.run(lakers_player_data, function_name = "player_predictions") 



