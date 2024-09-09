import os.path
import time
# import cupy as cp
# import arcpy
import h5py
import numpy as np
import cupy as cp

def create_gdb(project_fp,databasename):
    if not os.path.exists(project_fp+'\\'+databasename+'.gdb'):
        gdb=arcpy.CreateFileGDB_management(project_fp,databasename)
        print(type(gdb))
        print("数据库创建成功")
    else:
        print("数据库在之前已创建")
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
def merge_blocks():
    pass
if __name__=="__main__":
    project_fp = 'F:\popLight\日度灯光分区统计'
    database_name = 'daily_zontal'
    radius=3
    # year=2012
    blocks=construct_blocks()

    #初始化工作路径
    if not os.path.exists(project_fp):
        os.makedirs(project_fp)

    for year in range(2012,2021):
    # #导入企业栅格
        with h5py.File(rf'./年度企业存量栅格/{year}firms_position.h5', 'r') as f:
            firm = np.array(f['data'][str(year)][:])
        if not os.path.exists(f'./result/日度分区统计/deep/企业加权暂存/{radius}x{radius}/{year}'):
            os.makedirs(f'./result/日度分区统计/deep/企业加权暂存/{radius}x{radius}/{year}')
    #拼合日度加班情况
        days = os.listdir(f'./{year}')
        days=[day for day in days if day[-4:]!='.csv']
        print(days)
        with h5py.File(f'./result/daily_overwork/deep/ratio/{year}/{days[0]}.h5', 'r') as f:
            x_axis = f['data']['x'][:]
            y_axis = f['data']['y'][:]
        firm = firm[x_axis, y_axis]
        for day in days:
            with h5py.File(f'./result/daily_overwork/deep/ratio/{year}/{day}.h5','r') as f:
                x_axis=f['data']['x'][:]
                y_axis = f['data']['y'][:]
                dummy= f['data']['dummy'][:]
            dummy2=dummy/firm
            dummy2=100*np.round(dummy2,decimals=2).astype(np.uint8)
            dummy2=np.where(dummy==2,200,dummy2)
            with h5py.File(f'./result/日度分区统计/deep/企业加权暂存/{radius}x{radius}/{year}/{day}.h5 ','w') as f:
                dataset=f.create_group('data')
                f['data'].create_dataset(name=day, data=dummy2,compression="gzip")
                f['data'].create_dataset(name='x', data=x_axis, compression="gzip")
                f['data'].create_dataset(name='y', data=y_axis, compression="gzip")
                f['data'].create_dataset(name='nan',data=200)
        #
        #     with h5py.File(f'./result/日度分区统计/企业加权暂存/{year}/{day}.h5 ', 'r') as f:
        #         dummy2=f['data'][day][:]
        #
        #     arcpy.sa.ZonalStatisticsAsTable(r"F:\日度夜间灯光\原始数据\2019年中国各级行政区划\v84\c市_WGCS1984.shp",
        #                                     "市代码", arcpy.NumPyArrayToRaster(dummy2, arcpy.Point(70, 10),
        #                                                                        x_cell_size=0.004166666666666667,
        #                                                                        y_cell_size=0.004166666666666667,
        #                                                                        value_to_nodata=200),
        #                                     rf"F:\popLight\日度灯光分区统计\daily_zontal.gdb\wfc{year}{day}", "DATA",
        #                                     "ALL", "CURRENT_SLICE", 90, "AUTO_DETECT", "ARITHMETIC", 360)
        #     print(f"第{year}年第{day}天加班分区统计已输出完毕")
        # # time.sleep(1000)
    # arcpy.env.overwriteOutput = False



