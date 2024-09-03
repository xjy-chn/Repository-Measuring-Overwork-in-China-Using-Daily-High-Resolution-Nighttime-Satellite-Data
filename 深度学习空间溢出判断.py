import os
import h5py
import numpy as np
with h5py.File(fr'F:\DeepLearning\dataLoader\不进行标准化\predict\2012\019.h5','r') as f:
    label=f['data']['label'][:]
    y_hat=f['data']['predict'][:]
    x_axis=f['data']['x'][:]
    y_axis = f['data']['y'][:]
dummy=y_hat>=label
print(dummy.astype(np.uint8))
dummy=np.where(label==65535,65535,dummy)
print(dummy.shape,x_axis.shape,y_axis.shape)
print(list(x_axis))