import time

import h5py
import os
files=os.listdir('./result/annual_overwork/2012/ratio')
dif=[]
for file in files:
    pairs=[]
    for i in [2013]:
        root = f'./result/annual_overwork/{i}/ratio'
        with h5py.File(root+'/'+file,'r') as f:
            print(i,f['data'][file[:-3]][:])



