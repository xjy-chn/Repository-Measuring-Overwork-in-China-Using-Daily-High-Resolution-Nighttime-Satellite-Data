import os
import time

import h5py
import numpy as np


# import arcpy
def merge_surrounding_median(daily_files):
    data2 = 2 * np.ones((12000, 16800), dtype=np.uint8)
    for file in daily_files:
        block = file[-9:-3]
        h = int(file[-8:-6])
        v = int(file[-5:-3])
        # print(file,block,h,v)
        with h5py.File(file, 'r') as f:
            data = f['data'][block][:]
        data2[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data
    with h5py.File(f'./result/surrounding_median/national/{r}x{r}_winsored/{year}/{file[-13:-10]}.h5', 'w') as f:
        f.create_group('data')
        f['data'].create_dataset(name=file[-13:-10], data=data2, compression="gzip")


if __name__ == "__main__":
    r=3
    for year in range(2012, 2021):
        days = os.listdir(f'./result/surrounding_median/{r}x{r}_winsored/{year}')
        if not os.path.exists(f'./result/surrounding_median/national/{r}x{r}_winsored/{year}'):
            os.makedirs(f'./result/surrounding_median/national/{r}x{r}_winsored/{year}')
        for day in days:
            daily_files = os.listdir(f'./result/surrounding_median/{r}x{r}_winsored/{year}/{day}')
            daily_files = [f'./result/surrounding_median/{r}x{r}_winsored/{year}/{day}' + '/' + f for f in daily_files]
            print(daily_files[0][-9:-3], daily_files[0][-13:-10])
            merge_surrounding_median(daily_files)

