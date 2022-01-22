# QuaternionsEKF
PC Side code for Quaternion animation based on IMU Sensor data 

# Block Diagram

```
 Proof of Concept 1:

 3-QUATERNION-ROTATION/PythonIMU_naive          AHRS_RPI3B
     |                                              |
     PC              udp socket over wifi         RPI3B
 readIMU_naive.py---------> request -----> reqIMUData.py <--- i2c ---> IMU sensors
/  Class IMUread \<-------- response <----/       IMU.py               berryIMUv3
|
\
 readIMUtest.py --> print sensor data every 1sec


TO RUN POC1:

1. On RPI3B side - start the server

iqdean@rpi3ubu2004:~/AHRS_RPI3B$ sudo python3 reqIMUdata.py
[sudo] password for iqdean:
Found BerryIMUv3 (LSM6DSL and LIS3MDL)
reqIMUdata Server started on 0.0.0.0:8090

2. On PC Side - start the client

C:\<path_to>\2022\SWDEV\QuaternionsEKF\3-QUATERNION-ROTATION\PythonIMU_naive>python readIMUtest.py
recording data
------------------------------
gyro radians: x = 0.000, y = -0.061, z = 0.011
accel      g: x = -1.007, y = -0.061, z -0.079
mag    gauss: x = -0.937, y = 0.057, z = 0.079
------------------------------
------------------------------
gyro radians: x = -0.013, y = -0.062, z = 0.017
accel      g: x = -1.006, y = -0.060, z -0.079
mag    gauss: x = -0.938, y = 0.055, z = 0.078
------------------------------
...

```


