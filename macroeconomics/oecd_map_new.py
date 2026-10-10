import pandas as pd

oecd_cs = pd.read_csv('oecd_cs_coicop2018_cleaned_oct.csv')
oecd_cs_data = oecd_cs.copy()
oecd_map = pd.DataFrame(oecd_cs[['Category','Transaction']].drop_duplicates())
oecd_map.reset_index(inplace = True)
#oecd_map.to_csv('oecd_check_map.csv')

for i in range(len(oecd_map)):
###### CP01-CP05 Clean ########
    if oecd_map.loc[i,'Category'] == 'CP022':
        oecd_map.loc[i,'Transaction'] = 'Tobacco'
    elif oecd_map.loc[i,'Category'] == 'CP023':
        oecd_map.loc[i,'Transaction'] = 'Alcohol production services'
    elif oecd_map.loc[i,'Category'] == 'CP043':
        oecd_map.loc[i,'Transaction'] = 'Maintenance and repair of the dwelling'
    elif oecd_map.loc[i,'Category'] == 'CP051':
        oecd_map.loc[i,'Transaction'] = 'Furniture and furnishings, carpets and other floor coverings'
###### CP06-07 Clean ########
    elif oecd_map.loc[i,'Category'] == 'CP061':
        oecd_map.loc[i,'Transaction'] = 'Medical products, appliances and equipment'
    elif oecd_map.loc[i,'Category'] == 'CP062':
        oecd_map.loc[i,'Transaction'] = 'Outpatient services'
    elif oecd_map.loc[i,'Category'] == 'CP063':
        oecd_map.loc[i,'Transaction'] = 'Hospital services'

    elif oecd_map.loc[i,'Category'] == 'CP073':
        oecd_map.loc[i,'Transaction'] = 'Transport services'
###### CP08 Clean ########
    elif oecd_map.loc[i,'Category'] == 'CP08':
        oecd_map.loc[i,'Transaction'] = 'Communication'
    elif oecd_map.loc[i,'Category'] == 'CP081':
        oecd_map.loc[i,'Transaction'] = 'Telephone and telefax equipment'
    elif oecd_map.loc[i,'Category'] == 'CP082':
        oecd_map.loc[i,'Transaction'] = 'Postal services'
    elif oecd_map.loc[i,'Category'] == 'CP083':
        oecd_map.loc[i,'Transaction'] = 'Telephone and telefax services'
###### CP09 Clean ########
    elif oecd_map.loc[i,'Category'] == 'CP09':
        oecd_map.loc[i,'Transaction'] = 'Recreation and culture'
    elif oecd_map.loc[i,'Category'] == 'CP091':
        oecd_map.loc[i,'Transaction'] = 'Audio-visual, photographic and information processing equipment'
    elif oecd_map.loc[i,'Category'] == 'CP092':
        oecd_map.loc[i,'Transaction'] = 'Other major durables for recreation and culture'
    elif oecd_map.loc[i,'Category'] == 'CP093':
        oecd_map.loc[i,'Transaction'] = 'Other recreational items and equipment, gardens and pets'
    elif oecd_map.loc[i,'Category'] == 'CP094':
        oecd_map.loc[i,'Transaction'] = 'Recreational and cultural services'
    elif oecd_map.loc[i,'Category'] == 'CP095':
        oecd_map.loc[i,'Transaction'] = 'Newspapers, books and stationery'
    elif oecd_map.loc[i,'Category'] == 'CP096':
        oecd_map.loc[i,'Transaction'] = 'Package holidays'
    elif oecd_map.loc[i,'Category'] == 'CP097':
        oecd_map.loc[i,'Transaction'] = 'Cultural goods'
    elif oecd_map.loc[i,'Category'] == 'CP098':
        oecd_map.loc[i,'Transaction'] = 'Cultural services'

        ###### CP10-11 Clean ########
    elif oecd_map.loc[i, 'Category'] == 'CP10':
        oecd_map.loc[i, 'Transaction'] = 'Education'
    elif oecd_map.loc[i, 'Category'] == 'CP101':
        oecd_map.loc[i, 'Transaction'] = 'Pre-primary and primary education'
    elif oecd_map.loc[i, 'Category'] == 'CP105':
        oecd_map.loc[i, 'Transaction'] = 'Education not definable by level'
    elif oecd_map.loc[i, 'Category'] == 'CP11':
        oecd_map.loc[i, 'Transaction'] = 'Restaurants and hotels'
    elif oecd_map.loc[i, 'Category'] == 'CP111':
        oecd_map.loc[i,'Transaction'] = 'Catering services'
 ###### CP12-13 Clean ########
    elif oecd_map.loc[i, 'Category'] == 'CP12':
        oecd_map.loc[i, 'Transaction'] = 'Miscellaneous goods and services'
    elif oecd_map.loc[i, 'Category'] == 'CP121':
        oecd_map.loc[i, 'Transaction'] = 'Insurance'
    elif oecd_map.loc[i, 'Category'] == 'CP122':
        oecd_map.loc[i, 'Transaction'] = 'Financial services n.e.c.'
    elif oecd_map.loc[i, 'Category'] == 'CP13':
        oecd_map.loc[i, 'Transaction'] = 'Social protection'
    elif oecd_map.loc[i, 'Category'] == 'CP132':
        oecd_map.loc[i,'Transaction'] = 'Personal effects'
    elif oecd_map.loc[i, 'Category'] == 'CP133':
        oecd_map.loc[i, 'Transaction'] = 'Other services n.e.c.'
    elif oecd_map.loc[i, 'Category'] == 'CP139':
        oecd_map.loc[i, 'Transaction'] = 'Prostitution; other services n.e.c.'
    elif oecd_map.loc[i, 'Category'] == '_T':
        oecd_map.loc[i, 'Category'] = 'TOTAL'


for i in range(len(oecd_map)):
###### CP01-CP05 Clean ########
    if oecd_map.loc[i,'Category'] == 'CP133':
        oecd_map.loc[i,'Category'] = 'CP127'
    elif oecd_map.loc[i,'Category'] == 'CP132':
        oecd_map.loc[i,'Category'] = 'CP123'
    elif oecd_map.loc[i,'Category'] == 'CP122':
        oecd_map.loc[i,'Category'] = 'CP126'
    elif oecd_map.loc[i,'Category'] == 'CP13':
        oecd_map.loc[i,'Category'] = 'CP124'
    elif oecd_map.loc[i,'Category'] == 'CP139':
        oecd_map.loc[i,'Category'] = 'CP122_127'

    elif oecd_map.loc[i,'Category'] == 'CP081':
        oecd_map.loc[i,'Category'] = 'CP082'
    elif oecd_map.loc[i,'Category'] == 'CP082':
        oecd_map.loc[i,'Category'] = 'CP081'
    elif oecd_map.loc[i,'Category'] == 'CP131':
        oecd_map.loc[i,'Category'] = 'CP121'
    elif oecd_map.loc[i,'Category'] == 'CP121':
        oecd_map.loc[i,'Category'] = 'CP125'


oecd_map.to_csv('check_map_transform_oecd.csv')