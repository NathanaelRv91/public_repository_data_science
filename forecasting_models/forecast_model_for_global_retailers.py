# Import python packages
import pandas as pd
import numpy as np 
from datetime import date
from datetime import time 
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector as sconn

from snowflake.snowpark.context import get_active_session
session = get_active_session()

pc_pivot = session.table("PRODUCTOIN_DB.PUBLIC.FCT_CONSUMER_SPEND_FORECAST")
NM = session.table("PRODUCTOIN_DB.PUBLIC.FCT_GLOBAL_RETAILER_TRANSACTIONS")

pc_pivot['ly_cs'] = pc_pivot['CONSUMER_SPENDING'].shift(1, fill_value = 0)
pc_pivot['yoy_cs'] = (pc_pivot['CONSUMER_SPENDING']/pc_pivot['ly_cs']) - 1

NM = cr.calc_cats(NM)
for i in range(len(NM)):
    if (NM.loc[i, 'level'] == 1) & \
            (NM.loc[i, 'Category1'] == 'Food and non-alcoholic beverages'):
        NM.loc[i, 'food_flag'] = 'Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 2) & \
            (NM.loc[i, 'Category2'] in ('Alcoholic beverages', 'Tobacco')):
        NM.loc[i, 'food_flag'] = 'Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 2) & \
            (NM.loc[i, 'Category2'] in ('Household textiles', 'Glassware, tableware and household utensils',
                                        'Tools and equipment for house and garden',
                                        'Medical products, appliances and equipment',
                                        'Telephone and telefax equipment', 'Newspapers, books and stationery',
                                        'Personal effects')):
        NM.loc[i, 'food_flag'] = 'Non-Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 3) & \
            (NM.loc[i, 'Category3'] in ['Non-durable household goods',
                                        'Appliances, articles and products for personal care']):
        NM.loc[i, 'food_flag'] = 'Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 4) & \
            (NM.loc[i, 'Category4'] in ['Pets and related products: Pets, pet foods, veterinary and grooming '
                                        'products for pets ']):
        NM.loc[i, 'food_flag'] = 'Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 4) & \
            (NM.loc[i, 'Category4'] in ['Garden products','Plants and flowers ']):
        NM.loc[i, 'food_flag'] = 'Non-Food'
        NM.loc[i, 'total_flag'] = 1

    elif (NM.loc[i, 'level'] == 3) & \
            (NM.loc[i, 'Category3'] in ['Clothing materials, other articles of clothing and clothing accessories',
                                        'Garments ', 'Shoes and other footwear ',
                                        'Materials for the maintenance and repair of the dwelling',
                                        'Furniture and furnishings', 'Carpets and other floor coverings',
                                        'Major household appliances whether electric or not',
                                        'Equipment for the reception, recording and reproduction of sound',
                                        'Equipment for the reception, recording and reproduction of sound and '
                                        'vision', 'Portable sound and vision devices ',
                                        'Other equipment for the reception, recording and reproduction of sound '
                                        'and picture', 'Personal computers ', 'Software ',
                                        'Photographic and cinematographic equipment and optical instruments '
                                        'cameras', 'Recording media', 'Small electric household appliances ',
                                        'Accessories for information processing equipment (keyboards, scanners, '
                                        'monitors, printers) ', 'Other recreational items and equipment ',
                                        'Calculators and other information processing equipment',
                                        'Cleaning, repair and hire of clothing ',
                                        'Major durables for outdoor and indoor recreation']):
        NM.loc[i, 'food_flag'] = 'Non-Food'
        NM.loc[i, 'total_flag'] = 1
    else:
        NM.loc[i, 'food_flag'] = np.nan
        NM.loc[i, 'total_flag'] = np.nan

NM['Cat_CS'] = NM.groupby(['RMM', 'Year', 'food_flag'])['cat_abs'].transform('sum')
NM['Total_CS'] = NM.groupby(['RMM', 'Year', 'total_flag'])['cat_abs'].transform('sum')

NM['Cat_CS'] = NM.groupby(['RMM', 'Year', 'food_flag'])['cat_abs'].transform('sum')
NM['Total_CS'] = NM.groupby(['RMM', 'Year', 'total_flag'])['cat_abs'].transform('sum')
    # clean up the data frame columns, and keep only total and food consumer spending data
NM = NM.loc[:, ['RMM', 'Year', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'food_flag', 'total_flag', 'Cat_CS', 'Total_CS']]
NM.drop_duplicates(inplace=True)
NM.dropna(inplace=True)
NM.drop(NM[NM.food_flag == 'Non-Food'].index, inplace=True)
NM.drop(['food_flag'], axis=1, inplace=True)
NM.reset_index(drop=True, inplace=True)
NM.rename(columns={"Cat_CS": "Food_CS"}, inplace=True)

# get food share of total cs
NM['food_share_cs'] = NM['Food_CS'] / NM['Total_CS']
NM= cr.fill_years(NM)
NM= cr.calc_rs(NM)
NM = cr.calc_growth(gdp5,NM)
NM = NM[NM.Year > 2008]
df = NM
###### RS growth forecast for retail model ######
df = df.sort_values(by=['RMM', 'Year']).reset_index(drop=True)
for i in range(len(df)):
    if df.loc[i, 'Food_CS'] > 0:
        df.loc[i, 'Food_CS_Final'] = df.loc[i, 'Food_CS']
        df.loc[i, 'Food_RS_Final'] = df.loc[i, 'Food_RS']
        df.loc[i, 'Total_CS_Final'] = df.loc[i, 'Total_CS']
        df.loc[i, 'Total_RS_Final'] = df.loc[i, 'Total_RS']

for i in range(len(df)):
    if math.isnan(df.loc[i,'Total_CS_Final']):
        if df.loc[i,'food_growth'] > 0:
            df.loc[i, 'Food_CS_Final'] = df.loc[i - 1, 'Food_CS_Final'] * (1 + df.loc[i, 'food_growth'])
            df.loc[i, 'Food_RS_Final'] = df.loc[i - 1, 'Food_RS_Final'] * (1 + df.loc[i, 'food_growth'])
            df.loc[i, 'Total_CS_Final'] = df.loc[i - 1, 'Total_CS_Final'] * (1 + df.loc[i, 'cs_growth'])
            df.loc[i, 'Total_RS_Final'] = df.loc[i - 1, 'Total_RS_Final'] * (1 + df.loc[i, 'cs_growth'])

df = df.loc[:, ['RMM', 'Year', 'Total_CS_Final', 'Food_CS_Final', 'Total_RS_Final', 'Food_RS_Final']]

df.rename(columns={"Food_CS_Final": "Food_CS", "Food_RS_Final": "Food_RS",
                    "Total_CS_Final": "Total_CS", "Total_RS_Final": "Total_RS"}, inplace=True)
df.dropna(inplace=True)
final_df = pc_pivot.merge(df, how='left', left_on=['RMM', 'YEAR'], right_on=['RMM', 'Year'])

## Fill missing RS values from other RS Models: assumption is slightly non-linear to ensure consistency in the forecast ##
final_df['ly_cs'] = final_df['CONSUMER_SPENDING'].shift(1, fill_value = 0)
final_df['yoy_cs'] = (final_df['CONSUMER_SPENDING']/final_df['ly_cs']) - 1
final_df.reset_index(inplace = True, drop = True)
for i in range(len(final_df)):
    if math.isnan(final_df.loc[i,'Total_RS']):
        final_df.loc[i,'Total_RS'] =  final_df.loc[i -1,'Total_RS'] * (.99 + final_df.loc[i,'yoy_cs'])
        final_df.loc[i, 'Total_CS'] = final_df.loc[i - 1, 'Total_CS'] * (.99 + final_df.loc[i, 'yoy_cs'])
        final_df.loc[i, 'Food_RS'] = final_df.loc[i - 1, 'Food_RS'] * (.99 + final_df.loc[i, 'yoy_cs'])
        final_df.loc[i, 'Food_CS'] = final_df.loc[i - 1, 'Food_CS'] * (.99 + final_df.loc[i, 'yoy_cs'])
    else:
        pass

# to prevent syntax errors with Snowflake's default naming conventions.
final_df.columns = [col.upper() for col in df.columns]

# 2. Establish connection to Snowflake
conn = snowflake.connector.connect(
    user="NATHANAEL_RICHARDSON",
    password="MY_PASSWORD",
    account="MY_ACCOUNT_IDENTIFIER",
    warehouse="WH_SMALL",
    database="PRODUCTION_DATABASE",
    schema="PUBLIC"
)

try:
    # 3. Write DataFrame to Snowflake
    # Set auto_create_table=True if the table does not exist yet
    success, nchunks, nrows, _ = write_pandas(
        conn=conn, 
        df=final_df, 
        table_name="RETAIL_SALES_FORECASTING", 
        auto_create_table=True,
        overwrite=False
    )
    print(f"Successfully uploaded {nrows} rows.")
    
finally:
    conn.close()
