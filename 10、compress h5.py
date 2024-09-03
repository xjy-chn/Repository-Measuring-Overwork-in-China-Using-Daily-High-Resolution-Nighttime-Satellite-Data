import os
import time

import h5py
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
if __name__=="__main__":
    radius=3
    blocks=construct_blocks()
    for year in range(2012,2021):
        for block in blocks:
            files=os.listdir(fr'F:\日度夜间灯光\原始数据\result\daily_overwork\3x3_winsor\{year}\{block}\dummy')
            raw_files=[fr'F:\日度夜间灯光\原始数据\result\daily_overwork\{radius}x{radius}_winsor\{year}\{block}\dummy'+'\\'+file for file in files]
            c_files=[fr'F:\日度夜间灯光\原始数据\result\daily_overwork\{radius}x{radius}_winsor\compressed\{year}\{block}\dummy'+'\\'+file for file in files]
            if not os.path.exists(fr'F:\日度夜间灯光\原始数据\result\daily_overwork\{radius}x{radius}_winsor\compressed\{year}\{block}\dummy'):
                os.makedirs(fr'F:\日度夜间灯光\原始数据\result\daily_overwork\{radius}x{radius}_winsor\compressed\{year}\{block}\dummy')
            for i in range(len(raw_files)):
                with h5py.File(raw_files[i],'r') as f:
                    data=f['data'][block][:]

                with h5py.File(c_files[i],'w') as f2:
                    f2.create_group('information')
                    f2.create_group('data')
                    f2['data'].create_dataset(name=block,data=data,compression="gzip")
                    f2['information'].create_dataset(name='基本信息', data="这是分块保存的日度加班情况")