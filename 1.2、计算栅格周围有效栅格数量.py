import os
import time

import numpy as np
import json
import h5py
import numpy.ma as ma


def search_day_dirs(year):
    dirs = os.listdir(f'./{year}')
    dirs = [f'./{year}' + '/' + dir for dir in dirs]
    dirs = [dir for dir in dirs if os.path.isdir(dir)]
    # print(dirs)
    return dirs


def search_h5_files(path):
    return os.listdir(path)


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


def get_days(data_year):
    # 节假日、假日、周末、工作日
    festivals, holidays, weekends, works, all = [], [], [], [], []
    with open(f'./万年历/{data_year}.json', 'r', encoding='utf-8') as file:
        content = json.load(file)
        data = content['data']
        for month in data:
            for day in month['days']:
                if day['type'] == 2:
                    festivals.append(day)
                    holidays.append(day)
                    all.append(day)
                elif day['type'] == 1:
                    holidays.append(day)
                    weekends.append(day)
                    all.append(day)
                elif day['type'] == 0:
                    works.append(day)
                    all.append(day)
    return festivals, holidays, weekends, works, all


def read_raw_h5(fp):
    with h5py.File(fp, 'r') as file:
        # 读取数据集到 NumPy 数组
        dataset = file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL']
        data_array = np.array(dataset)
        # 无效值替换为空
        # nan_indices = np.where(data_array == 65535)
        # data_array[nan_indices] = np.nan
    return data_array


def read_median_h5(fp, block):
    with h5py.File(fp, 'r') as file:
        # 读取数据集到 NumPy 数组
        dataset = file['data'][block]
        data_array = np.array(dataset)
        # 无效值替换为空
        # nan_indices = np.where(data_array == 65535)
        # data_array[nan_indices] = np.nan
    return data_array


def save(data, block, year, description):
    filename = block
    # print(filename)
    if not os.path.exists(f'./result/{year}'):
        os.makedirs(f'./result/{year}')
    with h5py.File(f'./result/{year}' + '/' + filename + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)


def save_overwork(data, block, year, description):
    filename = block
    # print(filename)
    if not os.path.exists(f'./result/{year}'):
        os.makedirs(f'./result/{year}')
    with h5py.File(f'./result/{year}' + '/' + filename + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)


def collect_block_files(year, type, annual_type):
    for block in blocks:
        block_files = []
        for day in type:
            key = str(day['dayOfYear']).zfill(3)
            for file in daily_files[f'./{year}/' + key]:
                if block in file:
                    block_files.append(f'./{year}/{key}/' + file)
                    break
        annual_type[block] = block_files
    return annual_type


def cal_median(year, annual_type):
    # 处理数据
    for key, value in annual_type.items():
        daynum = len(value)
        array = np.zeros((daynum, 2400, 2400), dtype=np.uint16)
        for i in range(daynum):
            array[i] = read_raw_h5(value[i])

        mask = np.isin(array, values_to_exclude)
        # time.sleep(100)
        median_value = ma.median(ma.array(array, mask=mask), axis=0)
        print(median_value.shape)
        description = f"{year}年{key}地区的节假日中位数"
        save(data=median_value, block=key, year=year, description=description)


def save_surrounding_valid(data, year, day, description):
    # print(filename)
    if not os.path.exists(f'./result/surrounding_valid/{year}'):
        os.makedirs(f'./result/surrounding_valid/{year}')
    with h5py.File(f'./result/surrounding_valid/{year}' + '/' + day + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=day, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)

def cal_surrounding_median_dummy():
    end=0
    for key, value in daily_files.items():
        day = key[-3:]
        year = key[2:6]
        st = time.time()
        if not os.path.isfile(f'./result/surrounding_valid/{year}' + '/' + day + '.h5'):
            st = time.time()
            ntl = -np.ones((5 * 2400, 7 * 2400), dtype=np.uint16)
            # print('ntl', ntl)
            for block in value:
                h = int(block[18:20])
                v = int(block[21:23])
                # print(key + '/' + block)
                data = read_raw_h5(key + '/' + block)
                ntl[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data
            # print(ntl.shape)
            padded_ntl = np.pad(ntl, ((1, 1), (1, 1)), 'constant', constant_values=(65535, 65535))
            # print(padded_ntl.strides)
            # print(padded_ntl.shape)
            surrounding_median = ntl
            view = np.lib.stride_tricks.as_strided(padded_ntl, shape=(12000, 16800, 3, 3), strides=(33604, 2, 33604, 2))
            # center = view[:, :, 1, 1]
            # # print(center.shape)
            view = view.reshape((12000, 16800, 9))
            fill = -np.ones((12000, 16800), dtype=np.uint16)
            view[:, :, 5] = fill
            invalid=np.count_nonzero(view==65535,axis=2)
            print(invalid.shape)
            valid=9-invalid
            valid=valid.astype(np.uint8)
            print(np.max(valid))
            save_surrounding_valid(data=valid, year=year, day=day, description=f"这是全国{year}年度{day}天的数据")
            median_values=None
            dummy_surrounding_median=None
            mask=None
            view=None
            fill=None
            padded_ntl=None
            data=None
            ntl=None
        print(f"这是全国{year}年度{day}天的数据保存完毕")
        end+=time.time()-st
        print("用时：",end)
if __name__ == "__main__":
    values_to_exclude = [65535]
    # for year in range(2012,2025):
    #     if year not in [2012,2022,2024]:
    for year in range(2012,2013):
            day_dirs = search_day_dirs(year)
            files = [search_h5_files(path) for path in day_dirs]
            daily_files = dict(zip(day_dirs, files))
            print(daily_files)
            print(daily_files.keys())
            cal_surrounding_median_dummy()
