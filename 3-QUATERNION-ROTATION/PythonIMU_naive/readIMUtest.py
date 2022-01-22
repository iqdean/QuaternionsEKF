#------------------------------------------------------------------------------
# readIMUtest.py
#
#  test program that uses Class IMUread from readIMUnaive.py to read berryIMU
#  sensors every 1 second
#
# PC                                          RPI3B
# readIMU_naive.py   ------> request -----> reqIMUData.py <--- i2c ---> IMU sensors
# |             \<-------- response <----/       IMU.py                  
# |
# readIMUtest.py --> print sensor data every 1sec
#
#------------------------------------------------------------------------------

import readIMU_naive as imu
import time

if __name__ == '__main__':
    
    s = imu.IMUread()    # instance a IMUread class object

    print('recording data')
    while 1:

        data = s.getIMUdata()
	
	# for debug
        #print(f'type(data): {type(data)}')      # type(data): <class 'tuple'>
        #print(f'len of data TUPLE: {len(data)}')
        
        wx = data[0]
        wy = data[1]
        wz = data[2]
        ax = data[3]
        ay = data[4]
        az = data[5]
        mx = data[6]
        my = data[7]
        mz = data[8]
               
        print('{}'.format('-'*30))
        print('gyro radians: x = {0:3.3f}, y = {1:3.3f}, z = {2:3.3f}'.format(wx,wy,wz))        
        print('accel      g: x = {0:3.3f}, y = {1:3.3f}, z {2:3.3f}'.format(ax,ay,az))
        print('mag    gauss: x = {0:3.3f}, y = {1:3.3f}, z = {2:3.3f}'.format(mx,my,mz))
        print('{}'.format('-'*30))
       
        time.sleep(1)
        
