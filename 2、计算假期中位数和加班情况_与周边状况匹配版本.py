import os
import time
import cupy as cp
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


def save_overwork(data, date, year, description, block, type):
    filename = date
    # print(filename)
    if not os.path.exists(f'./result/daily_overwork/{year}/{block}/{type}'):
        os.makedirs(f'./result/daily_overwork/{year}/{block}/{type}')
    with h5py.File(f'./result/daily_overwork/{year}/{block}/{type}' + '/' + filename + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)


def collect_block_files(year, type, annual_type):

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



def merge_annual_holiday_blocks(blocks_fp):
    # 将年度节假日中位数区块数据合并
    national_annual_ntl = -cp.ones((5 * 2400, 7 * 2400), dtype=cp.uint16)
    for fp in blocks_fp:
        block = fp[-9:-3]
        h = int(block[1:3])
        v = int(block[4:6])
        with h5py.File(fp, 'r') as file:
            # 读取数据集到 NumPy 数组
            dataset = file['data'][block]
            data_array = cp.array(dataset)
        national_annual_ntl[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data_array
    return national_annual_ntl


def merge_daily_raw_blocks(blocks_fp: dict):
    # 原始日度区块数据合并
    daily_raw = -cp.ones((5 * 2400, 7 * 2400), dtype=cp.uint16)
    for key, fps in blocks_fp.items():
        for fp in fps:
            block = fp[17:23]
            h = int(block[1:3])
            v = int(block[4:6])
            with h5py.File(key + "/" + fp, 'r') as file:
                # 读取数据集到 NumPy 数组
                dataset = file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL']
                data_array = cp.array(dataset)
            daily_raw[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)] = data_array
    return daily_raw


if __name__ == "__main__":

    values_to_exclude = [65535]
    for year in range(2012,2013):
        day_dirs = search_day_dirs(year)

        files = [search_h5_files(path) for path in day_dirs]
        daily_files = dict(zip(day_dirs, files))
        print(daily_files.keys())
        # 构造区块,提取工作日
        blocks = sorted(construct_blocks())
        _, holidays, _, works, all = get_days(year)
        works_num = len(works)
        days=len(all)
        annual_holidays = dict()
        annual_works = dict()
        # 已经算完的
        # annual_holidays=collect_block_files(year,type=holidays,annual_type=annual_holidays)
        # cal_median(year,annual_type=annual_holidays)
        # 计算每天和中位数的差值
        annual_works = collect_block_files(year, type=works, annual_type=annual_works)
        print(annual_works.keys(), daily_files.keys())

        # 得到全国年度假期灯光中位数数组
        median_fp = f"./result/{year}"
        median_blocks_fp = os.listdir(median_fp)
        median_blocks_fp = sorted([median_fp + '/' + fp for fp in median_blocks_fp])
        national_annual_median_holiday_ntl = merge_annual_holiday_blocks(median_blocks_fp)

        # annual_overwork_intensity=-cp.ones((works_num,5*2400,7*2400),dtype=cp.uint16)
        # annual_overwork_dummy = -cp.ones((works_num, 5 * 2400, 7 * 2400),dtype=cp.uint16)
        print(len(all))
        for i in range(len(all)):
            date = str(all[i]['dayOfYear']).zfill(3)
            print(date)
            key = f'./{year}/{date}'
            if key in daily_files.keys():
                fp = daily_files[key]
                fp = {key: fp}
                print(fp)
                daily_raw = merge_daily_raw_blocks(fp)
                daily_raw=daily_raw.astype(cp.int16)
                # print("原始值最小值：",cp.min(daily_raw))
                # print("原始值最大值：", cp.max(daily_raw))
                national_annual_median_holiday_ntl=national_annual_median_holiday_ntl.astype(cp.int16)
                dif = daily_raw - national_annual_median_holiday_ntl
                dif=cp.where(daily_raw <national_annual_median_holiday_ntl,0,dif)
                # 导入判断是否加班的第二个条件：本栅格亮度是否高于周围八个栅格的中位数
                surrounding_fp = f'./result/surrounding_median/national/{year}/{date}.h5'
                #第三个条件，周围有效栅格数量
                valid_fp=f'./result/surrounding_valid/{year}/{date}.h5'
                with h5py.File(surrounding_fp, 'r') as file:
                    # 读取数据集到 NumPy 数组
                    dataset = file['data'][date]
                    sur_median = cp.array(dataset)
                with h5py.File(valid_fp, 'r') as file:
                    # 读取数据集到 NumPy 数组
                    dataset = file['data'][date]
                    sur_valid = cp.array(dataset)

                # print(sur_median.shape, dif.shape)
                # 缺失值标记

                overwork_intensity = dif * sur_median

                condition1 = overwork_intensity > 0
                condition2 = overwork_intensity != 65535
                overwork_intensity = cp.where(overwork_intensity < 0, 0, overwork_intensity)

                #原始数据缺失的
                overwork_intensity = cp.where(daily_raw == 65535, 65535, overwork_intensity)
                overwork_intensity = cp.where(national_annual_median_holiday_ntl == 65535, 65535, overwork_intensity)
                #周边栅格有效数量大于等于3
                overwork_intensity=cp.where(sur_valid<3,65535,overwork_intensity)
                #周边栅格中位数缺失
                overwork_intensity=cp.where(sur_median==2,65535,overwork_intensity)
                #测试检查
                # c1=sur_median==2
                # c2=overwork_intensity!=65535
                # x,y=cp.where(c1&c2)
                #检查取值范围[0,65535]
                # print("加班强度最小值：",cp.min(overwork_intensity))
                # print("加班强度最大值：", cp.max(overwork_intensity))
                # time.sleep(100)
                # for i in range(len(x)):
                #     print('原始数据：',daily_raw[x[i],y[i]])
                #     print('假期中位数：',national_annual_median_holiday_ntl[x[i],y[i]])
                #     print('周围有效栅格：',sur_valid[x[i], y[i]])
                #     time.sleep(5)
                # print("最小最大值：",cp.count_nonzero(overwork_intensity[x,y]==65535),cp.count_nonzero(overwork_intensity[x,y]==0),
                #       len(x)==cp.count_nonzero(overwork_intensity[x,y]==65535)+cp.count_nonzero(overwork_intensity[x,y]==0))
                # time.sleep(1000)
                overwork_dummy = cp.where(condition1 & condition2, 1, overwork_intensity)
                overwork_dummy=cp.where(overwork_dummy==65535,2,overwork_dummy)
                overwork_dummy=overwork_dummy.astype(cp.uint8)
                # 检查缺失值是否复原
                # print(cp.max(overwork_dummy),cp.min(overwork_dummy))
                # time.sleep(100)
                # 分块存储
                for block in blocks:
                    h = int(block[1:3])
                    v = int(block[4:6])
                    # save_overwork(data=overwork_intensity[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)].get(),
                    #               date=date, year=year, description="这是分块保存的日度加班情况",
                    #               block=block, type="intensity")
                    save_overwork(data=overwork_dummy[2400 * (v - 3):2400 * (v - 2), 2400 * (h - 25):2400 * (h - 24)].get(),
                                  date=date, year=year, description="这是分块保存的日度加班情况",
                                  block=block, type="dummy")
                    print(f"{year}年第{int(date)}日{block}块保存完成")
