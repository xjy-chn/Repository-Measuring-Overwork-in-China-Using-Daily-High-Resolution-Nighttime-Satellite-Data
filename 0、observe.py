import h5py
import numpy as np
import cupy as cp
with h5py.File(r'F:\日度夜间灯光\原始数据\result\annual_overwork\national\dummy\dummy2012.h5','r') as f:
    data=f['data']['2012'][:]
print(np.count_nonzero(data==101)/5760000)
print(data)