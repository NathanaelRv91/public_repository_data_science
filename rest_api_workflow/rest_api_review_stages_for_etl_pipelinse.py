import requests

url = "https://ucxmqbt-aj89853.snowflakecomputing.com/api/v2/statements"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJU********cAyR64SmSDpg",
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
for key, value in data_response.items():
    if key == 'data':
        print(f"FOUND DATA!: {value}")
    else:
        pass
print(data_response)
