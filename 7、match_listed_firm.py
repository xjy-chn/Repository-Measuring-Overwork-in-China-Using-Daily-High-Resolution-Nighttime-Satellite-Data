import os.path

import pandas as pd
import h5py
import numpy as np
def match_Alisted_firm(data,year):
    annual_data=data[data['year']==year]
    annual_data.reset_index(inplace=True,drop=True)
    # print(annual_data)
    xindex=list(annual_data['xindex'])
    yindex=list(annual_data['yindex'])
    # print(xindex,yindex)
    with h5py.File(f'./result/annual_overwork/national/dummy/dummy{year}.h5','r') as f:
        ntl=np.asarray(f['data'][f'{year}'])
    print(np.count_nonzero(ntl==101))
    annual_ntl=ntl[xindex,yindex]
    print(annual_ntl.dtype,np.count_nonzero(annual_ntl==101),len(annual_ntl))
    df_ntl=pd.DataFrame(annual_ntl,columns=['overwork'])
    print(df_ntl.columns)
    print(len(df_ntl[df_ntl['overwork']==101]))
    annual_overwork=pd.concat([annual_data,df_ntl],axis=1)
    print(len(annual_overwork))
    annual_overwork.to_excel(f'./result/variables/上市公司/{year}.xlsx')
if __name__=="__main__":
    if not os.path.exists('./result/variables/上市公司'):
        os.makedirs('./result/variables/上市公司')
    data = pd.read_excel('./企业办公地经纬度/处理后的企业经纬度.xlsx')
    # print(len(data[data['year']>2020]))
    for year in range(2012,2021):
        match_Alisted_firm(data,year)