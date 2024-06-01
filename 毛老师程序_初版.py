import json
import os
import h5py
import numpy as np
from osgeo import gdal, ogr


def read_h5(fp):
    with h5py.File(fp, 'r') as file:
        # 读取数据集到 NumPy 数组
        dataset = file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL']
        data_array = np.array(dataset)
        # 无效值替换为0
        nan_indices = np.where(data_array == 65535)
        data_array[nan_indices] = 0
    return data_array


def arr_to_tiff(array, fp, data_type):
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(fp, array.shape[1], array.shape[0], 1, data_type)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.GetRasterBand(1).SetNoDataValue(9999.0)
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


def clip_tiff(shapefile_path, tiff_path, output_path):
    shapefile = ogr.Open(shapefile_path)
    layer = shapefile.GetLayer()
    tiff_dataset = gdal.Open(tiff_path)
    output_dataset = gdal.Warp(output_path, tiff_dataset, cutlineDSName=shapefile_path, cutlineLayer=layer.GetName(),
                               cropToCutline=True)
    output_dataset.GetRasterBand(1).ComputeStatistics(0)
    output_dataset = None
    tiff_dataset = None
    shapefile = None


def merge_h5(h5_dir):
    array = np.zeros((5 * 2400, 7 * 2400), dtype=np.uint16)
    h5_files = [file for file in os.listdir(h5_dir)]
    for i in range(5):
        for j in range(7):
            tile_array = [h5_file for h5_file in h5_files if f'h{25 + j}v0{3 + i}' in h5_file]
            if len(tile_array) == 1:
                array[i * 2400:(i + 1) * 2400, j * 2400:(j + 1) * 2400] = read_h5(f'{h5_dir}/{tile_array[0]}')
    # 最后再 * 0.1,使用uint16生成的文件较小
    # return array * 0.1
    return array


def get_days(data_year):
    # 节假日、假日、周末、工作日
    festivals, holidays, weekends, works = [], [], [], []
    with open(f'./万年历/{data_year}.json', 'r', encoding='utf-8') as file:
        content = json.load(file)
        data = content['data']
        for month in data:
            for day in month['days']:
                if day['type'] == 2:
                    festivals.append(day)
                    holidays.append(day)
                elif day['type'] == 1:
                    holidays.append(day)
                    weekends.append(day)
                elif day['type'] == 0:
                    works.append(day)
    return festivals, holidays, weekends, works


def get_sum_array(_days, dir_path, year_dir):
    sum_array = np.zeros((5 * 2400, 7 * 2400), dtype=np.uint32)
    for _day in _days:
        day_dir = f"{_day['dayOfYear']:03}"
        # 日数据合并
        if os.path.exists(f'{dir_path}/{year_dir}/{day_dir}'):
            array = merge_h5(f'{dir_path}/{year_dir}/{day_dir}')
            sum_array += array
    return sum_array


def merge(dir_path):
    year_dirs = [file for file in os.listdir(dir_path) if os.path.isdir(f'{dir_path}/{file}')]
    for year_dir in year_dirs:
        festivals, holidays, weekends, works = get_days(year_dir)
        print(len(festivals), len(holidays), len(weekends), len(works))
        # 节假日
        festival_sum_array = get_sum_array(festivals, dir_path, year_dir)
        festival_mean_array = festival_sum_array * 0.1 / len(festivals)
        arr_to_tiff(festival_mean_array, f'E:/VNP46A2/结果/{year_dir}/节假日_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/节假日_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/节假日_{year_dir}_裁切.tif')
        # 假日
        holiday_sum_array = get_sum_array(holidays, dir_path, year_dir)
        holiday_mean_array = holiday_sum_array * 0.1 / len(holidays)
        arr_to_tiff(holiday_mean_array, f'E:/VNP46A2/结果/{year_dir}/假日_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/假日_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/假日_{year_dir}_裁切.tif')
        # 周末
        weekend_sum_array = get_sum_array(weekends, dir_path, year_dir)
        weekend_mean_array = weekend_sum_array * 0.1 / len(weekends)
        arr_to_tiff(weekend_mean_array, f'E:/VNP46A2/结果/{year_dir}/周末_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/周末_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/周末_{year_dir}_裁切.tif')
        # 工作日
        work_sum_array = get_sum_array(works, dir_path, year_dir)
        work_mean_array = work_sum_array * 0.1 / len(works)
        arr_to_tiff(work_mean_array, f'E:/VNP46A2/结果/{year_dir}/工作日_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/工作日_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/工作日_{year_dir}_裁切.tif')
        # 每年周末跟工作日的差值
        work_weekend_dif_array = work_mean_array - weekend_mean_array
        arr_to_tiff(work_weekend_dif_array, f'E:/VNP46A2/结果/{year_dir}/周末和工作日的差值_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/周末和工作日的差值_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/周末和工作日的差值_{year_dir}_裁切.tif')
        # 每年法定假日（除去周六周日）跟工作日的差值
        work_festival_dif_array = work_mean_array - festival_mean_array
        arr_to_tiff(work_festival_dif_array, f'E:/VNP46A2/结果/{year_dir}/节假日和工作日的差值_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/节假日和工作日的差值_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/节假日和工作日的差值_{year_dir}_裁切.tif')
        # 每年法定假日（包括周六周日）跟工作日的差值
        work_holiday_dif_array = work_mean_array - holiday_mean_array
        arr_to_tiff(work_holiday_dif_array, f'E:/VNP46A2/结果/{year_dir}/假日和工作日的差值_{year_dir}.tif', gdal.GDT_Float32)
        clip_tiff(f'./国界/国.shp', f'E:/VNP46A2/结果/{year_dir}/假日和工作日的差值_{year_dir}.tif',
                  f'E:/VNP46A2/结果/{year_dir}/假日和工作日的差值_{year_dir}_裁切.tif')
    return


if __name__ == '__main__':
    merge('E:/VNP46A2/源数据')


