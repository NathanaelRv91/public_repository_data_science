import requests
import json
import pandas as pd

url = "https://population.un.org/dataportalapi/api/v1/locations?sort=id"

headers = {'Accept':'application/json'}

response = requests.get(url, headers = headers)
print(response.status_code)

data = response.json()
df = pd.json_normalize(data['data'])

while data['nextPage'] != None:
    # Reset the target to the next page
    target = data['nextPage']

    #call the API for the next page
    response = requests.get(target)

    # Convert response to JSON format
    data = response.json()

    # Store the next page in a data frame
    df_temp = pd.json_normalize(data['data'])

    # Append next page to the data frame
    df = pd.concat([df,df_temp], axis = 0)

df.to_csv('un_prospects_locations.csv')
print(df.columns)
