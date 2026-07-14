import snowflake.snowpark as snowpark

def subcategory_counts(session: snowpark.Session):
    # 1. Fetch data into a Snowpark DataFrame
    df = session.sql("SELECT PRODUCTCATEGORY, COUNT(DISTINCT PRODUCTSUBCATEGORY) AS health_beauty_ct FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Health & Beauty' GROUP BY 1")
    df2 = session.sql("SELECT PRODUCTCATEGORY, COUNT(DISTINCT PRODUCTSUBCATEGORY) AS grocery_ct FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Edible grocery' GROUP BY 1 ")
    df3 = session.sql("SELECT PRODUCTCATEGORY, COUNT(DISTINCT PRODUCTSUBCATEGORY) AS grocery_ct FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Household care' GROUP BY 1 ")
    df4 = session.sql("SELECT PRODUCTCATEGORY, COUNT(DISTINCT PRODUCTSUBCATEGORY) AS grocery_ct FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Pet care' GROUP BY 1 ")
    # 2. Extract value for testing
    result_row = df.collect()[0]
    actual_count = result_row[1]

    result_row2 = df2.collect()[0]
    actual_count2 = result_row2[1]

    result_row3 = df3.collect()[0]
    actual_count3 = result_row3[1]

    result_row4 = df4.collect()[0]
    actual_count4 = result_row4[1]
    
    # 3. Run the assert test
    expected_count = 11
    expected_count2 = 13
    expected_count3 = 9
    expected_count4 = 6
    assert actual_count == expected_count, f"Test Failed! Expected {expected_count} rows, but got {actual_count} Health & Beauty Subcategories."
    assert actual_count2 == expected_count2, f"Test Failed! Expected {expected_count2} rows, but got {actual_count2} Grocery Subcategories."
    assert actual_count3 == expected_count3, f"Test Failed! Expected {expected_count3} rows, but got {actual_count3} Household Care Subcategories."
    assert actual_count4 == expected_count4, f"Test Failed! Expected {expected_count4} rows, but got {actual_count4} Pet Care Subcategories."
    return "All tests passed successfully!"

def banner_years(session: snowpark.Session):
    # 1. Fetch data into a Snowpark DataFrame
    df = session.sql("SELECT BANNERNAME, COUNT(DISTINCT YEAR) AS health_beauty_years FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Health & Beauty' GROUP BY 1")
    df2 = session.sql("SELECT BANNERNAME, COUNT(DISTINCT YEAR) AS grocery_years FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Edible grocery' GROUP BY 1 ")
    df3 = session.sql("SELECT BANNERNAME, COUNT(DISTINCT YEAR) AS household_years FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Household care' GROUP BY 1 ")
    df4 = session.sql("SELECT BANNERNAME, COUNT(DISTINCT YEAR) AS petcare_years FROM PRODUCTION_DB.PUBLIC.CATEGORYDATA WHERE PRODUCTCATEGORY = 'Pet care' GROUP BY 1 ")
    # 2. Extract value for testing
    result_rows = df.collect()
    result_rows = pd.DataFrame(result_rows)
    result_rows.reset_index(inplace = True)
    actual_count = result_rows['HEALTH_BEAUTY_YEARS']

    result_rows2 = df2.collect()
    result_rows2 = pd.DataFrame(result_rows2)
    result_rows2.reset_index(inplace = True)
    actual_count2 = result_rows2['GROCERY_YEARS']
    #print(actual_count2)
    result_rows3 = df3.collect()
    result_rows3 = pd.DataFrame(result_rows3)
    result_rows3.reset_index(inplace = True)
    actual_count3 = result_rows3['HOUSEHOLD_YEARS']

    result_rows4 = df4.collect()
    result_rows4 = pd.DataFrame(result_rows4)
    result_rows4.reset_index(inplace = True)
    actual_count4 = result_rows4['PETCARE_YEARS']
    
    # 3. Run the assert test
    expected_count = 8
    expected_count2 = 8
    expected_count3 = 8
    expected_count4 = 8
    assert all( i <= expected_count for i in actual_count), f"Test Failed! Expected {expected_count} rows, but got {actual_count} Health & Beauty Years."
    assert all( i <= expected_count2 for i in actual_count2), f"Test Failed! Expected {expected_count2} rows, but got {actual_count2} Grocer Years."
    assert all( i <= expected_count3 for i in actual_count3), f"Test Failed! Expected {expected_count3} rows, but got {actual_count3} Household Care Years."
    assert all( i <= expected_count4 for i in actual_count4), f"Test Failed! Expected {expected_count4} rows, but got {actual_count4} Pet Care Years."
    return "All tests passed successfully!"

def subcategory_source_table_checks(session: snowpark.Session):
    # 1. Fetch data into a Snowpark DataFrame
    df_default_health = session.sql("SELECT MAIN_CATEGORY,CHANNELNAME,FORMATNAME,ROUND(SUM(PCT_TOTAL),6) AS health_beauty_splits FROM PRODUCTION_DB.PUBLIC.CATEGORY_PROFILE WHERE MAIN_CATEGORY = 'Health & Beauty' GROUP BY 1,2,3")
    df_default_grocery = session.sql("SELECT MAIN_CATEGORY,CHANNELNAME,FORMATNAME,ROUND(SUM(PCT_TOTAL),6) AS grocery_splits FROM PRODUCTION_DB.PUBLIC.CATEGORY_PROFILE WHERE MAIN_CATEGORY = 'Edible grocery' GROUP BY 1,2,3")
    df_default_house = session.sql("SELECT MAIN_CATEGORY,CHANNELNAME,FORMATNAME,ROUND(SUM(PCT_TOTAL),6) AS household_splits FROM PRODUCTION_DB.PUBLIC.CATEGORY_PROFILE WHERE MAIN_CATEGORY = 'Household care' GROUP BY 1,2,3")
    df_default_pet = session.sql("SELECT MAIN_CATEGORY,CHANNELNAME,FORMATNAME,ROUND(SUM(PCT_TOTAL),6) AS petcare_splits FROM PRODUCTION_DB.PUBLIC.CATEGORY_PROFILE WHERE MAIN_CATEGORY = 'Pet care' GROUP BY 1,2,3")

    # 1. Health & Beauty Default Splits:
    result_row_health = df_default_health.collect()
    result_row_health = pd.DataFrame(result_row_health)
    result_row_health.reset_index(inplace = True)
    actual_total_health = result_row_health['HEALTH_BEAUTY_SPLITS']

    # 2. Grocery Default Splits:
    result_row_grocery = df_default_grocery.collect()
    result_row_grocery = pd.DataFrame(result_row_grocery)
    result_row_grocery.reset_index(inplace = True)
    actual_total_grocery = result_row_grocery['GROCERY_SPLITS']

    # 3. Household Care Default Splits:
    result_row_house = df_default_house.collect()
    result_row_house = pd.DataFrame(result_row_house)
    result_row_house.reset_index(inplace = True)
    actual_total_house = result_row_house['HOUSEHOLD_SPLITS']

    # 4. PetCare Default Splits:
    result_row_pet = df_default_pet.collect()
    result_row_pet = pd.DataFrame(result_row_pet)
    result_row_pet.reset_index(inplace = True)
    actual_total_pet = result_row_pet['PETCARE_SPLITS']
    
    expected_total = 1.0000
    
    assert all(i == expected_total for i in actual_total_health), f"Test Failed! Expected {expected_total} but got {actual_total} for subcategory totals within Health & Beauty."
    assert all(i == expected_total for i in actual_total_grocery), f"Test Failed! Expected {expected_total} but got {actual_total} for subcategory totals within Grocery."
    assert all(i == expected_total for i in actual_total_house), f"Test Failed! Expected {expected_total} but got {actual_total} for subcategory totals within Household Care."
    assert all(i == expected_total for i in actual_total_pet), f"Test Failed! Expected {expected_total} but got {actual_total} for subcategory totals within Pet Care."
    return "All tests passed successfully!"
