import os.path
import time

import pandas as pd
import h5py
import numpy as np
def read_data(year,ntl,radius):
    data=pd.read_csv(f'./工商注册原始数据/{year}indpool_all.csv',encoding='gb18030')
    print(data.columns)
    print(data.head())
    print(data['long'])
    print(data['lat'])
    print(data['Cate20code'])
    data['yindex']=data.apply(lambda x:int((x['long']-70)/(10/2400)),axis=1)
    data['xindex'] = data.apply(lambda x: int((60-x['lat'] ) / (10 / 2400)), axis=1)
    data['overwork']=data.apply(lambda x:float(ntl[x['xindex'],x['yindex']]),axis=1)
    data.to_csv(f'./result/variables/deep/{radius}x{radius}_winsor/工商企业加班情况/{year}.csv',index=False)
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
    radius=3
    if not os.path.exists(fr'./result/variables/deep/{radius}x{radius}_winsor/工商企业加班情况'):
        os.makedirs(fr'./result/variables/deep/{radius}x{radius}_winsor/工商企业加班情况')
    for year in range(2013,2014):
        t=time.time()
        ntl = 101 * np.ones((12000, 16800), dtype=np.uint8)

        with h5py.File(f'./result/annual_overwork/deep/{year}_dummy.h5', 'r') as f:
            x = list(f['data']['x'][:])
            print(len(x))
            print(np.count_nonzero(f['data']['dummy'][:] == 101))
            y = list(f['data']['y'][:])
            ntl[x, y] = f['data']['dummy'][:]
        read_data(year,ntl,radius)
        print(f"{year}年耗时{time.time()-t}")
