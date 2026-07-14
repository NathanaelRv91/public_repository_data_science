import eurostat
import wbgapi as wb
import pandas as pd

# call Eurostat API
df = eurostat.get_data_df('demo_pjangroup')
df.to_csv('demo_pjangroup.csv')
df = pd.DataFrame(df)
df.drop('unit', axis=1, inplace=True)
df.drop('freq', axis=1, inplace=True)
df.rename(columns = {'geo\TIME_PERIOD':'MARKET'}, inplace = True)
df = df[df.sex == 'T']
df.drop('sex', axis=1, inplace=True)
df = pd.melt(df, id_vars=['age','MARKET'], var_name='Year',value_name = 'population')
df = pd.DataFrame(df)
df.reset_index(inplace = True)
df= df[df.Year.isin(['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025'])]
df.to_csv('test_population_grouping.csv')

## Create Age 0 - 24 Model ##
df_total = df[df.age == 'TOTAL']
df_total= df_total.groupby(['MARKET','Year']).population.sum()
df_total = pd.DataFrame(df_total)
df_total.reset_index(inplace = True)

## Create Age 0 - 24 Model ##
df_0_24 = df[df.age.isin(['Y10-14','Y15-19','Y20-24','Y5-9','Y_LT5'])]
df_0_24= df_0_24.groupby(['MARKET','Year']).population.sum()
df_0_24 = pd.DataFrame(df_0_24)
df_0_24.reset_index(inplace = True)
#df_0_24[df_0_24.MARKET == 'DE'].to_csv('test_population_grouping_0_24.csv')

## Create Age 25-64 Model ##
df_25_64 = df[df.age.isin(['Y25-29','Y30-34','Y35-39','Y40-44','Y45-49','Y50-54','Y55-59','Y60-64'])]
df_25_64 = df_25_64.groupby(['MARKET','Year']).population.sum()
df_25_64 = pd.DataFrame(df_25_64)
df_25_64.reset_index(inplace = True)
#df_25_64[df_25_64.MARKET == 'DE'].to_csv('test_population_grouping_25_64.csv')


## Create Age 65 & Over Model ##
df_65_plus = df[df.age.isin(['Y65-69','Y70-74','Y75-79','Y80-84','Y_GE85'])]
df_65_plus = df_65_plus.groupby(['MARKET','Year']).population.sum()
df_65_plus= pd.DataFrame(df_65_plus)
df_65_plus.reset_index(inplace = True)

df_final = df_total.merge(df_0_24, how = 'left', on = ['MARKET','Year'])

df_final = df_final.merge(df_25_64, how = 'left', on = ['MARKET','Year'])
print(df_final.columns)
df_final.columns = ['MARKET','Year','total_population','population_0_24_count','population_25_64_count']
df_final = df_final.merge(df_65_plus, how = 'left', on = ['MARKET','Year'])
df_final.columns = ['MARKET','Year','total_population','population_0_24_count','population_25_64_count','population_65_plus_count']
#df_final.to_csv('test_population_report.csv')

df_final['Population_0_24'] = df_final['population_0_24_count']/df_final['total_population']
df_final['Population_25_64'] = df_final['population_25_64_count']/df_final['total_population']
df_final['Population_65_plus'] = df_final['population_65_plus_count']/df_final['total_population']
map = pd.read_csv('map.csv')
df_final = df_final.merge(map, how = 'inner', on = 'MARKET')
df_final = df_final.iloc[:,[11,10,0,1,2,6,7,8]]
df_final.to_csv('raw_population_report.csv')
