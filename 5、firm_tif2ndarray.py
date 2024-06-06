#切换arcpy环境

from osgeo import gdal
import numpy as np
import h5py
import os
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
def cal_total()
if __name__=="__main__":
    industry=["A","B","C","D","E","F","G",
              "H","I","J","K","L","M","N",
              "O","P","Q","R"]
    for i  in industry:
        for y in range(2012,2021):
            dataset=get_data(y,i,cellsize=100)
            save_surrounding_median(data=dataset,year=y,industry=i,cellsize=100)