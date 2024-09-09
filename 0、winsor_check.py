import os
import time

import h5py
import numpy as np
import pandas as pd
# import arcpy
from osgeo import gdal
year=2012
def construct_blocks():
    blocks = []
    delete_blocks = ['h25v07', 'h26v07', 'h27v07', 'h30v07', 'h31v07']
    for h in range(25, 32):
        for v in range(3, 8):
            block = "h{}v{}".format(h, str(v).zfill(2))
            blocks.append(block)
    # print(blocks)
    for block in delete_blocks:
        blocks.remove(block)
    return blocks
blocks=construct_blocks()
CN_holidays_no_missing = np.ones((5 * 2400, 7 * 2400), dtype=np.uint16)


for block in blocks:
    with h5py.File(f'result/overwork_nomissing/winsor/{year}/holidays/{block}.h5') as f:
        CN_holidays_no_missing[(int(block[4:6]) - 3) * 2400:(int(block[4:6]) - 2) * 2400,
        (int(block[1:3]) - 25) * 2400:(int(block[1:3]) - 24) * 2400] = np.array(f['data'][block][:], dtype=np.uint16)
        print(block[4:6], block[1:3])

with h5py.File(fr'./result/annual_overwork/deep/2012_dummy.h5','r') as f:
    x=f['data']['x'][:]
    y=f['data']['y'][:]
CN_holidays_no_missing=CN_holidays_no_missing[x,y]
print(CN_holidays_no_missing.shape)
print(np.count_nonzero(CN_holidays_no_missing<5))
pos=np.where(CN_holidays_no_missing<5)
missing_x,missing_y=x[pos],y[pos]
files=os.listdir(r'F:\日度夜间灯光\原始数据\result\daily_overwork\deep\ratio\2012')
files2=[r'F:\日度夜间灯光\原始数据\result\daily_overwork\deep\ratio\2012'+'\\'+file for file in files]
# for file in files2:
#     with h5py.File(file,'r') as f:
#         print(f['data']['dummy'][435])

for file in files:
    blocks=os.listdir(f'./2012/{file[:-3]}')
    array=65535*np.ones((12000,16800),dtype=np.uint16)
    for block in blocks:
        h = int(block[18:20])
        v = int(block[21:23])
        with h5py.File(f'./2012/{file[:-3]}'+'\\'+block,'r') as f:
            array[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL'][:]
    print('array',np.count_nonzero(array[missing_x,missing_y]!=65535))
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
