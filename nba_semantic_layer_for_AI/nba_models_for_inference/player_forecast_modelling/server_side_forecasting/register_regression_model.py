
from snowflake.snowpark.context import get_active_session
import pandas as pd
import numpy as np
import datetime as dt 
from snowflake.ml.registry import Registry 

from sklearn.model_selection import train_test_split
session = get_active_session()

sample_df = session.table("NBA_DB.REPORTS.PLAYER_X_TRAIN").limit(100)

reg = Registry(session = session)
model_version = reg.log_model(
    model=model,  
    model_name="MY_PREDICTIVE_MODEL",
    version_name="V1",
    sample_input_data = sample_df,
    comment="Initial deployment of our forecasting model."
)
