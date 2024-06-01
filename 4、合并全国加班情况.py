import os
import time

import h5py
import numpy as np
import arcpy
def convert(block,nodata_value,xcell_size,ycell_size):

        with h5py.File(os.path.join(sPath,fileName), "r") as f:
            data=f["Gap_Filled_DNB_BRDF-Corrected_NTL"]['mean'][:]
        ds = np.array(data)




        hcode=int(block[1:3])
        vcode=int(block[4:])
        TiffName = oDir + os.sep + os.path.basename(fileName)[0:-3] + '.tif'  # 输出文件名(可根据实际情况改)
        # arcpy.NumPyArrayToRaster()不清楚输入参数可以查看arcpy的官方文档
        # 矩阵转为栅格
        raster = arcpy.NumPyArrayToRaster(ds, arcpy.Point(-180+((hcode)*10), 90-((vcode+1)*10)),
                                          x_cell_size=xcell_size, y_cell_size=ycell_size, value_to_nodata=nodata_value)
        # 添加地理坐标系 GCS_WGS_1984
        spatialRef = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(raster, spatialRef)
        raster.save(TiffName)


if __name__ == "__main__":
    for year in range(2020,2021):
        # intensity = 655340 * np.ones((5 * 2400, 7 * 2400), dtype=np.uint32)
        # for v in range(5):
        #     for h in range(7):
        #         inten_fp = f'./result/annual_overwork/{year}/intensity/h{h + 25}v{str(v + 3).zfill(2)}.h5'
        #         print(inten_fp)
        #         if os.path.isfile(inten_fp):
        #             with h5py.File(inten_fp, "r") as f:
        #                 data = f["data"][f'h{h + 25}v{str(v + 3).zfill(2)}'][:]
        #             intensity[v * 2400:(v + 1) * 2400, h * 2400:(h + 1) * 2400] = data
        #
        #
        #         #
        #         # dummy_fp = f'./result/annual_overwork/{year}/dummy/h{h + 25}v{str(v + 3).zfill(2)}.h5'
        # raster = arcpy.NumPyArrayToRaster(intensity, arcpy.Point(70, 10),
        #                                   x_cell_size=0.0041666667, y_cell_size=0.0041666667,
        #                                   value_to_nodata=655340)
        # spatialRef = arcpy.SpatialReference(4326)
        # arcpy.DefineProjection_management(raster, spatialRef)
        # if not os.path.exists(f'./result/annual_overwork/national/intensity'):
        #     os.makedirs(f'./result/annual_overwork/national/intensity')
        # raster.save(f'./result/annual_overwork/national/intensity/overwork_intensity{year}.tif')
        # intensity = None

        dummy = -np.ones((5 * 2400, 7 * 2400), dtype=np.uint16)
        print(dummy)
        for v in range(5):
            for h in range(7):
                dummy_fp = f'./result/annual_overwork/{year}/ratio/h{h + 25}v{str(v + 3).zfill(2)}.h5'
                print(dummy_fp)
                if os.path.isfile(dummy_fp):
                    with h5py.File(dummy_fp, "r") as f:
                        data = f["data"][f'h{h + 25}v{str(v + 3).zfill(2)}'][:]
                        dummy[v * 2400:(v + 1) * 2400, h * 2400:(h + 1) * 2400] = data
        raster = arcpy.NumPyArrayToRaster(dummy, arcpy.Point(70, 10),
                                          x_cell_size=0.0041666667, y_cell_size=0.0041666667,
                                          value_to_nodata=65535)
        print('bbbbbbbbbbbbbbbbbbbbb')
        spatialRef = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(raster, spatialRef)
        if not os.path.exists(f'./result/annual_overwork/national/dummy'):
            os.makedirs(f'./result/annual_overwork/national/dummy')
        raster.save(f'./result/annual_overwork/national/dummy/overwork_dummy{year}.tif')
    # ds = np.array(data)
    # print(np.max(ds))
    # print(np.min(ds))
    # print(np.mean(ds))
