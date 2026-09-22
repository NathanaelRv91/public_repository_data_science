import requests
import pandas as pd
import json

url = "https://population.un.org/dataportalapi/api/v1/indicators"

headers = {'accept':'application/json'}
response = requests.get(url, headers = headers)
print(response.status_code)

id_list=[]
name_list=[]
short_name=[]
description=[]
display_name=[]
dimCategory=[]
variableType=[]
valueType=[]
unitScaling=[]
precision=[]
sourceId=[]
sourceName=[]
sourceYear=[]
topicId =[]
topicName = []

data = response.json()
for key,value in data.items():
    if key == 'data':
        for i in value:
            if isinstance(i,dict):
                for k,v in i.items():
                    if k == 'name':
                        name_list.append(v)
                    if k == 'id':
                        id_list.append(v)
                    if k == 'sourceYear':
                        sourceYear.append(v)
                    if k == 'shortName':
                        short_name.append(v)
                    if k == 'description':
                        description.append(v)
                    if k == 'displayName':
                        display_name.append(v)
                    if k == 'dimCategory':
                        dimCategory.append(v)
                    if k == 'variableType':
                        variableType.append(v)
                    if k == 'valueType':
                        valueType.append(v)
                    if k == 'unitScaling':
                        unitScaling.append(v)
                    if k == 'sourceId':
                        sourceId.append(v)
                    if k == 'sourceName':
                        sourceName.append(v)
                    if k == 'topicId':
                        topicId.append(v)
                    if k == 'topicName':
                        topicName.append(v)

indicator_df = pd.DataFrame({"ID":id_list,"INDICATOR_NAME":name_list,
                  "Short_Name":short_name,"Desc":description,"Display_Name":display_name,"Dim_Category":dimCategory,
                    "Variable_Type":variableType,"Value_Type":valueType,"unit_scaling":unitScaling,"Source_Id":sourceId,
                    "Source_Name":sourceName,"Topic_Id":topicId,"Topic_Name":topicName})
