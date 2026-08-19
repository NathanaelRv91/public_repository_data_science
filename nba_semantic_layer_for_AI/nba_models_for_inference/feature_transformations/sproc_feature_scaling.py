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
                        one_hot_cols: list,
                        scaled_cols: list,
                        minmax_cols: list | None) -> T.Variant:

  
                        
