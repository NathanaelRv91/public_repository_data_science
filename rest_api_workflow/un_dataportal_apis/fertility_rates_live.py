import requests
import json
import pandas as pd

headers = {'Accept':'application/json', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYXRoYW5hZWxydjkxQGdtYWlsLmNvbSIsImVtYWlsIjoibmF0aGFuYWVscnY5MUBnbWFpbC5jb20iLCJ1bmlxdWVfbmFtZSI6Im5hdGhhbmFlbHJ2OTFAZ21haWwuY29tIiwibmJmIjoxNzkwMTAyMzY2LCJleHAiOjE4MjE2MzgzNjYsImlhdCI6MTc5MDEwMjM2NiwiaXNzIjoiZG90bmV0LXVzZXItand0cyIsImF1ZCI6ImRhdGEtcG9ydGFsLWFwaSJ9.YZigO90IKe5eKXJjWdKx9gP9MRVRAcvkIGPUsByvfuY'}
base_url = "https://population.un.org/dataportalapi/api/v1/data/"
params = "indicators/67/start/2005/end/2026"
url = "https://population.un.org/dataportalapi/api/v1/data/indicators/19/locations/428,682,860,360,388/start/2010/end/2026?pageSize=1000"
response = requests.get(url, headers = headers)

print(response.status_code)
data = response.json()
df = pd.json_normalize(data['data'])
df = df[df.variant == 'Median']

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
