import os
import time

import h5py
import numpy as np
import pandas as pd
# import arcpy
from osgeo import gdal
# with h5py.File(fr'./result/annual_overwork/deep/2012_dummy.h5','r') as f:
#     print(len(f['data']['x'][:]))
#     data=pd.DataFrame([f['data']['dummy'][:],f['data']['x'][:],f['data']['y'][:]]).T
#     data.columns=['overwork','xindex','yindex']
#     data.to_csv(fr'F:\日度夜间灯光\原始数据\result\检查工商注册原始数据和栅格\2012栅格数据.csv',index=False)


#
# dataset = gdal.Open(f'./2012pool-50m.tif')
# band = dataset.GetRasterBand(1)  # 获取第一个波段
# array = band.ReadAsArray()  # 读取波段数据为NumPy数组
# print(np.count_nonzero(array>0))
# array=array[1:12001,0:16800]
# x,y=np.where(array>0)
# print(np.count_nonzero(array>0))
# print(np.sum(array))
# data=pd.DataFrame([x,y]).T
# data.columns=['xindex','yindex']
# data.to_csv(fr'F:\日度夜间灯光\原始数据\result\检查工商注册原始数据和栅格\2012最原始栅格数据.csv',index=False)
x=7002
y=12259
files=os.listdir(r'F:\日度夜间灯光\原始数据\result\daily_overwork\deep\ratio\2012')
files2=[r'F:\日度夜间灯光\原始数据\result\daily_overwork\deep\ratio\2012'+'\\'+file for file in files]
# for file in files2:
#     with h5py.File(file,'r') as f:
#         print(f['data']['dummy'][435])

for file in files:
    with h5py.File(fr'F:\日度夜间灯光\原始数据\result\deep\surrounding_pic\5x5_winsored\2012\{file}', 'r') as f:
        print(f['data']['019'][591440])
        print(f['data']['x'][591440])
        print(f['data']['y'][591440])
    time.sleep(100)

for file in files:
    print(file)
    with h5py.File(fr'F:\DeepLearning\dataLoader\不进行标准化\predict\2012\{file}', 'r') as f:
        print(f['data']['label'][591440])
        print(f['data']['predict'][591440])
        print(f['data']['x'][591440])
        print(f['data']['y'][591440])
    time.sleep(1)
    blocks=os.listdir(f'./2012/{file[:-3]}')
    array=65535*np.ones((12000,16800),dtype=np.uint16)
    for block in blocks:
        h = int(block[18:20])
        v = int(block[21:23])
        with h5py.File(f'./2012/{file[:-3]}'+'\\'+block,'r') as f:
            array[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL'][:]
    print('array',array[x,y])
