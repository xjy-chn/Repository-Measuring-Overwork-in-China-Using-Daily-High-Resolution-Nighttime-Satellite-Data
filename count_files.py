import os
for i in range(2012,2025,1):
    files=os.listdir(f'./{i}')
    print(files)
    files=[f'./{i}'+'/'+file for file in files]
    print(files)
    files=[file for file in files if os.path.isdir(file)]
    for file in files:
        if len(os.listdir(file))!=30:
           with open('天数不等于30天.txt','a',encoding='utf-8') as f:
               f.write(file+'\n')