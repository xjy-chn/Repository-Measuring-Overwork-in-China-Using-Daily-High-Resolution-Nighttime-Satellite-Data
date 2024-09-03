import os
import time

import h5py
import numpy as np
null=[]
files=os.listdir(r'F:\日度夜间灯光\原始数据\2012')
files=[r'F:\日度夜间灯光\原始数据\2012'+'\\'+file for file in files]
files = [h5 for h5 in files if h5[-4:] != '.csv']
for file in files:
    f=os.listdir(file)
    for i in f:
        if 'h25v03' in i:
            with h5py.File(file+'\\'+i,'r') as d:
                data=d['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['DNB_BRDF-Corrected_NTL'][:]
                c1=data!=65535
                c2=data>=27
                x,y=np.where(c1&c2)
                print(len(x))
                time.sleep(1)
print(np.mean(null))
# a=np.ones((365,12000,16800),dtype=np.uint8)