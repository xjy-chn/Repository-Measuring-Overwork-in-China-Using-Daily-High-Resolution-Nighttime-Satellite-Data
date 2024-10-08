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
    festivals, holidays, weekends, works, all= [], [], [], [], []
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
def read_median_h5(fp,block):
    with h5py.File(fp, 'r') as file:
        # 读取数据集到 NumPy 数组
        dataset = file['data'][block]
        data_array = np.array(dataset)
        # 无效值替换为空
        # nan_indices = np.where(data_array == 65535)
        # data_array[nan_indices] = np.nan
    return data_array
def save(data,block,year,description):
    filename=block
    # print(filename)
    if not os.path.exists(f'./result/{year}'):
        os.makedirs(f'./result/{year}')
    with h5py.File(f'./result/{year}'+'/'+filename+'.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block,data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)
def save_overwork(data,block,year,description):
    filename=block
    # print(filename)
    if not os.path.exists(f'./result/{year}'):
        os.makedirs(f'./result/{year}')
    with h5py.File(f'./result/{year}'+'/'+filename+'.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block,data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)
def collect_block_files(year,type,annual_type):
    for block in blocks:
        block_files = []
        for day in type:
            key = str(day['dayOfYear']).zfill(3)
            if f'./{year}/' + key in daily_files.keys():
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
        print(mask[0, 0, 0], array[0, 0, 0])
        # time.sleep(100)
        median_value = ma.median(ma.array(array, mask=mask), axis=0)
        print(median_value.shape)
        description = f"{year}年{key}地区的节假日中位数"
        save(data=median_value, block=key, year=year, description=description)
def merge_annual_holiday_blocks(blocks_fp):
    #将年度节假日中位数区块数据合并
    national_annual_ntl=-np.ones((5 * 2400, 7 * 2400), dtype=np.uint16)
    for fp in blocks_fp:
        block=fp[-9:-3]
        h = int(block[1:3])
        v = int(block[4:6])
        with h5py.File(fp, 'r') as file:
            # 读取数据集到 NumPy 数组
            dataset = file['data'][block]
            data_array = np.array(dataset)
        national_annual_ntl[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data_array
    return national_annual_ntl
if __name__ == "__main__":
    values_to_exclude = [65535]
    # for year in range(2012,2025):
    #     if year not in [2012,2022,2024]:
    year=2012
    day_dirs = search_day_dirs(year)

    files = [search_h5_files(path) for path in day_dirs]
    daily_files = dict(zip(day_dirs, files))
    print(daily_files.keys())

    # print(daily_files)
    # 构造区块
    blocks = sorted(construct_blocks())
    # print(blocks)
    # time.sleep(100)
    _, holidays, _, works, all = get_days(year)
    # print(holidays)
    annual_holidays = dict()
    annual_works = dict()
    # 已经算完的
    annual_holidays=collect_block_files(year,type=holidays,annual_type=annual_holidays)
    cal_median(year,annual_type=annual_holidays)
    # #计算每天和中位数的差值
    # works_num=len(works)
    # annual_works=collect_block_files(year,type=works,annual_type=annual_works)
    # print(annual_works.keys(),daily_files.keys())
    # print(works)
    #
    # median_fp=f"./result/{year}"
    # median_blocks_fp=os.listdir(median_fp)
    # median_blocks_fp=sorted([median_fp+'/'+fp for fp in median_blocks_fp])
    # print(median_blocks_fp)
    # #得到全国年度假期灯光中位数数组
    # national_annual_median_holiday_ntl=merge_annual_holiday_blocks(median_blocks_fp)
    # print(national_annual_median_holiday_ntl)
    # # print(blocks)
    # # print(median_blocks_fp)
    # print(len(works))
    # time.sleep(100)
    # for key, value in works.items():
    #     print(value)
    #     print(key)
    # print(len(works.keys()))
    #
    # for key,value in daily_files.items():
    #     print(value)
    #     print(key)
    #     break
    # print(len(daily_files.keys()))



    #
    #
    # median_files_dict=dict(zip(blocks,median_blocks_fp))
    # # print(median_files_dict)
    # for key,value in annual_works.items():
    #     median=read_median_h5(fp=median_files_dict[key],block=key)
    #     overwork_value=np.zeros((works_num,2400,2400),dtype=np.uint16)
    #     overwork_dummy=np.zeros((works_num,2400,2400),dtype=np.uint16)
    #     for f in range(len(value)):
    #         daily=read_raw_h5(value[f])
    #         daily=np.where(daily==65535,65535*2,daily)
    #         dif=daily-median
    #         condition=dif<0
    #         dummy_variable=np.where(condition,0,dif)
    #         condition2=dummy_variable>0
    #         condition2_2=dummy_variable<65535
    #         condition3 = dummy_variable >= 65535
    #         dummy_variable = np.where(condition2&condition2_2, 1, dummy_variable)
    #         dummy_variable = np.where(condition3, -1, dummy_variable)
    #
    #         dif= np.where(condition3, 65535, dummy_variable)
    #         overwork_value[f]=dif
    #         overwork_dummy[f]=dummy_variable
    #     missing=np.count_nonzero(overwork_dummy==65535,axis=0)
    #     print(overwork_dummy)
    #     print(missing.shape,overwork_dummy.shape)
    #     print(np.max(missing))
    #     #统计加班天数和比例
    #     overwork_day_num=np.count_nonzero(overwork_dummy==1,axis=0)
    #     total_day_num=works_num-missing
    #     overwork_day_ratio=(overwork_day_num/total_day_num)
    #     print(overwork_day_ratio)
    #
    #     #统计超额工作强度
    #     overwork_value=np.where(overwork_value==65535,0,overwork_value)
    #     sum_value=np.sum(overwork_value,axis=0)
    #
    #     time.sleep(100)
