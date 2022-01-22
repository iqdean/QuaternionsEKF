
# PC                                          RPI3B
# readIMU_naive.py   ------> request -----> reqIMUData.py <--- i2c ---> IMU sensors
# |             \<-------- response <----/       IMU.py                  
# |
# readIMUtest.py --> print sensor data every 1sec
# udp-client2.py updated to use readIMU_naive.py Class IMUread.getIMUdata() to read raw sensor

import readIMU_naive as imu
import time

if __name__ == '__main__':
    
    s = imu.IMUread()    # instance a IMUread class object

    print('recording data')
    while 1:
        print('readIMUtest.py {}'.format('-'*30))
        #ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
        #mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
        # wx,wy,wz,ax,ay,az,mx,my,mz = s.getIMUdata()
        data = s.getIMUdata()

        print(f'type(data): {type(data)}')      # type(data): <class 'tuple'>
        print(f'len of data TUPLE: {len(data)}')

        print(f' Unpacked Gx: {data[0]}, Gy: {data[1]}, Gz: {data[2]}')
        print(f' Unpacked Ax: {data[3]}, Ay: {data[4]}, Az: {data[5]}')
        print(f' Unpacked Mx: {data[6]}, My: {data[7]}, Mz: {data[8]}') 
            
        '''
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
        
        #print('accel raw: x = {0:2.2f}, y = {1:2.2f}, z {2:2.2f}= '.format(ax,ay,az))
        #print('gyro raw: x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(wx,wy,wz))
        #print('mag raw: x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(mx,my,mz))
        
        print(f' Unpacked Gx: {wx}, Gy: {wy}, Gz: {wz}')
        print(f' Unpacked Ax: {ax}, Ay: {ay}, Az: {az}')
        print(f' Unpacked Mx: {mx}, My: {my}, Mz: {mz}')
        print('{}'.format('-'*30))
        '''
        
        time.sleep(1)
        
