# QuaternionsEKF
PC Side code for Quaternion animation based on IMU Sensor data 

# Block Diagram

```
 Proof of Concept 1:

 3-QUATERNION-ROTATION                          AHRS_RPI3B
     |                                              |
     PC              udp socket over wifi         RPI3B
 readIMU_naive.py---------> request -----> reqIMUData.py <--- i2c ---> IMU sensors
/  Class IMUread \<-------- response <----/       IMU.py               berryIMUv3
|
\
 readIMUtest.py --> print sensor data every 1sec

```


