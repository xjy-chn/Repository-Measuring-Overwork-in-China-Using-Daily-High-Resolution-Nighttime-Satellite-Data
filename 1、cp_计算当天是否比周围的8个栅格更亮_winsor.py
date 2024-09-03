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


def save_surrounding_median(data, year, day, block, description, r,bound=True):
    # print(filename)
    if bound:
        if not os.path.exists(f'./result/surrounding_median/{r}x{r}_winsored/{year}/{day}'):
            os.makedirs(f'./result/surrounding_median/{r}x{r}_winsored/{year}/{day}')
        with h5py.File(f'./result/surrounding_median/{r}x{r}_winsored/{year}/{day}' + '/' + block + '.h5', "w") as f:
            f.create_group('imformation')
            f.create_group('data')
            f['data'].create_dataset(name=block, data=data,compression="gzip")
            f['imformation'].create_dataset(name='基本信息', data=description)
            f['imformation'].create_dataset(name='radius', data=r)
    else:
        if not os.path.exists(f'./result/surrounding_median/{r}x{r}/{year}/{day}'):
            os.makedirs(f'./result/surrounding_median/{r}x{r}/{year}/{day}')
        with h5py.File(f'./result/surrounding_median/{r}x{r}/{year}/{day}' + '/' + block + '.h5', "w") as f:
            f.create_group('imformation')
            f.create_group('data')
            f['data'].create_dataset(name=block, data=data,compression="gzip")
            f['imformation'].create_dataset(name='基本信息', data=description)
            f['imformation'].create_dataset(name='radius', data=r)

def cal_surrounding_median_dummy(left, right,r):
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
        c1 = ntl < left
        c2 = ntl > right
        c3 = ntl != 65535
        ntl = cp.where(c1 & c3, 65535, ntl)
        ntl = cp.where(c2 & c3, 65535, ntl)
        padded_ntl = cp.pad(ntl, (((r-1)//2, (r-1)//2), ((r-1)//2, (r-1)//2)), 'constant', constant_values=(65535, 65535))
        print(padded_ntl.strides)
        view = cp.lib.stride_tricks.as_strided(padded_ntl, shape=(12000, 16800, r, r),
                                               strides=((16800+(r-1)) * 2, 2, (16800+(r-1)) * 2, 2))
        padded_ntl = None
        view = view.reshape((12000, 16800, r ** 2))
        # print(view.shape)
        # time.sleep(100)
        # if not os.path.exists("./测试/cp中位数/cpm"):
        #     os.makedirs("./测试/cp中位数/cpm")
        # with h5py.File(f"./测试/cp中位数/cpview2.h5", 'w') as f:
        #     f.create_group('data')
        #     f['data'].create_dataset(name="data", data=view2.get())
        # print("已保存")

        for block in blocks:
            if not os.path.isfile(f'./result/surrounding_median/{year}/{day}' + '/' + block + '.h5'):
                h = int(block[1:3])
                v = int(block[4:6])
                view2 = cp.zeros((2400, 2400, r ** 2 - 1), dtype=cp.uint16)
                # print(view,'vvvvvvvvvvvvvvvvvvvvvvvvvvvvv')
                view2[:, :, 0:(r ** 2 - 1) / 2] = view[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24),
                                                  0:(r ** 2 - 1) / 2]
                view2[:, :, (r ** 2 - 1) / 2:(r ** 2 - 1)] = view[2400 * (v - 3):2400 * (v - 2),
                                                             2400 * (h - 25):2400 * (h - 24), (r ** 2 + 1) / 2:r ** 2]
                # view = None
                array = -cp.ones((2400, 2400, (r ** 2 - 1) * 2), dtype=cp.uint16)
                # time.sleep(100)
                view3 = cp.where(view2 == 65535, 0, view2)
                # print(np.count_nonzero(view3==0))
                array[:, :, 0:(r ** 2 - 1)] = view2
                array[:, :, (r ** 2 - 1):(r ** 2 - 1) * 2] = view3
                view2 = None
                view3 = None
                median_values = cp.median(array, axis=2)
                # median_values.astype(cp.uint32)
                # median_values = median_values + 1
                # median_values = cp.array(median_values, dtype=cp.uint32)

                # median_values = cp.where(median_values == -1, 65535, median_values)
                # median_values = cp.where(median_values == 0, cp.nan, median_values)
                # median_values = median_values - 1
                # print(cp.max(median_values))
                median_values = cp.where(cp.count_nonzero(array == 65535, axis=2) == r ** 2 - 1, 65535, median_values)
                # print(cp.max(median_values))
                # if not os.path.exists("./测试/cp中位数/cpm"):
                #     os.makedirs("./测试/cp中位数/cpm")
                # with h5py.File(f"./测试/cp中位数/cpm/{block}.h5",'w') as f:
                #     f.create_group('data')
                #     f['data'].create_dataset(name=block, data=median_values.get())

                # median_values = cp.where(median_values == cp.nan, 65535, median_values).astype(cp.uint16)
                dummy_surrounding_median = ntl[2400 * (v - 3):2400 * (v - 2),
                                           2400 * (h - 25):2400 * (h - 24)] > median_values
                dummy_surrounding_median = cp.where(median_values == 65535, 2, dummy_surrounding_median)
                dummy_surrounding_median = cp.where(
                    ntl[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] == 65535, 2,
                    dummy_surrounding_median)
                # print(cp.max(dummy_surrounding_median))
                dummy_surrounding_median = dummy_surrounding_median.astype(cp.uint8)
                # print(cp.max(dummy_surrounding_median))

                save_surrounding_median(data=dummy_surrounding_median.get().astype(np.uint8), year=year, day=day,
                                        block=block,
                                        description=f"这是全国{year}年度{day}天{block}的数据,用时{time.time() - st}",
                                        r=r)
                print(f"这是全国{year}年度{day}天{block}的数据,用时{time.time() - st}")

                median_values = None
                array1 = None

        array = None
        dummy_surrounding_median = None
        mask = None
        # view = None
        data = None
        ntl = None
        print(f"这是全国{year}年度{day}天的数据保存完毕")
        end += time.time() - st
        print("用时：", end)


def cal_bound(year):
    with h5py.File(f'./计算正态区间/{year}.h5', 'r') as f:
        mean = cp.array(f['data']['mean'])
        variance = cp.array(f['data']['std'])
        valid = cp.array(f['data']['vaid_grid'])
        sum = cp.nansum(mean * valid)
        total_variance = cp.nansum(variance * valid)
        total_valid = cp.nansum(valid)
        mean = sum / total_valid
        std = (total_variance / total_valid) ** 0.5
        return float(mean - 3 * std), float(mean + 3 * std)


if __name__ == "__main__":
    values_to_exclude = [65535]
    blocks = construct_blocks()
    # for year in range(2012,2025):
    #     if year not in [2012,2022,2024]:
    for year in range(2016, 2021):
        l, r = cal_bound(year)
        left, right = cp.exp(l) - 1, cp.exp(r) - 1
        if year != 2022:
            day_dirs = search_day_dirs(year)
            files = [search_h5_files(path) for path in day_dirs]
            daily_files = dict(zip(day_dirs, files))
            print(daily_files)
            print(daily_files.keys())
            cal_surrounding_median_dummy(left,right,r=3)
