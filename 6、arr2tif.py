import h5py
import numpy as np
from osgeo import gdal,ogr
# import arcpy
import os
def arr_to_tiff(array, fp, data_type,nodata_value):
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(fp, array.shape[1], array.shape[0], 1, data_type)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.GetRasterBand(1).SetNoDataValue(nodata_value)
    dataset.GetRasterBand(1).ComputeStatistics(0)

    shp_ds = ogr.Open(f'./国界/国.shp')
    layer = shp_ds.GetLayer()
    spatial_ref = layer.GetSpatialRef()
    # 设置输出 GeoTIFF 文件的地理参考信息
    dataset.SetProjection(spatial_ref.ExportToWkt())
    # 设置地理变换参数
    rows, cols = array.shape
    x_min, x_max, y_min, y_max = 70,140,10,60

    pixel_width = (x_max - x_min) / cols
    pixel_height = (y_max - y_min) / rows
    dataset.SetGeoTransform((x_min, pixel_width, 0, y_max, 0, -pixel_height))
def arcpy_to_tiff(data,fp,filename):
    raster = arcpy.NumPyArrayToRaster(data, arcpy.Point(70, 10),
                                      x_cell_size=0.0041666667, y_cell_size=0.0041666667,
                                      value_to_nodata=101)
    spatialRef = arcpy.SpatialReference(4326)
    arcpy.DefineProjection_management(raster, spatialRef)
    if not os.path.exists(fp):
        os.makedirs(fp)
    raster.save(f'{fp}/{filename}.tif')

if __name__=="__main__":
    if not os.path.exists(f'./result/variables/有企业的栅格的加班情况/tiff'):
        os.makedirs(f'./result/variables/有企业的栅格的加班情况/tiff')
    for year in range(2012,2021):
        # with h5py.File(f'./result/variables/有企业的栅格的加班情况/{year}dummy.h5') as f:
        #     data = np.array(f['data'][f'{year}'][:])
        # arr_to_tiff(data, f'./result/variables/有企业的栅格的加班情况/tiff/{year}dummy.tif', gdal.GDT_Int8, 101)
        with h5py.File(f'./result/variables/有企业的栅格的加班情况/numWeighted_{year}dummy.h5') as f:
            data = np.array(f['data'][f'{year}'][:])
        arr_to_tiff(data, f'./result/variables/有企业的栅格的加班情况/tiff/numWeighted_{year}dummy.tif', gdal.GDT_Int8, 101)