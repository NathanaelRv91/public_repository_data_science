
from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import Registry 

from sklearn.model_selection import train_test_split
session = get_active_session()

sample_df = session.table("NBA_DB.PLAYER_DATA.PLAYER_DETAILS").limit(100)

reg = Registry(session = session)
model_version = reg.log_model(
    model=model,  
    model_name="MY_PREDICTIVE_MODEL",
    version_name="V1",
    sample_input_data=sample_df,
    comment="Initial deployment of our forecasting model."
)
