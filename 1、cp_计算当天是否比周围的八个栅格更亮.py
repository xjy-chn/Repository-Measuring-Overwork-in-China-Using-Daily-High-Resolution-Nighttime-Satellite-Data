import os
import time

import numpy as np
import json
import h5py
import numpy.ma as ma
import cupy as cp

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
        data_array = cp.array(dataset)
        # 无效值替换为空
        # nan_indices = cp.where(data_array == 65535)
        # data_array[nan_indices] = cp.nan
    return data_array


def read_median_h5(fp, block):
    with h5py.File(fp, 'r') as file:
        # 读取数据集到 NumPy 数组
        dataset = file['data'][block]
        data_array = cp.array(dataset)
        # 无效值替换为空
        # nan_indices = cp.where(data_array == 65535)
        # data_array[nan_indices] = cp.nan
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
        array = cp.zeros((daynum, 2400, 2400), dtype=cp.uint16)
        for i in range(daynum):
            array[i] = read_raw_h5(value[i])

        mask = cp.isin(array, values_to_exclude)
        # time.sleep(100)
        median_value = ma.median(ma.array(array, mask=mask), axis=0)
        print(median_value.shape)
        description = f"{year}年{key}地区的节假日中位数"
        save(data=median_value, block=key, year=year, description=description)


def save_surrounding_median(data, year, day, block,description):
    # print(filename)
    if not os.path.exists(f'./result/surrounding_median/{year}/{day}'):
        os.makedirs(f'./result/surrounding_median/{year}/{day}')
    with h5py.File(f'./result/surrounding_median/{year}/{day}' + '/' + block + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)


def cal_surrounding_median_dummy():
    end = 0
    # pinned_mempool = cp.get_default_pinned_memory_pool()
    for key, value in daily_files.items():
        # pinned_mempool.free_all_blocks()
        day = key[-3:]
        year = key[2:6]
        st = time.time()
        ntl = -cp.ones((5 * 2400, 7 * 2400), dtype=cp.uint16)
        for block in value:
            h = int(block[18:20])
            v = int(block[21:23])
            data = read_raw_h5(key + '/' + block)
            ntl[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data
        data = None
        padded_ntl = cp.pad(ntl, ((1, 1), (1, 1)), 'constant', constant_values=(65535, 65535))
        view = cp.lib.stride_tricks.as_strided(padded_ntl, shape=(12000, 16800, 3, 3), strides=(33604, 2, 33604, 2))
        padded_ntl = None
        view = view.reshape((12000, 16800, 9))
        view2 = cp.zeros((12000, 16800, 8), dtype=cp.uint16)
        view2[:, :, 0:4] = view[:, :, 0:4]
        view2[:, :, 4:8] = view[:, :, 5:9]
        # if not os.path.exists("./测试/cp中位数/cpm"):
        #     os.makedirs("./测试/cp中位数/cpm")
        # with h5py.File(f"./测试/cp中位数/cpview2.h5", 'w') as f:
        #     f.create_group('data')
        #     f['data'].create_dataset(name="data", data=view2.get())
        # print("已保存")

        array = -cp.ones((12000, 16800, 16), dtype=cp.uint16)
        view3 = cp.where(view2 == 65535, 0, view2)
        # print(np.count_nonzero(view3==0))
        array[:, :, 0:8] = view2
        array[:, :, 8:16] = view3
        view2 = None
        view3 = None
        for block in blocks:
            if not os.path.isfile(f'./result/surrounding_median/{year}/{day}' + '/' + block + '.h5'):
                h = int(block[1:3])
                v = int(block[4:6])
                # print(h,v)
                array1 = array[2400 * (v-3):2400 * (v -2),2400 * (h-25):2400 * (h-24), :]
                # print(array1.shape)
                median_values = cp.median(array1, axis=2)
                # median_values.astype(cp.uint32)
                # median_values = median_values + 1
                # median_values = cp.array(median_values, dtype=cp.uint32)

                # median_values = cp.where(median_values == -1, 65535, median_values)
                # median_values = cp.where(median_values == 0, cp.nan, median_values)
                # median_values = median_values - 1
                # print(cp.max(median_values))
                median_values=cp.where(cp.count_nonzero(array1==65535,axis=2)==8,65535,median_values)
                # print(cp.max(median_values))
                # if not os.path.exists("./测试/cp中位数/cpm"):
                #     os.makedirs("./测试/cp中位数/cpm")
                # with h5py.File(f"./测试/cp中位数/cpm/{block}.h5",'w') as f:
                #     f.create_group('data')
                #     f['data'].create_dataset(name=block, data=median_values.get())

                # median_values = cp.where(median_values == cp.nan, 65535, median_values).astype(cp.uint16)
                dummy_surrounding_median = ntl[2400 * (v-3):2400 * (v -2),2400 * (h-25):2400 * (h -24)] > median_values
                dummy_surrounding_median=cp.where(median_values==65535,2,dummy_surrounding_median)
                dummy_surrounding_median = cp.where(ntl[2400 * (v-3):2400 * (v -2),2400 * (h-25):2400 * (h -24)] == 65535, 2, dummy_surrounding_median)
                # print(cp.max(dummy_surrounding_median))
                dummy_surrounding_median = dummy_surrounding_median.astype(cp.uint8)
                # print(cp.max(dummy_surrounding_median))

                save_surrounding_median(data=dummy_surrounding_median.get().astype(np.uint8), year=year, day=day,
                                        block=block,
                                        description=f"这是全国{year}年度{day}天{block}的数据,用时{time.time() - st}")
                print(f"这是全国{year}年度{day}天{block}的数据,用时{time.time() - st}")

                median_values = None
                array1 = None

        array=None
        dummy_surrounding_median = None
        mask = None
        view = None
        data = None
        ntl = None
        print(f"这是全国{year}年度{day}天的数据保存完毕")
        end += time.time() - st
        print("用时：", end)


if __name__ == "__main__":
    values_to_exclude = [65535]
    blocks=construct_blocks()
    # for year in range(2012,2025):
    #     if year not in [2012,2022,2024]:
    for year in range(2015, 2016):
        if year!=2022:
            day_dirs = search_day_dirs(year)
            files = [search_h5_files(path) for path in day_dirs]
            daily_files = dict(zip(day_dirs, files))
            print(daily_files)
            print(daily_files.keys())
            cal_surrounding_median_dummy()
