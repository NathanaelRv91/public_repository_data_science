import snowflake.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from openpyxl import Workbook, load_workbook
from pandas import ExcelWriter
import xlsxwriter

ctx = snowflake.connector.connect(
    user='nathanael_richardson',
    password='my_password',
    account='xyz1234-trhresis.us-west-2',
    database='PRODUCTION',
    schema='PUBLIC',
    warehouse='WH_PRODUCTION',
    role='ACCOUNTADMIN')

cs = ctx.cursor()
query = """
create or replace temporary table Retailer_Full as (
select *,
lag(total_rank, 1, 0) over (partition by marketname,bannername order by marketname,bannername, year) as total_rank_lag,
total_rank_lag - total_rank total_rank_change

from (
select marketname 
                , bannername
                , year 
                , total_sales
                , online_sales
                , lag(total_sales, 1, 0) over (partition by marketname, bannername order by marketname, bannername, year) as total_sales_lag
              , div0(total_sales,total_sales_lag)-1 total_sales_yoy
                , total_rank
                , online_share  
from(
select marketname,bannername,sum(sales) total_sales,
  sum(case when echannel = 'Ecommerce' then sales else 0 end) online_sales, year,row_number() over (partition by marketname, year order by marketname, year
                            , sum(sales) desc) total_rank,
            row_number() over (partition by marketname, year order by marketname, year
                            , online_sales desc) online_rank,
  div0(online_sales,total_sales) online_share

 from(
 select distinct marketname
                            , bannername
                            ,echannel
                            , year(year) as year
                            , sum(sales_new) as sales 
                        from (
                            select distinct r.marketname
                                , r.bannername
                                , case 
                                    when r.formatname in ('Drive', 'Pureplay-1P', 'Pureplay-3P', 'Omnichannel-1P'
                                        , 'Omnichannel-3P') then 'Ecommerce'
                                    else 'Store-based'
                                end as echannel 
                                , sum(r.netsales / e.rate) as sales_new
                                , r.year 
                            from "PRNG"."PUBLIC"."PRNGRETAILERDATA" r 
                            join "PRNG"."PUBLIC"."EXCHANGERATE" e 
                            on r.currencycode = e.code 
                                and year(r.year) = e.year 
                            group by r.marketname
                                , r.formatname
                                , r.bannername
                                , r.year
                            order by r.marketname
                                , year(r.year)
                                , r.bannername
                        ) 
                      group by marketname
                            , bannername
                            , year
                            , echannel
                      order by marketname, bannername, year 
                      )


                      group by marketname,bannername,year
                      order by marketname, bannername, year)

order by marketname, bannername, year) where marketname in (
'United States', 'China', 'Japan', 'Germany', 'United Kingdom', 
                'Canada', 'France', 'Italy', 'South Korea', 'Spain','Mexico',
                'Sweden','Netherlands','Russia', 'Poland','Norway'
) and year in (2022,2023,2024,2025,2026,2027, 2028,2029
)
)
"""

query_2 = """
select * from Retailer_Full where total_rank < 51
"""

for sq in query.split(';'):
    print(sq)
    cs.execute(sq + ';')

for sq in query_2.split(';'):
    print(sq)
    cs.execute(sq + ';')

one_row = cs.fetchall()
col_names = []
for elt in cs.description:
    col_names.append(elt[0])

results = pd.read_sql(query_2, ctx)
df = results
df.to_csv('Banner_Pull.csv')

df['YEAR'] = df.YEAR.astype(str)
markets = df['MARKETNAME'].astype(str).unique()

for i in range(len(markets)):
    results = df[df['MARKETNAME'] == markets[i]]
    years = results['YEAR'].unique()

years = [years[0]] + [years[0]] + [years[0]] + [years[1]] + [years[1]] + [years[2]] + [years[2]] + [years[3]] + \
        [years[3]] + [years[4]] + [years[4]] + [years[0]] + [years[0]] + [years[0]] + [years[0]] + [years[0]] + \
        [years[0]] + [years[1]] + [years[1]] + [years[1]] + [years[1]] + [years[1]] + [years[1]] + [years[2]] + \
        [years[2]] + [years[2]] + [years[2]] + [years[2]] + [years[2]] + [years[3]] + [years[3]] + [years[3]] + \
        [years[3]] + [years[3]] + [years[3]] + [years[4]] + [years[4]] + [years[4]] + [years[4]] + [years[4]] + \
        [years[4]]
# replace the first year in the list with null
years[0] = ""

pivoted = df.pivot(index=['MARKETNAME', 'TOTAL_RANK'], columns='YEAR',
                   values=list(df.columns[1:])).swaplevel(0, 1, axis=1).reset_index()

# rename columns
pivoted.columns = pivoted.columns.map('_'.join)
pivoted.columns = pivoted.columns.str.rstrip('_1')

# tidy up the columns and sort appropriately
pivoted = pivoted.sort_index(axis=1)

# Redo the column list for
cols = pivoted.columns.to_list()
Columns = pd.DataFrame(cols)
Columns.to_csv('Index_Map.csv')

cols = cols[80:] + [cols[20]] + [cols[26]] + [cols[24]] + cols[21:22] + [cols[28]] + [cols[38]] + [cols[48]] + [cols[78]]

pivoted = pivoted[cols]
pivoted = pivoted.rename(columns={"MARKETNAME": "Marketname", "TOTAL_RANK": "Total_Sales_Rank"})
p_canada = pivoted[pivoted['Marketname'] == 'Canada']
p_china = pivoted[pivoted['Marketname'] == 'China']
p_france = pivoted[pivoted['Marketname'] == 'France']
p_germany = pivoted[pivoted['Marketname'] == 'Germany']
p_italy = pivoted[pivoted['Marketname'] == 'Italy']
p_japan = pivoted[pivoted['Marketname'] == 'Japan']
p_skorea = pivoted[pivoted['Marketname'] == 'South Korea']
p_spain = pivoted[pivoted['Marketname'] == 'Spain']
p_uk = pivoted[pivoted['Marketname'] == 'United Kingdom']
p_usa = pivoted[pivoted['Marketname'] == 'United States']
p_mexico = pivoted[pivoted['Marketname'] == 'Mexico']
p_netherlands = pivoted[pivoted['Marketname'] == 'Netherlands']
p_russia = pivoted[pivoted['Marketname'] == 'Russia']
p_norway = pivoted[pivoted['Marketname'] == 'Norway']
p_poland = pivoted[pivoted['Marketname'] == 'Poland']
p_sweden = pivoted[pivoted['Marketname'] == 'Sweden']

with pd.ExcelWriter("BANNERS_OUTPUT_PRIMARY.xlsx") as writer:
    workbook = writer.book
    format1 = workbook.add_format({'num_format': '$#,###,###,##0'})
    format2 = workbook.add_format({'num_format': '#0.0%'})
    red_format = workbook.add_format({'bg_color': '#FF9999'})
    green_format = workbook.add_format({'bg_color': '#99FF99'})
    header_format = workbook.add_format({'bold': True})
    header_format.set_align('center')
    # add border formats
    top_format = workbook.add_format()
    top_format.set_top(1)
    top_format.set_bottom(1)

    bottom_format = workbook.add_format()
    bottom_format.set_bottom(1)

    left_format = workbook.add_format()
    left_format.set_left(1)

    right_format = workbook.add_format()
    right_format.set_right(1)

    bottom_left_format = workbook.add_format()
    bottom_left_format.set_left(1)
    bottom_left_format.set_bottom(1)

    bottom_right_format = workbook.add_format()
    bottom_right_format.set_right(1)
    bottom_right_format.set_bottom(1)

    top_right_format = workbook.add_format()
    top_right_format.set_right(1)
    top_right_format.set_top(1)

    top_left_format = workbook.add_format()
    top_left_format.set_left(1)
    top_left_format.set_top(1)

    left_edge_format = workbook.add_format()
    left_edge_format.set_left(1)
    left_edge_format.set_top(1)
    left_edge_format.set_bottom(1)

    right_edge_format = workbook.add_format()
    right_edge_format.set_right(1)
    right_edge_format.set_top(1)
    right_edge_format.set_bottom(1)

    full_format = workbook.add_format()
    full_format.set_right(1)
    full_format.set_top(1)
    full_format.set_bottom(1)
    full_format.set_left(1)
    p_usa.to_excel(writer, sheet_name='USA', index=False, startrow=2, startcol=1)
    p_canada.to_excel(writer, sheet_name='CANADA', index=False, startrow=2, startcol=1)
    p_china.to_excel(writer, sheet_name='CHINA', index=False, startrow=2, startcol=1)
    p_france.to_excel(writer, sheet_name='FRANCE', index=False, startrow=2, startcol=1)
    p_germany.to_excel(writer, sheet_name='GERMANY', index=False, startrow=2, startcol=1)
    p_italy.to_excel(writer, sheet_name='ITALY', index=False, startrow=2, startcol=1)
    p_japan.to_excel(writer, sheet_name='JAPAN', index=False, startrow=2, startcol=1)
    p_skorea.to_excel(writer, sheet_name='S. KOREA', index=False, startrow=2, startcol=1)
    p_spain.to_excel(writer, sheet_name='SPAIN', index=False, startrow=2, startcol=1)
    p_uk.to_excel(writer, sheet_name='UK', index=False, startrow=2, startcol=1)
    p_mexico.to_excel(writer, sheet_name='MEXICO', index=False, startrow=2, startcol=1)
    p_russia.to_excel(writer, sheet_name='RUSSIA', index=False, startrow=2, startcol=1)
    p_netherlands.to_excel(writer, sheet_name='NETHERLANDS', index=False, startrow=2, startcol=1)
    p_poland.to_excel(writer, sheet_name='POLAND', index=False, startrow=2, startcol=1)
    p_sweden.to_excel(writer, sheet_name='SWEDEN', index=False, startrow=2, startcol=1)
    p_norway.to_excel(writer, sheet_name='NORWAY', index=False, startrow=2, startcol=1)

    for i in writer.sheets:
        worksheet = writer.sheets[i]  # set format for sales cells
        # worksheet.write_row(1,1,years)
        worksheet.set_column('G:G', None, format1)
        worksheet.set_column('E:E', None, format1)

        # set format for percentage cells
        worksheet.set_column('J:J', None, format2)
        worksheet.set_column('L:L', None, format2)
        worksheet.set_column('H:H', None, format2)
        worksheet.set_column('I:I', None, format2)
        worksheet.set_column('K:K', None, format2)

        worksheet.conditional_format('F4:F53', {'type': 'cell',
                                                'criteria': 'greater than',
                                                'value': 0,
                                                'format': red_format})
        worksheet.conditional_format('F4:F53', {'type': 'cell',
                                                'criteria': 'less than',
                                                'value': 0,
                                                'format': green_format})
