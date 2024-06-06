import os
import time

import h5py
import numpy as np
with h5py.File('001.h5','r') as f:
    data1=f['data']['001'][:]
    data1=np.array(data1,dtype=np.uint8)

print(np.max(data1))
with h5py.File('npview.h5','r') as f:
    npview=f['data']['data'][:]
    npview=np.array(npview)
with h5py.File('cpview2.h5', 'r') as f:
    cpview = f['data']['data'][:]
    cpview = np.array(cpview)
# print(npview.shape,cpview.shape)


files=os.listdir('./001')
files=['./001'+'/'+file for file in files]
data2=2*np.ones((12000, 16800),dtype=np.uint8)

for file in files:
    block=file[6:12]
    h=int(file[7:9])
    v=int(file[10:12])
    # print(file,block,h,v)
    with h5py.File(file,'r') as f:
        data=f['data'][block][:]
        print(np.max(data))
    data2[2400*(v-3):2400*(v-2),2400*(h-25):2400*(h-24)]=data


print(np.count_nonzero(data1==data2))
print(np.count_nonzero(data1!=data2))
time.sleep(10)
x,y=np.where(data2!=data1)
print(np.max(x),np.max(y))
print(np.min(x),np.min(y))
for i in range(len(x)):
    print(x[i],y[i])
    print(data1[x[i],y[i]])
    print(data2[x[i], y[i]])
    print(npview[x[i],y[i]])
    print(cpview[x[i], y[i]])
    time.sleep(2)
