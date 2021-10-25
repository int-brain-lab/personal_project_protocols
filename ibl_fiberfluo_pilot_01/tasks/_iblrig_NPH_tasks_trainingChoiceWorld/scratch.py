import pandas as pd
import scipy as sp
f = 'C:\\iblrig_data\\Subjects\\_iblrig_calibration\\2018-12-04\\4\\raw_behavior_data\\_iblrig_calibration_water_function.csv'

df1 = pd.read_csv(f)

time2vol = sp.interpolate.pchip(df1["open_time"], df1["weight_perdrop"])                           
x=0
while np.round(time2vol(x), 3) < 3:
    x+=1