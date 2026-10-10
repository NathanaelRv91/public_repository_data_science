import pandas as pd
import numpy as np

oecd_list = pd.read_csv('oecd_cs_coicop2018_cleaned_oct.csv')
oecd_new = pd.DataFrame(oecd_list[['Category','Transaction']].drop_duplicates())
oecd_new.to_csv('oecd_new_list_api.csv')

oecd_yrs = pd.DataFrame(oecd_list[['Market','Year']].drop_duplicates())
oecd_yrs['key'] = 1

oecd_yrs.reset_index(inplace = True)
oecd_master_map = pd.read_csv('check_map_transform_oecd.csv')
oecd_master_map = pd.DataFrame(oecd_master_map)
oecd_master_map['key'] = 1
oecd_master_map.reset_index(inplace = True)

template = pd.merge(oecd_yrs, oecd_master_map, how = 'outer', on = 'key')
template.to_csv('check_master_template.csv')

oecd_cs_99 = pd.read_csv('final_api_df_COICOP_NEW_group3.csv')
oecd_list = pd.DataFrame(oecd_cs_99[['Category','Transaction']].drop_duplicates())

pd.DataFrame(oecd_list).to_csv('coicop_oecd_99.csv')

euro_cs = pd.read_csv('euro_cs_coicop_cleaned.csv')
euro_list = pd.DataFrame(euro_cs[['coicop','Transaction']].drop_duplicates())

pd.DataFrame(euro_list).to_csv('coicop_euro_list_api.csv')
