import time
import matplotlib.pyplot as plt
import h5py
from osgeo import gdal
import os
import numpy as np
import cupy as cp
import numpy.ma as ma
from scipy.stats import linregress
from scipy.stats.mstats import winsorize
import pandas as pd
# 项目初始化
project_fp = "F:\popLight\测试"
databse_name = "日度灯光项目.gdb"
result_fp = project_fp + "\\" + "result"


def create_project():
    arcpy.env.workspace = project_fp
    if not os.path.exists(project_fp):
        os.makedirs(project_fp)
    if not os.path.exists(result_fp):
        os.makedirs(project_fp)
    if not os.path.exists(project_fp + '\\' + databse_name):
        arcpy.CreateFileGDB_management(arcpy.env.workspace, "日度灯光项目.gdb")


def mask():
    raster = arcpy.sa.ExtractByMask("F:\\2012pool-50m.tif",
                                    r"E:\论文数据\历年行政区划\历年行政区划\2019年中国各级行政区划\2019行政区划\市.shp")
    raster2 = arcpy.Raster("F:\\2012pool-50m.tif")
    # raster3=arcpy.Raster(r"E:\论文数据\历年行政区划\历年行政区划\2019年中国各级行政区划\2019行政区划\市.shp")
    data = arcpy.RasterToNumPyArray(raster, nodata_to_value=256)
    data2 = arcpy.RasterToNumPyArray(raster2, nodata_to_value=256)
    # data3 = arcpy.RasterToNumPyArray(raster3)
    # print(data.shape,data2.shape,data3.shape)
    # print(data[7000:7010,12000],data2[7000:7010,12000])
    print(np.count_nonzero(data == 256))
    print(np.count_nonzero(data2 == 256))
    print(data2.shape)
    return data


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


def cal_overwork_inten(year, weight=False,):
    with h5py.File(f"./result/annual_overwork/national/intensity/intensity{year}.h5", 'r') as f:
        overwork = cp.array(f['data'][f'{year}'][:], dtype=cp.uint32)
    with h5py.File(f'./年度企业存量栅格/{year}firms_position.h5', "r") as f:
        firmnum = cp.array(f['data'][f'{year}'][:], dtype=cp.uint16)
    with h5py.File(f'./工作日平均灯光亮度/workday_ntl{year}.h5', "r") as f:
        workdayntl = cp.array(f['data'][f'{year}'][:], dtype=cp.uint16)
    firmdummy = cp.where(firmnum > 0, 1, firmnum)
    overwork = cp.where(firmdummy == 0, 655350, overwork)
    print(overwork)
    roverwork=overwork/workdayntl
    roverwork=cp.where(overwork==655350,655350,roverwork)
    roverwork=cp.where(workdayntl==cp.nan,655350,roverwork)
    roverwork = cp.where(workdayntl == 0, 655350, roverwork)
    if not os.path.exists(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班绝对强度'):
        os.makedirs(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班绝对强度')
    if not os.path.exists(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班相对强度'):
        os.makedirs(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班相对强度')
    with h5py.File(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班绝对强度/{year}intensity.h5', 'w') as f:
        f.create_group('data')
        f['data'].create_dataset(name=str(year), data=overwork.get())
        f['data'].create_dataset(name='nan', data=655350)
        f['data'].create_dataset(name='description',
                                 data="使用计算出的加班强度栅格，未经过工作日平均灯光标准化，将没有企业的栅格中的加班情况赋值为空")

    with h5py.File(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班相对强度/R_{year}intensity.h5', 'w') as f:
        f.create_group('data')
        f['data'].create_dataset(name=str(year), data=roverwork.get())
        f['data'].create_dataset(name='nan', data=655350)
        f['data'].create_dataset(name='description',
                                 data="使用计算出的加班强度栅格，经过工作日平均灯光标准化将没有企业的栅格中的加班情况赋值为空")
    print(f"{year}年的加班（使用企业存量剔除不存在企业的地区）保存成功")
    if weight:
        overwork2 = overwork / firmnum
        overwork2 = cp.where(overwork == 655350, 655350, overwork2)
        roverwork2=roverwork/firmnum
        roverwork2= cp.where(roverwork == 655350, 655350, roverwork2)
        with h5py.File(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班绝对强度/numWeighted_{year}intensity.h5', 'w') as f:
            f.create_group('data')
            f['data'].create_dataset(name=str(year), data=overwork2.get())
            f['data'].create_dataset(name='nan', data=655350)
            f['data'].create_dataset(name='description',
                                     data="使用计算出的相对加班强度栅格，未经平均灯光强度标准化，将没有企业的栅格中的加班情况赋值为空,使用企业数量进行了加权")
        with h5py.File(f'./result/variables/有企业的栅格的加班情况/不去掉居民区+加班相对强度/R_numWeighted_{year}intensity.h5', 'w') as f:
            f.create_group('data')
            f['data'].create_dataset(name=str(year), data=roverwork2.get())
            f['data'].create_dataset(name='nan', data=655350)
            f['data'].create_dataset(name='description',
                                     data="使用计算出的相对加班强度栅格，经平均灯光强度标准化，将没有企业的栅格中的加班情况赋值为空,使用企业数量进行了加权")
        print(f"{year}年的企业数量加权的加班（使用企业存量剔除不存在企业的地区）保存成功")

def cal_overwork_ratio_withoutResident(year, x,y,weight=False):
    with h5py.File(f"./result/annual_overwork/national/intensity/intensity{year}.h5", 'r') as f:
        overwork = cp.array(f['data'][f'{year}'][:], dtype=cp.uint32)
    with h5py.File(f'./年度企业存量栅格/{year}firms_position.h5', "r") as f:
        firmnum = cp.array(f['data'][f'{year}'][:], dtype=cp.uint16)
    with h5py.File(f'./工作日平均灯光亮度/workday_ntl{year}.h5', "r") as f:
        workdayntl = cp.array(f['data'][f'{year}'][:], dtype=cp.uint16)
    firmdummy = cp.where(firmnum > 0, 1, firmnum)
    overwork = cp.where(firmdummy == 0, 655350, overwork)
    roverwork = overwork / workdayntl
    roverwork = cp.where(overwork == 655350, 655350, roverwork)
    roverwork = cp.where(workdayntl == cp.nan, 655350, roverwork)
    roverwork = cp.where(workdayntl == 0, 655350, roverwork)
    overwork[x,y]=655350
    roverwork[x,y]=655350
    if not os.path.exists(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班绝对强度'):
        os.makedirs(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班绝对强度')
    if not os.path.exists(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班相对强度'):
        os.makedirs(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班相对强度')
    with h5py.File(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班绝对强度/{year}intensity.h5', 'w') as f:
        f.create_group('data')
        f['data'].create_dataset(name=str(year), data=overwork.get())
        f['data'].create_dataset(name='nan', data=655350)
        f['data'].create_dataset(name='description',
                                 data="使用计算出的加班强度栅格，未经过工作日平均灯光标准化，将没有企业的栅格中的加班情况赋值为空,去掉居民区")

    with h5py.File(f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班相对强度/R_{year}intensity.h5',
                   'w') as f:
        f.create_group('data')
        f['data'].create_dataset(name=str(year), data=roverwork.get())
        f['data'].create_dataset(name='nan', data=655350)
        f['data'].create_dataset(name='description',
                                 data="使用计算出的加班强度栅格，经过工作日平均灯光标准化将没有企业的栅格中的加班情况赋值为空，去掉居民区")
    print(f"{year}年的加班（使用企业存量剔除不存在企业的地区）保存成功")
    if weight:
        overwork2 = overwork / firmnum
        overwork2 = cp.where(overwork == 655350, 655350, overwork2)
        roverwork2 = roverwork / firmnum
        roverwork2 = cp.where(roverwork == 655350, 655350, roverwork2)
        with h5py.File(
                f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班绝对强度/numWeighted_{year}intensity.h5',
                'w') as f:
            f.create_group('data')
            f['data'].create_dataset(name=str(year), data=overwork2.get())
            f['data'].create_dataset(name='nan', data=655350)
            f['data'].create_dataset(name='description',
                                     data="使用计算出的相对加班强度栅格，未经平均灯光强度标准化，将没有企业的栅格中的加班情况赋值为空,使用企业数量进行了加权，去掉居民区")
        with h5py.File(
                f'./result/variables/有企业的栅格的加班情况/去掉居民区+加班相对强度/R_numWeighted_{year}intensity.h5',
                'w') as f:
            f.create_group('data')
            f['data'].create_dataset(name=str(year), data=roverwork2.get())
            f['data'].create_dataset(name='nan', data=655350)
            f['data'].create_dataset(name='description',
                                     data="使用计算出的相对加班强度栅格，经平均灯光强度标准化，将没有企业的栅格中的加班情况赋值为空,使用企业数量进行了加权，去掉居民区")
        print(f"{year}年的企业数量加权的加班（使用企业存量剔除不存在企业的地区）保存成功")

def del_resident():
    resident=pd.read_excel('./result/variables/有企业的栅格的加班情况/居民地/原始excel数据导出.xlsx')
    print(resident.columns)
    print(len(resident))
    resident['yindex'] = resident.apply(lambda x: int((x['x'] - 70) / (10 / 2400)), axis=1)
    resident['xindex'] = resident.apply(lambda x: int((x['y'] - 10) / (10 / 2400)), axis=1)
    resident=resident[resident['xindex']>=0]
    resident.reset_index(inplace=True,drop=True)
    x,y=list(resident['xindex']),list(resident['yindex'])
    return x,y
def cal_corrcoef(year):
    blocks = construct_blocks()
    with h5py.File(f"./result/annual_overwork/national/dummy/dummy{year}.h5", 'r') as f:
        overwork = cp.array(f['data'][f'{year}'][:], dtype=cp.uint8)
    with h5py.File(f'./年度企业存量栅格/{year}firms_position.h5', "r") as f:
        firmnum = cp.array(f['data'][f'{year}'][:], dtype=cp.uint16)

    firmdummy = cp.where(firmnum > 0, 1, firmnum)
    overwork = cp.where(firmdummy == 0, 101, overwork)
    firmnum2 = cp.zeros((30, 2400, 2400),dtype=cp.uint16)
    overwork2 = 101 * cp.zeros((30, 2400, 2400),dtype=cp.uint8)
    for i in range(len(blocks)):
        h = int(blocks[i][1:3])
        v = int(blocks[i][4:6])
        print(h,v)
        firmnum2[i] = firmnum[(v - 3) * 2400:(v - 2) * 2400, (h - 25) * 2400:(h - 24) * 2400]
        overwork2[i] = overwork[(v - 3) * 2400:(v - 2) * 2400, (h - 25) * 2400:(h - 24) * 2400]
    firmnum2=firmnum2.reshape((30*2400*2400,1))
    overwork2=overwork2.reshape((30*2400*2400,1))
    include=cp.where(overwork2!=101)
    firmnum2=firmnum2[include]
    overwork2 = overwork2[include]
    # print(cp.count_nonzero(firmnum==0))
    woverwork2=winsorize(overwork2.get(),[0.01,0.01])
    wfirmnum2=winsorize(firmnum2.get(),[0.01,0.01])
    # time.sleep(100)
    corr = cp.corrcoef(overwork2,firmnum2)
    plt.ion()
    slope, intercept, r_value, p_value, std_err = linregress(overwork2.get(),firmnum2.get())
    plt.scatter(firmnum2.get(),overwork2.get(),s=3)
    plt.plot(firmnum2.get(), slope * firmnum2.get() + intercept, color='red')
    plt.xlabel(f"栅格内企业数量，R={str(corr[1,1])}")
    plt.ylabel("加班天数占比")
    plt.title("原始数据未缩尾")
    if not os.path.exists("./result/variables/描述性统计/相关性和散点图/散点图"):
        os.makedirs("./result/variables/描述性统计/相关性和散点图/散点图")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/{year}.svg")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/{year}.jpg")
    plt.show()
    plt.close()

    corr = cp.corrcoef(woverwork2,wfirmnum2)
    plt.ion()
    slope, intercept, r_value, p_value, std_err = linregress(woverwork2,wfirmnum2)
    plt.scatter(wfirmnum2,woverwork2,s=3)
    plt.plot(wfirmnum2, slope * wfirmnum2 + intercept, color='red')
    plt.xlabel(f"栅格内企业数量，R={str(corr[1,1])}")
    plt.ylabel("加班天数占比")
    plt.title("左右1%缩尾")
    if not os.path.exists("./result/variables/描述性统计/相关性和散点图/散点图"):
        os.makedirs("./result/variables/描述性统计/相关性和散点图/散点图")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/w{year}.svg")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/w{year}.jpg")
    plt.show()
    plt.close()

    corr = cp.corrcoef(overwork2.get(), wfirmnum2)
    plt.ion()
    slope, intercept, r_value, p_value, std_err = linregress(overwork2.get(), wfirmnum2)
    plt.scatter(wfirmnum2, overwork2.get(), s=3)
    plt.plot(wfirmnum2, slope * wfirmnum2 + intercept, color='red')
    plt.xlabel(f"栅格内企业数量，R={str(corr[1, 1])}")
    plt.ylabel("加班天数占比")
    plt.title("只对企业数量左右1%缩尾")
    if not os.path.exists("./result/variables/描述性统计/相关性和散点图/散点图"):
        os.makedirs("./result/variables/描述性统计/相关性和散点图/散点图")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/wx{year}.svg")
    plt.savefig(f"./result/variables/描述性统计/相关性和散点图/散点图/wx{year}.jpg")
    plt.show()
    plt.close()
    return  float(corr[1,1])


if __name__ == "__main__":
    corrs = []
    st=time.time()
    plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
    x,y=del_resident()
    for year in range(2012, 2013):
        # 保留有企业地区的加班天数占比
        cal_overwork_inten(year,weight=True)
        cal_overwork_ratio_withoutResident(year,x,y,weight=True)
        # 计算栅格层面的相关系数
        # corrs.append(cal_corrcoef(year))
    # print(corrs)
    # print('耗时：',time.time()-st)
    del_resident()
