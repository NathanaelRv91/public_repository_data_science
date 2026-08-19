sproc_oversample_smote = session.sproc.register(func=sproc_oversample_smote, 
                                                name='sproc_oversample_smote', 
                                                is_permanent=True, 
                                                replace=True,
                                                stage_location='@NBA_STAGE',
                                                packages=[f'snowflake-snowpark-context',
                                                          f'skicit-learn==1.5.0',
                                                          f'pandas==2.2.3])


print(f"Current Database and schema: {session.get_fully_qualified_current_schema()}")
print(f"Current Warehouse: {session.get_current_warehouse()}")
