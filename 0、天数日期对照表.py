import json
import time

import pandas as pd

if __name__=="__main__":
    all_data=pd.DataFrame()
    for year in range(2012,2021):
        annual_data= {'dayOfYear':[],
               'date':[]}
        dayOfYear=[]
        date=[]
        with open(f'./万年历/{year}.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
            data = content['data']
            for month in data:
                for day in month['days']:
                    print(day['date'])
                    # time.sleep(100)
                    dayOfYear.append(day['dayOfYear'])

                    date.append(day['date'])
        # print(data)
        annual_data['dayOfYear']=dayOfYear
        annual_data['date']=date
        annual_data=pd.DataFrame(annual_data)
        annual_data['year']=year
        all_data=pd.concat([all_data,annual_data])
    all_data.to_excel(r'./result/日度分区统计/天数日期对照表.xlsx',index=False)
