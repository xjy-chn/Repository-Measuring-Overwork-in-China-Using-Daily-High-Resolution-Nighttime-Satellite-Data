import h5py
import numpy as np
with h5py.File(r'F:\日度夜间灯光\VNP46A1\VNP46A1.A2024173.h29v06.001.2024176225314.h5','r') as f:
    print(f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['BrightnessTemperature_M12'][:])
    print(f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['BrightnessTemperature_M12'][:].shape)
    print(np.mean(f['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['BrightnessTemperature_M12'][:]))