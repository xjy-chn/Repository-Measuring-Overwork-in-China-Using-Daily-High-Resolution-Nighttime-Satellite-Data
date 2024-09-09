import os.path
import time

import pandas as pd
import h5py
import numpy as np
def match_Alisted_firm(data,year,radius):
    annual_data=data[data['year']==year]
    annual_data.reset_index(inplace=True,drop=True)
    # print(annual_data)
    xindex=list(annual_data['xindex'])
    yindex=list(annual_data['yindex'])
    # print(xindex,yindex)
    ntl=101*np.ones((12000,16800),dtype=np.uint8)

    with h5py.File(f'./result/annual_overwork/deep/{year}_dummy.h5','r') as f:
        x=list(f['data']['x'][:])
        print(len(x))
        print(np.count_nonzero(f['data']['dummy'][:]==101))
        y=list(f['data']['y'][:])
        ntl[x,y] = f['data']['dummy'][:]
        print(np.count_nonzero(ntl!=101))
    print(ntl.shape)
    print(np.count_nonzero(ntl==101))
    xindex=[x for x in xindex]
    yindex=[y for y in yindex]
    annual_ntl=ntl[xindex,yindex]
    print(annual_ntl.dtype,np.count_nonzero(annual_ntl==101),len(annual_ntl))
    df_ntl=pd.DataFrame(annual_ntl,columns=['overwork'])
    print(df_ntl.columns)
    print('为空的样本数量：',len(df_ntl[df_ntl['overwork']==101]))
    annual_overwork=pd.concat([annual_data,df_ntl],axis=1)
    print(len(annual_overwork))
    annual_overwork.to_excel(f'./result/variables/deep/{radius}x{radius}_winsor/上市公司/{year}.xlsx')
def ob():
    data2=pd.DataFrame()
    for year in range(2012,2021):
        # match_Alisted_firm(data,year,radius=radius)
        with h5py.File(f'./result/annual_overwork/deep/{year}_dummy.h5', 'r') as f:
            x = list(f['data']['x'][:])
            y = list(f['data']['y'][:])
        coordinate=pd.DataFrame([x,y]).T
        coordinate['year']=year
        coordinate.columns=['x','y','year']
        data2=pd.concat([data2,coordinate],axis=0)
        print(year)
    data2.to_csv('./企业办公地经纬度/工商企业注册地经纬度.csv',index=False)
if __name__=="__main__":
    radius=3
    if not os.path.exists(f'./result/variables/deep/{radius}x{radius}_winsor/上市公司'):
        os.makedirs(f'./result/variables/deep/{radius}x{radius}_winsor/上市公司')
    data = pd.read_excel('./企业办公地经纬度/处理后的企业经纬度.xlsx')

    # print(len(data[data['year']>2020]))
    for year in range(2012,2021):
        match_Alisted_firm(data,year,radius=radius)
        # ob()
