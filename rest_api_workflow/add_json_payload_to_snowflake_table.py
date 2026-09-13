import json
import requests
import snowflake.connector
import datetime
# 1. Fetch your JSON payload using requests
url = "https://jsonplaceholder.typicode.com/todos/1"
#headers = {"Authorization": "Bearer YOUR_TOKEN"}

response = requests.get(url)
json_data = response.json()  # This returns a Python dictionary or list

# 2. Establish the Snowflake Connection
# Ensure your environment variables or credentials are set securely
conn = snowflake.connector.connect(
    account='UCXMQBT-AJ89853',
    user='********r91',
    password = '*********dNcr2029!',
    warehouse='COMPUTE_WH',
    database='JSON_DB',
    schema='PUBLIC'
)

cursor = conn.cursor()

try:
    # 3. Serialize Python object to a string format for safe parsing
    json_string = json.dumps(json_data)

    # 4. Insert data using PARSE_JSON to safely bind to the VARIANT column
    cursor.execute(
        "INSERT INTO MY_API_TABLE (loaded_at, json_data) SELECT %s, PARSE_JSON(%s)",
        (datetime.datetime.now(), json_string)
    )

    print(f"Successfully loaded {cursor.rowcount} record(s) into Snowflake.")

finally:
    cursor.close()
    conn.close()

