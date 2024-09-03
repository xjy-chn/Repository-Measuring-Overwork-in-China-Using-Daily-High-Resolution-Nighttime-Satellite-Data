import os.path
import cupy as cp
import pandas as pd
import h5py
import numpy as np
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
def merge_daily_overwork(year,day,radius,blocks):
    national_daily_overwork=2*cp.ones((12000,16800),dtype=cp.uint8)
    for block in blocks:
        if os.path.isfile(f'./result/daily_overwork/{radius}x{radius}_winsor/{year}/{block}/dummy/{day}.h5'):
          with h5py.File(f'./result/daily_overwork/{radius}x{radius}_winsor/{year}/{block}/dummy/{day}.h5','r') as f:
              data =cp.array(f['data'][block][:],dtype=cp.uint8)
          national_daily_overwork[(int(block[4:6])-3)*2400:(int(block[4:6])-2)*2400,
          (int(block[1:3])-25)*2400:(int(block[1:3])-24)*2400]=data
    return national_daily_overwork


def match_Alisted_firm(data,year,day,blocks,radius):
    annual_data=data[data['year']==year]
    annual_data.reset_index(inplace=True,drop=True)
    # print(annual_data)
    xindex=list(annual_data['xindex'])
    yindex=list(annual_data['yindex'])
    overwork=merge_daily_overwork(year, day, radius, blocks)
    print(np.count_nonzero(overwork==2))
    daily_overwok=overwork[xindex,yindex]
    df_overwork=pd.DataFrame(daily_overwok.get(),columns=['overwork'])
    df_overwork['daysOfYear']=df_overwork.apply(lambda x:str(day).zfill(3),axis=1)
    d_overwork=pd.concat([annual_data,df_overwork],axis=1)
    d_overwork.to_excel(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}/{day}.xlsx')
if __name__=="__main__":
    radius=3
    blocks=construct_blocks()
    if not os.path.exists(f'./result/variables/{radius}x{radius}_winsor/上市公司'):
        os.makedirs(f'./result/variables/{radius}x{radius}_winsor/上市公司')
    data = pd.read_excel('./企业办公地经纬度/处理后的企业经纬度.xlsx')
    # print(len(data[data['year']>2020]))
    # 匹配
    # for year in range(2012,2021):
    #     if not os.path.exists(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}'):
    #         os.makedirs(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}')
    #     days = os.listdir(f'./{year}')
    #     days = [day for day in days if day[-4:] != ".csv"]
    #     for day in days:
    #         match_Alisted_firm(data,year,day,blocks,radius=radius)
    #

    # 合并
    for year in range(2012,2021):
        annual=pd.DataFrame()
        files=os.listdir(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}')
        for file in files:
            data=pd.read_excel(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}/{file}')
            annual=pd.concat([annual,data],axis=0)
            print(f'{file}')
        annual.to_csv(f'./result/variables/{radius}x{radius}_winsor/上市公司/{year}日度.csv',index=False)