from databricks.sdk import WorkspaceClient
import io

w = WorkspaceClient()

local_file_path = f"C:/Users/nathaneal.richardson/PycharmProjects4/2026_market_model/df_int.csv"

catalog = "workspace"
schema = "default"
volume_name = "test_volume_market_data"
table_name = "wb_int_test_20260917"

volume_dest_path = f"/Volumes/{catalog}/{schema}/{volume_name}/local_file.csv"
warehouse_id = "256b9b686bacaca1"

print(f"Uploading {local_file_path} to {volume_dest_path}...")
with open(local_file_path, "rb") as f:
    w.files.upload(file_path=volume_dest_path, contents=f)


sql_statement = f"""
COPY INTO {catalog}.{schema}.{table_name}
FROM '{volume_dest_path}'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
"""

print(f"Ingesting file into table {catalog}.{schema}.{table_name}...")
response = w.statement_execution.execute_statement(
    warehouse_id=warehouse_id,
    statement=sql_statement
)

print("Ingestion statement submitted successfully!")
