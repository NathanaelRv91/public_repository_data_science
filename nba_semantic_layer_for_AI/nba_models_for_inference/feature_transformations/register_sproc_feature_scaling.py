sproc_oversample_smote = session.sproc.register(func=sproc_oversample_smote, 
                                                name='sproc_oversample_smote', 
                                                is_permanent=True, 
                                                replace=True,
                                                stage_location='@ML_NBA',
                                                packages=[f'snowflake-snowpark-context',
                                                          f'skicit-learn==1.5.0',
                                                          f'pandas==2.2.3])


