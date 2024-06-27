#切换arcpy环境

from osgeo import gdal
import numpy as np
import h5py
import os
import cupy as cp
from scipy.stats.mstats import winsorize
# 打开GeoTiff文件
def get_data(fp):
    dataset = gdal.Open(fp)
    if dataset is None:
        print('无法打开数据集')
    else:
        # 读取全部波段数据
        band = dataset.GetRasterBand(1)  # 获取第一个波段
        array = band.ReadAsArray()  # 读取波段数据为NumPy数组
        dataset=array
    return dataset
def save_surrounding_median(data, year):
    # print(filename)
    if not os.path.exists(f'./工作日平均灯光亮度'):
        os.makedirs(f'./工作日平均灯光亮度')
    with h5py.File(f'./工作日平均灯光亮度/workday_ntl{year}.h5', "w") as f:
        f.create_group('data')
        f['data'].create_dataset(name=str(year), data=data)
def cal_total():
    pass
if __name__=="__main__":
    for year in range(2013,2021):
        workday_ntl_fp=fr'F:\日度夜间灯光\结果\{year}\工作日_{year}.tif'
        dataset=get_data(workday_ntl_fp)
        print(dataset.shape,dataset.dtype)
        save_surrounding_median(dataset,year)
    #行业栅格图像转hdf5
    # for i  in industry:
    #     for y in range(2012,2021):
    #         dataset=get_data(y,i,cellsize=100)
    #         save_surrounding_median(data=dataset,year=y,industry=i,cellsize=100)




