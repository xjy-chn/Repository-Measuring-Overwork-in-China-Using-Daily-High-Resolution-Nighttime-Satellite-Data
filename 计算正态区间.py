import h5py
import numpy as np
import cupy as cp
from osgeo import gdal,ogr
import os
import time


def clip_tiff(shapefile_path, tiff_path, output_path):
    shapefile = ogr.Open(shapefile_path)
    layer = shapefile.GetLayer()
    tiff_dataset = gdal.Open(tiff_path)
    output_dataset = gdal.Warp(output_path, tiff_dataset, cutlineDSName=shapefile_path, cutlineLayer=layer.GetName(),
                               cropToCutline=True)
    data=cp.array(output_dataset.ReadAsArray())
    # print(cp.count_nonzero(cp.array(output_dataset.ReadAsArray())!=101))
    output_dataset.GetRasterBand(1).ComputeStatistics(0)
    output_dataset = None
    tiff_dataset = None
    shapefile = None
    return data
def arr_to_tiff(array, fp, data_type,nodata):
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(fp, array.shape[1], array.shape[0], 1, data_type)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.GetRasterBand(1).SetNoDataValue(nodata)
    dataset.GetRasterBand(1).ComputeStatistics(0)

    shp_ds = ogr.Open(f'./国界/国.shp')
    layer = shp_ds.GetLayer()
    spatial_ref = layer.GetSpatialRef()
    # 设置输出 GeoTIFF 文件的地理参考信息
    dataset.SetProjection(spatial_ref.ExportToWkt())
    # 设置地理变换参数
    rows, cols = array.shape
    x_min, x_max, y_min, y_max = layer.GetExtent()
    pixel_width = (x_max - x_min) / cols
    pixel_height = (y_max - y_min) / rows
    dataset.SetGeoTransform((x_min, pixel_width, 0, y_max, 0, -pixel_height))

    dataset.FlushCache()
    dataset = None
    shp_ds = None

if __name__=="__main__":
    for year in range(2012,2021):
        year_st=time.time()
        excluded_values=[65535]
        days=[day for day in os.listdir(f'./{year}') if day[-4:]!='.csv']
        valid_grid=cp.ones((1,len(days)))
        mean=cp.ones((1,len(days)))
        variance=cp.ones((1,len(days)))
        for i in range(len(days)):
            st = time.time()
            national=-cp.ones((12000, 16800), dtype=cp.uint16)
            files=os.listdir(f'./{year}/{days[i]}')
            if len(files)>0:
                for file in files:
                    block=file[17:23]
                    h=int(block[1:3])
                    v=int(block[4:6])
                    with h5py.File(f'./{year}/{days[i]}/{file}','r') as f:
                        data=cp.array(f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL'][:],dtype=cp.uint16)
                    national[2400*(v-3):2400*(v-2),2400*(h-25):2400*(h-24)]=data
                arr_to_tiff(national.get(),fp='./计算正态区间/临时tif/a.tif',data_type=gdal.GDT_UInt16,nodata=65535)
                ntl=clip_tiff(shapefile_path=r"F:\日度夜间灯光\国界\国.shp",
                           tiff_path='./计算正态区间/临时tif/a.tif',
                          output_path='./计算正态区间/临时tif/b.tif')
            # print(ntl.shape)
            # print(cp.count_nonzero(cp.array(ntl)!=65535))
                x,y=cp.where(cp.array(ntl,dtype=cp.uint16)!=65535)
                valid_ntl=ntl[x,y]
                valid_grid[0,i]=len(x)
                mean[0,i] = cp.mean(cp.log(valid_ntl+1))
                variance[0,i] = cp.std(cp.log(valid_ntl+1))**2
            else:
                valid_grid[0,i] = 0
                mean[0,i] = cp.nan
                variance[0,i] = cp.nan
            print(mean[0,i])
            print(variance[0,i])
            print(valid_grid[0,i])
            daily=time.time()-st
            print(f"第{year}年第{days[i]}天已计算完毕,用时{daily}秒")
        with h5py.File(f'./计算正态区间/{year}.h5','w') as f:
            f.create_group('data')
            f['data'].create_dataset(name='vaid_grid', data=valid_grid.get())
            f['data'].create_dataset(name='mean', data=mean.get())
            f['data'].create_dataset(name='std', data=variance.get())
        print(f"第{year}年已计算完毕,用时{time.time()-year_st}秒")