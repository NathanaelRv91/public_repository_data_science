import requests

url = "https://ucxmqbt-aj89853.snowflakecomputing.com/api/v2/statements"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJraW*******************firCz99zKqQ",
    "Accept": "application/json",
    "User-Agent": "myApplicationName/1.0",
}

payload = {
    "statement": "DESCRIBE TABLE NBA_DB.PLAYER_DATA.PLAYER_DETAILS;",
    "timeout": 23,
}

response = requests.post(url, json=payload, headers=headers)


data_report = []
data_response = response.json()
for key, value in data_response.items():
    if key == 'data':
        print(f"DATA: {value}")
        data_report.append(str(value))
    else:
        pass
