#切换arcpy环境

from osgeo import gdal
import numpy as np
import h5py
import os
import cupy as cp
from scipy.stats.mstats import winsorize
# 打开GeoTiff文件
def get_data(year,industry,cellsize):
    dataset = gdal.Open(f'./分行业累计栅格/{year}-{industry}-{cellsize}m-pool.tif')
    if dataset is None:
        print('无法打开数据集')
    else:
        # 读取全部波段数据
        band = dataset.GetRasterBand(1)  # 获取第一个波段
        array = band.ReadAsArray()  # 读取波段数据为NumPy数组
        dataset=array[1:12001,0:16800].astype(np.uint16)
    return dataset
def save_surrounding_median(data, year, industry,cellsize):
    # print(filename)
    if not os.path.exists(f'./分行业累计栅格'):
        os.makedirs(f'./分行业累计栅格')
    with h5py.File(f'./分行业累计栅格/{year}-{industry}-{cellsize}m.h5', "w") as f:
        f.create_group('data')
        f['data'].create_dataset(name=industry, data=data)
def cal_total():
    pass
if __name__=="__main__":
    cellsize=100
    industry=["A","B","C","D","E","F","G",
              "H","I","J","K","L","M","N",
              "O","P","Q","R"]
    #行业栅格图像转hdf5
    # for i  in industry:
    #     for y in range(2012,2021):
    #         dataset=get_data(y,i,cellsize=100)
    #         save_surrounding_median(data=dataset,year=y,industry=i,cellsize=100)

    #分年加总企业数量
    if not os.path.exists(f'./分行业累计栅格'):
        os.makedirs(f'./分行业累计栅格')
    if not os.path.exists(f'./年度企业存量栅格'):
        os.makedirs(f'./年度企业存量栅格')
    for y in range(2012, 2021):
        total_firms = cp.zeros((18, 12000, 16800), dtype=cp.uint8)
        for i in range(len(industry)):
            with h5py.File(f'./分行业累计栅格/{y}-{industry[i]}-{cellsize}m.h5', "r") as f:
                total_firms[i] = cp.array(f['data'][industry[i]][:])
        total_firms=total_firms.astype(cp.uint16)
        total_num=cp.sum(total_firms,axis=0)
        total_firms=None
        "值域检查"
        # print(total_num.shape)
        # print(cp.count_nonzero(total_num>255))
        # print(cp.max(total_num))
        # print(cp.mean(total_num))
        # print(cp.max(winsorize(total_num.get(),limits=[0.1,0.9])))
        "输出保存"
        with h5py.File(f'./年度企业存量栅格/{y}firms_position.h5', "w") as f:
            f.create_group('data')
            f['data'].create_dataset(name=str(y),data=total_num.get())
        print(f"{y}年企业总数已保存")
        # break
