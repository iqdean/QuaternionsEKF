GOAL1: Quaternion animation using berryIMU
- original code setup from thepoorengineer.com webiste:
    PC <---- serial -----> Ardunion <-- I2C --> IMU Sensors

Convert to:
    PC <---- udp socket---> RPI3B <---- I2C --> IMU Sensors
----------------------------------------------------------------------

Step 0: Convert berryIMUv3 IMU.py + berryIMU.py reference code to use 
        adafruit_bus_device.i2c_device instead of python smbus i2c api

REF: Documents\2022\paragliding\paramotor-avionics\IMU\AHRS\IMU.py
     Documents\2022\paragliding\paramotor-avionics\IMU\AHRS\berryIMU.py

=== tested on RPI3B to confirm convertion from python smbus i2c to 
    adafruit_bus_device.i2c_device works 

Step 1: Read raw sensor data over req/response udp socket instead of serial i/f

1.0) Figure out how send data over udp sockect using python

1) === 1st contact - send raw IMU data from berryIMU using UDP socket ====

REF:
    RPI3B side 
        on PC @  
        Documents\2022\paragliding\paramotor-avionics\IMU\AHRS\sendIMUdata.py
        Documents\2022\paragliding\paramotor-avionics\IMU\AHRS\IMU.py
        on RPI3B @ 
        ~/AHRS/
    PC side
        Documents\2022\SWDEV\python\sockets\listener3.py

=== RPI3b - sendIMUdata.py pushes data to PC listener3.py ===

1.1) RPI3b  
         ~/AHRS/sendIMUdata.py   (currently only sends 3 16bit sensor values)
        - wacked down version of berryIMU.py code that reads raw sensor data
          and transmits over udp socket to listener3.py 

        ~/AHRS/IMU.py
        - modified original IMU.py inline code to
            a) use adafruit_bus_device.i2c_device instead of 
               python smbus api to access i2c_device
            b) converted orig IMU.py into Class IMU w constructor __init(),
               initIMU(), readACC[xyz](), readGYR[xyz](), readMAG[xyz]()
+

1.2) PC	\Documents\2022\SWDEV\python\sockets\listener3.py

1.3) See notes: 
C:\Users\UMG-AE.UMG-AE-HP\Documents\2022\SWDEV\python\sockets\1-sendIMU_listner3-RPI-udp-PC.txt

currently, RPI3B side sendIMU.py is broadcasting 3i of raw sensor data at a periodic rate over udp socket 
and PC side listner3.py is simple listening

need to restructure upd socket coms to be request/response based: 
client requests, server responds:

  Client      udp socket                    Server 
    PC -----> REQUEST Data ---------------> RPI3B <--- i2c---> imu sensors
    PC <----- RESPOND w DATA <------------/

python ints 32bit (4byte)                   raw sensor data 16bit (2byte)          
signed 2s complement #s                     signed 2s complement #
          \<-------------- byte array -----------/               read raw 16bit data from i2c sensor
                                                                 readACCx()  readACCy()   readACCz()
                                                                    |            |          |
rcvMsg=socket.recievefrom(numBytesToRcv)    sendMsg = pack('3i', gyroData[0],gyroData[1], gyroData[2])  
 x,y,z=unpack('3i',rcvdBytes)               socket.sendto(sendMsg, client_address)

On Server side, 
i2c sensor data is read 8bits (acc_l/acc_h) at a time, and fitted into a 16bit word
then its converted into a signed python int BEFORE getting packed into sendMsg byte array for 
tranmission over network socket:

def getGyroData()
    ...
    if acc_combined <= 32767, then return acc_combined else return (acc_combined - 65536)

# 16 bit signed 2's complement #s: Ex: raw sensor data from IMU in counts
# --------------------------------
#  hex   dec
# 7FFF  +32767  +(2^15 - 1)
# ...
# 0001  +1
# 0000  0
# FFFF  -1
# ...
# 8000  -32768  -(2^15)

On the client side, 
the recieved sensor data has to be unpacked based on SAME format (ex: 3i) that was used to pack it. 


1.4) Figure out how make upd socket interface REQUEST/RESPONSE to simulate getSerialData() function
     currently getting used in Quaterion animation 

REF: Documents\2022\SWDEV\python\sockets\bi-dir-udp
Directory of C:\Users\UMG-AE.UMG-AE-HP\Documents\2022\SWDEV\python\sockets\bi-dir-udp

1/09/2022  06:16 PM     639 udp-client.py \__ original code, localhost<->localhost
1/09/2022  06:16 PM     821 udp-server.py /   due to host/port defaults don't work on PC

1/12/2022  07:09 PM     1,129 udp-client1.py \__ req/response 3i, server sims rd of 3 16bit 2s comp #s 
1/11/2022  06:01 PM     4,020 udp-server1.py /   + timer to time req/resp timing @ client

1/12/2022  07:57 PM     2,278 udp-client2.py \__ req/response 9i, server sims rd of 9 16bit 2s comp #s
1/12/2022  08:00 PM     4,258 udp-server2.py /   

- Figure out how to xfer raw sensor data over udp socket using

     PC                          RPI3B
  udp_client2.py ----> Req ---- udp_server2.py <--- simulates reading 16bit 2s complement sensor data
                \<-- Response---/

- Figure out how to convert raw 16bit signed 2's complement data into 
  python integer (32bit signed 2's complement int) using python struct pack/unpack

- Time request/response round trip time of UDP Socket communications

On PC side Quaternion Animation
2) Documents\2022\SWDEV\AHRS-REFS\3-QUATERNION-ROTATION\PythonIMU_naive\readIMU_naive.py

- replace readSensor_naive.py with readIMU_naive.py which will use UDP socket to get 
  raw sensor data from RPI3b  

        =================================================
2.1)=== How to scale raw sensor values into actual units ====
        =================================================

https://thepoorengineer.com/en/quaternion/#gyroRotation
...
One last point though, in the getSerialData method for the python code, 
you will see some random constants as from the extract below.

def getSerialData(self):
    privateData = self.rawData[:]
    for i in range(self.numParams):
        data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
        value,  = struct.unpack(self.dataType, data)
        if i == 0:
            value = ((value * 0.00875) - 0.464874541896) / 180.0 * np.pi
        elif i == 1:
            value = ((value * 0.00875) - 9.04805461852) / 180.0 * np.pi
        elif i == 2:
            value = ((value * 0.00875) + 0.23642053973) / 180.0 * np.pi
        elif i == 3:
            value = (value * 0.061) - 48.9882695319
        elif i == 4:
            value = (value * 0.061) - 58.9882695319
        elif i == 5:
            value = (value * 0.061) - 75.9732905214
        elif i == 6:
            value = value * 0.080
        elif i == 7:
            value = value * 0.080
        elif i == 8:
            value = value * 0.080
        self.data[i] = value
    return self.data

These are actually the sensor bias value which I have determined through collecting the data 
while the sensor is stationary. It will most likely be different with your sensor so be sure 
to calibrate it first before using. If you look carefully at the readSensor_naive.py code, 
there is actually code for you to export the sensor readings to CSV. You can use those to
 get a list of values of sensor output to determine its bias value.

===== Comments ======

Hi Samuel,

The calibration for the gyro and accelerometer is really simple. I just took data 
for a period of time while the sensor is stationary and I took the average of all 
the values to use as the offset.

I suppose you are referring to the constant that “value” is multiplied by. 
The first 3 data comes from the gyro, and if you take a look at the data sheet 
for L3GD20H, you’ll find that there is a [Sensitivity] setting under 
the [Mechanical Characteristics] section. Since I used the 245 degrees per second 
[Measurement Range] (line 26 of the Arduino Code), this corresponds to a sensitivity of
8.75 milli-degrees per second, per digit. This simply means that an increment of
1 in the raw sensor data is equal to an increment of 8.75 milli-degrees.

As such,
1) (value * 0.00875) // convert raw gyro sensor data to units of degrees
2) (value * 0.00875) – 0.464874541896) // correct the sensor bias with an offset
3) ((value * 0.00875) – 0.464874541896) / 180.0 * np.pi // convert units to radians

The calibration of the accelerometer follows the same concept.

Hope this clears thing up.

Cheers!

For berryIMU v3 Hardware:
LSM6DSL - accelerometer & gyro
LIS3MDL - magnetometer

1. From IMU.initIMU() figure out what Full Scale values are getting set:

LSM6DSL
3D accelerometer 
    ±2/±4/±8/±16 g full scale  (units of gravity (g's) on each axis)
    Linear acceleration sensitivity
    FS = ±8 g     0.244 mg/LSB   +/- 32768 * .000244 g = +/- 7.99 g
3D gyroscope
   ±125/±250/±500/±1000/±2000 dps. (Degrees Per Sec on angular rotation) 
   Angular rate sensitivity
   FS = ±2000 dps  70 mdps/LSB   +/- 32768 * .070 dps = +/- 2293 dps

 LIS3MDL
 [1] http://www.pibits.net/code/raspberry-pi-and-lis3mdl-magnetic-field-sensor-example-in-python.php#codesyntax_1
 [2] https://community.st.com/s/question/0D50X00009XkXHf/sensitivity-of-lis3mdl-lsbgauss
 [3] https://aerospace.honeywell.com/content/dam/aerobt/en/documents/learn/products/sensors/application-notes/AN203_Compass_Heading_Using_Magnetometers.pdf

 3D magnetometer sensitivity
  ±4/8/12/16 gauss.    
  FS    LSB/gauss   (FS)*(LSB/gauss)
  8     3421        27368         1g = 3421, 2g = 2*3421, ... 4g = 4x3421 ...8g = 8*3421 = 27368                 
  FS = +-8 gauss    8/27368 = .292 mg/LSB   +/- 27368 * .000292 = +/- 8

  https://en.wikipedia.org/wiki/Earth%27s_magnetic_field#
  The magnitude of Earth's magnetic field at its surface ranges from 25 to 65 μT (0.25 to 0.65 gauss)
  > seems FS +-8 gauss is way too big but external magnetic field could be way stronger than earths

  ----- end how to scale raw sensor data ----

        ==============================================================
2.2) === readIMU_naive.py to replace readSensor_naive.py code complete ===
        ==============================================================

Test readIMU_naive.py:

PC                                          RPI3B
readIMU_naive.py   ------> request -----> sendIMUData.py <--- i2c ---> IMU sensors
 |             \<-------- response <----/       IMU.py                  
 |
readIMUtest.py --> print sensor data every 1sec

plotRawIMUData.py -> collect 1000 sensor readings & plot  
< this should allow use to devise experiment to measure sensor offsets>

https://makersportal.com/blog/2019/11/11/raspberry-pi-python-accelerometer-gyroscope-magnetometer#simple-plots
> no source code except whats shown on in the article
https://learn.adafruit.com/jupyter-on-any-computer-with-circuitpython-libraries-and-mcp2221/accelerometer
> uses jypyter notebook to run the python matplotlib code to do the graphing

TODO1:  sendIMUData.py + IMU.py    wait for req, response read 9i, pack, & send over udp
TODO2:  readIMUtest.py

2.2.1)  readIMU_naive.py - done 
2.2.2)  sendIMUData.py - update to send 9i in order expected by readmIMU_naive.py
2.2.3)  IMU.py - see if any changes needed






  
