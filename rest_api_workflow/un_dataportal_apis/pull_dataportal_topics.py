
import requests
import pandas as pd

url = "https://population.un.org/dataportalapi/api/v1/topics?sort=sortOrder"

headers = {'accept':'application/json'}
response = requests.get(url, headers = headers)
print(response.status_code)
data = response.json()
list_names = []
list_ids = []
for key, value in data.items():
    if key == 'data':
        for i in value:
            print(f"{i.keys()}!")
            if isinstance(i, dict):
                for k,v in i.items():
                    if k == 'name':
                        list_names.append(v)
                    if k == 'id':
                        list_ids.append(v)

indicator_df = pd.DataFrame({"ID":list_ids,"NAME":list_names})
