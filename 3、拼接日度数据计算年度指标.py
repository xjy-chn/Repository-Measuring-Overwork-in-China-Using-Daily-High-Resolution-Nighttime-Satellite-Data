import os
import time

import h5py
import json
import numpy as np
import numpy.ma as ma
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
def scan_all_files():
    for key,value in fps.items():
        block_inten_fp_f=os.listdir(f'./result/daily_overwork/{year}/{key}/intensity')
        block_inten_fp=[f'./result/daily_overwork/{year}/{key}/intensity'+'/'+ fp for fp in block_inten_fp_f]
        block_dummy_fp = [f'./result/daily_overwork/{year}/{key}/dummy' + '/' + fp for fp in block_inten_fp_f]
        value['intensity']=block_inten_fp
        value['dummy']=block_dummy_fp
    print(fps['h25v03']['intensity'])
def read_raw_h5(fp,block):
    if os.path.isfile(fp):
        with h5py.File(fp, 'r') as file:
            # 读取数据集到 NumPy 数组
            dataset = file['data'][block]
            data_array = np.array(dataset)
    else:
        data_array=-np.ones((2400,2400),dtype=np.uint16)
        # 无效值替换为空
        # nan_indices = np.where(data_array == 65535)
        # data_array[nan_indices] = np.nan
    return data_array
def save_annual_overwork(data, year, description, block, type):
    filename = block
    # print(filename)
    if not os.path.exists(f'./result/annual_overwork/{year}/{type}'):
        os.makedirs(f'./result/annual_overwork/{year}/{type}')
    with h5py.File(f'./result/annual_overwork/{year}/{type}' + '/' + filename + '.h5', "w") as f:
        f.create_group('imformation')
        f.create_group('data')
        f['data'].create_dataset(name=block, data=data)
        f['imformation'].create_dataset(name='基本信息', data=description)
if __name__=="__main__":

    #-----------------
    for year in range(2020,2021):
        types=["intensity","dummy"]
        _, holidays, _, works, all = get_days(year)
        values_to_exclude=[65535]

        #-----------------------
        blocks=construct_blocks()
        blocks_fp=sorted(os.listdir(f'./result/daily_overwork/{year}'))
        blocks_fp=sorted([f'./result/daily_overwork/{year}'+'/'+block for  block in blocks_fp])
        # print(blocks)
        # print(blocks_fp)
        # print(len(blocks_fp))
        # print(blocks)
        fps = dict()
        for i in range(len(blocks)):
            fps[blocks[i]]={
                "intensity":[],
                "dummy":[]
            }


        #确定合并范围：暂时只考虑工作日
        print(works)
        days=[]
        for day in works:
            days.append(str(day['dayOfYear']).zfill(3))

        for block, value in fps.items():
            # print(block)
            days_inten_fp = [f'./result/daily_overwork/{year}/{block}/intensity' + '/' + fp + '.h5' for fp in days]
            days_dummy_fp = [f'./result/daily_overwork/{year}/{block}/dummy' + '/' + fp + '.h5' for fp in days]
            fps[block]['intensity']=days_inten_fp
            fps[block]['dummy'] = days_dummy_fp
        # print(fps['h25v03']['intensity'])
        # print(fps['h25v03']['dummy'])
        # print(len(fps['h25v03']['intensity']))
        # print(len(fps['h25v03']['dummy']))
        for block, value in fps.items():
            # print(value)
            st=time.time()
            num = len(value['intensity'])
            # print(num_dummy==num_inten)
            data = -np.ones((num, 2400, 2400), dtype=np.uint16)
            for i in range(num):
                data[i] = read_raw_h5(value['intensity'][i], block)
            mask = np.isin(data, values_to_exclude)
            condition1=data!=65535
            condition2=data>0
            missing = np.count_nonzero(data == 65535, axis=0)
            no_missing=len(works)-missing
            overwork_days=np.count_nonzero(condition1&condition2, axis=0)

            # print(np.mean(no_missing))
            # print(len(works))
            # time.sleep(3)
            intensity=ma.median(ma.array(data, mask=mask), axis=0)
            ratio=overwork_days/no_missing
            ratio=np.round(ratio,decimals=2)
            ratio=(100*ratio).astype(np.uint16)
            ratio=np.where(no_missing==0,65535,ratio)
            # print(ra)
            save_annual_overwork(data=ratio,year=year,
                                 description=f"{year}年{block}快的年度加班天数占比,数值四舍五入后放大了100倍",
                                 block=block,type="ratio")

            # print(np.max(data))

            # # print(intensity.shape)
            # ave_intensity=intensity/overwork_days
            # ave_intensity=np.where(no_missing==0,65535,ave_intensity)
            # print(ave_intensity)
            intensity=np.round(10*intensity)
            intensity=intensity.astype(np.uint32)
            intensity = np.where(no_missing == 0, 65535, intensity)
            save_annual_overwork(data=intensity, year=year,
                                 description=f"{year}年{block}快的年度加班超过节假日灯光强度的中位数,数值四舍五入后放大了100倍",
                                 block=block, type="intensity")
            intensity=None
            ratio=None
            # print(np.mean(intensity))
            # print(np.median(intensity))
            # print(np.min(ratio))
            # print(np.max(ratio))
            print(f"{year}年{block}保存完成")
            print(f"用时{time.time()-st}秒")





#{block:{intensity:[],dummy:[]}
