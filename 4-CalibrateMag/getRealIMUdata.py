#!/usr/bin/env python
#-----------------------------------------------------------
# getRealIMUdata.py 
# - collect 30sec of raw IMU data and store it into csv file
# Replace:
#   csv <- 4-CalibrateMag/getRealData.py <-serial-> Arduino/ExtractSensorData/ExtraceSensorData.ino
# With:
#   csv <- 4-CalibrateMag/getRealIMUdata.py + readIMUraw.py <-udp socket-> AHRS-RPI3B/reqIMUdata.py
# -------------------------------
import readIMUraw as imu
import time
import numpy as np

if __name__ == '__main__':
    
    s = imu.IMUread()    # instance a IMUread class object
    rawData = []

    print('recording data')
    
    for x in range(60):

        data = s.getIMUdata()
        rawData.append(data)

	    # for debug
        #print(f'type(data): {type(data)}')      # type(data): <class 'tuple'>
        #print(f'len of data TUPLE: {len(data)}')
        
        print(f' Unpacked raw Gx: {data[0]}, Gy: {data[1]}, Gz: {data[2]}')
        print(f' Unpacked raw Ax: {data[3]}, Ay: {data[4]}, Az: {data[5]}')
        print(f' Unpacked raw Mx: {data[6]}, My: {data[7]}, Mz: {data[8]}')
        
        time.sleep(1)

    np.savetxt('test.csv',np.array(rawData), delimiter=',', fmt='%i')
 

