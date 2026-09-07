import requests
import pandas as pd

url = "https://ucxmqbt-aj89853.snowflakecomputing.com/api/v2/statements"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJraWQi*********fOD9Ei47WhygjeKaP8hcAyR64SmSDpg",
    "Accept": "application/json",
    "User-Agent": "myApplicationName/1.0",
}

payload = {
    "statement":
                 "LIST @NBA_DB.REPORTS.NBA_STAGE;",
    "timeout": 23,
}

response = requests.post(url, json=payload, headers=headers)
print(response.headers)
data_response = response.json()
list_stage = []
for key, value in data_response.items():
    if key == 'data':
        print(f"FOUND DATA!: {value}")
        for j in value:
            list_stage.append(j)
    else:
        pass
print(data_response)

pd.DataFrame(list_stage).to_csv('write_pandas_stage_summary.csv')
