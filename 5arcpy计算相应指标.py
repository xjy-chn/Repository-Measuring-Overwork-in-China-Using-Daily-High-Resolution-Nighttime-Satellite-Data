import arcpy
import os
import numpy as np
# 项目初始化
project_fp = "F:\popLight\测试"
databse_name = "日度灯光项目.gdb"
result_fp=project_fp+"\\"+"result"
arcpy.env.workspace = project_fp
if not os.path.exists(project_fp):
    os.makedirs(project_fp)
if not os.path.exists(result_fp):
    os.makedirs(project_fp)
if not os.path.exists(project_fp + '\\' + databse_name):
    arcpy.CreateFileGDB_management(arcpy.env.workspace, "日度灯光项目.gdb")
year = 2012


def mask():
    raster = arcpy.sa.ExtractByMask("F:\\2012pool-50m.tif", r"E:\论文数据\历年行政区划\历年行政区划\2019年中国各级行政区划\2019行政区划\市.shp")
    raster2=arcpy.Raster("F:\\2012pool-50m.tif")
    # raster3=arcpy.Raster(r"E:\论文数据\历年行政区划\历年行政区划\2019年中国各级行政区划\2019行政区划\市.shp")
    data=arcpy.RasterToNumPyArray(raster,nodata_to_value=256)
    data2 = arcpy.RasterToNumPyArray(raster2,nodata_to_value=256)
    # data3 = arcpy.RasterToNumPyArray(raster3)
    # print(data.shape,data2.shape,data3.shape)
    # print(data[7000:7010,12000],data2[7000:7010,12000])
    print(np.count_nonzero(data==256))
    print(np.count_nonzero(data2==256))
    print(data2.shape)
    return data
mask()
