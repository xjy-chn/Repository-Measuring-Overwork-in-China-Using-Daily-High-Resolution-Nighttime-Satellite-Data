import json
import time

import pandas as pd

if __name__=="__main__":
    all_data=pd.DataFrame()
    for year in range(2012,2021):
        annual_data= {'dayOfYear':[],
               'date':[],
                      'weekDay':[],
                      'typedes':[],
                      'type':[],
                      'weekOfYear':[]}
        dayOfYear=[]
        weekOfYear = []
        date=[]
        weekday=[]
        types=[]
        typedes=[]
        with open(f'./万年历/{year}.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
            data = content['data']
            for month in data:
                for day in month['days']:
                    print(day)
                    print(day['date'])
                    # time.sleep(100)
                    dayOfYear.append(day['dayOfYear'])
                    weekday.append(day['weekDay'])
                    date.append(day['date'])
                    types.append(day['type'])
                    typedes.append(day['typeDes'])
                    weekOfYear.append(day['weekOfYear'])
        # print(data)
        annual_data['dayOfYear']=dayOfYear
        annual_data['date']=date
        annual_data['weekDay']=weekday
        annual_data['type']=types
        annual_data['typedes']=typedes
        annual_data['weekOfYear']=weekOfYear
        annual_data=pd.DataFrame(annual_data)
        annual_data['year']=year
        all_data=pd.concat([all_data,annual_data])
    all_data.to_excel(r'./天数日期对照表.xlsx',index=False)
