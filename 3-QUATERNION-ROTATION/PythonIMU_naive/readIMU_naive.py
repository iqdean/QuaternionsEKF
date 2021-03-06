#------------------------------------------------------------------------------
# readIMU_naive.py
#
# class IMUread
#
#  __init__()
#
#      init udp socket connection to RPI3B
#
#  getIMUdata()
#
#     1. Request by sending a byte (any byte) to the server
#     2. Server responds by sending 9 32bit signed integers that have 16bit signed 2's complement
#        raw sensor counts (+/- 32678) packed into the 9 32bit signed integers before transmitting.
#        Packing & Upacking order is: Gyro(X,Y,Z), Accel(X,Y,Z), Mag(X,Y,Z)
#        Ex:
#           gx,gy,gz,ax,ay,az,mx,my,mz = unpack('9i', rcvdBytes)
#           print(f' Unpacked Gx: {gx}, Gy: {gy}, Gz: {gz}')
#           print(f' Unpacked Ax: {ax}, Ay: {ay}, Az: {az}')
#           print(f' Unpacked Mx: {mx}, My: {my}, Mz: {mz}')
#        Note:
#        a) negative values are already sign extended before getting packed for transmission
#        b) 9 32bit rcvd ints that get unpacked represent raw sensor counts (+/- 32768) in a pthon int.
#
#    return gx,gy,gz,ax,ay,az,mx,my,mz
# -----------------------------------------------------------------------------
#  LIS3MDL
# [1] http://www.pibits.net/code/raspberry-pi-and-lis3mdl-magnetic-field-sensor-example-in-python.php#codesyntax_1
# [2] https://community.st.com/s/question/0D50X00009XkXwiSAF/lis3mdl-data-interpretation
# [3] https://aerospace.honeywell.com/content/dam/aerobt/en/documents/learn/products/sensors/application-notes/AN203_Compass_Heading_Using_Magnetometers.pdf
#
#  From [3] 
#  The sensor output is linear:    magnetic_intensity (in gauss) = raw_data / sensitivity
#         raw_count/gauss
#  FS gauss LSB/gauss               (raw_data)/6842 = gauss  
#  ±4       6842        (+-4*6842) = (+-27368)/6842 = 4 gauss
#                     (+-0.5*6842) = (+- 3421)/6842 = 0.5 gauss
#  ±8       3421 
#  ±12      2281
#  ±16      1711
#
#  https://en.wikipedia.org/wiki/Earth%27s_magnetic_field#
#  The magnitude of Earth's magnetic field at its surface ranges from 25 to 65 μT (0.25 to 0.65 gauss)
#  > seems FS +-8 gauss is way too big but external magnetic field could be way stronger than earths
#---------------------------------------------------------------------------

import socket
from struct import pack
from struct import unpack
import array as arr
import time
import numpy as np

class IMUread:

    def __init__(self):
        self.numBytes2Get = 64
        self.destination = ('10.0.0.122', 8090)    # server runs on rpi
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data = arr.array('i',[64])     # 9 32bit ints = 9x4 = 36 , 9 64bit floats: 9x8 = 72

    def getIMUdata(self):
        rqMsg = pack('1i',self.data[0] )
        sentReqBytes = self.sock.sendto(rqMsg, self.destination)    # request  --> rpi3b <--> berryIMU
        rcvdBytes, address  = self.sock.recvfrom(self.numBytes2Get) # response <--/ server
        
        self.data =unpack('9i', rcvdBytes)
	
	# for debug
        #print(f' Unpacked raw Gx: {self.data[0]}, Gy: {self.data[1]}, Gz: {self.data[2]}')
        #print(f' Unpacked raw Ax: {self.data[3]}, Ay: {self.data[4]}, Az: {self.data[5]}')
        #print(f' Unpacked raw Mx: {self.data[6]}, My: {self.data[7]}, Mz: {self.data[8]}')
        # return self.data    # returns a tuple with 9 integer values
        
        # Scale raw sensour counts to convert to proper units Gyro(DPS), Accel(g's), Mag(gauss)
        # NOTE: All Full Scale (FS) sensitivities for BerryIMUv3 are set by IMU.initIMU() on RPI3B side

        # Gyro Angular rate sensitivity
        # FS = +-250 dps 8.75mdps/LSB   +/- 32768 * .00875   = +/-  287 dps
        # FS = ±2000 dps  70 mdps/LSB   +/- 32768 * .070 dps = +/- 2293 dps
        # TBD:                       gyro.(xyz) offsets = 0
        #                                   |
        # value = ((value * 0.00875) - 0.464874541896) / 180.0 * np.pi
        # Note: output units are in RADIANS/sec = (val.dps)/180*PI
        
        gx = (self.data[0] * 0.00875) / 180 * np.pi
        gy = (self.data[1] * 0.00875) / 180 * np.pi
        gz = (self.data[2] * 0.00875) / 180 * np.pi

        # Linear acceleration sensitivity
        # FS = ±4 g     0.061 mg/LSB   +/- 32768 * .000061 g = +/- 1.99 g
        # FS = ±8 g     0.244 mg/LSB   +/- 32768 * .000244 g = +/- 7.99 g
        # TBD:                   accel.(xyz) offsets = 0
        #                               |
        # value = (value * 0.061) - 48.9882695319
        ax = (self.data[3] * 0.000061) 
        ay = (self.data[4] * 0.000061) 
        az = (self.data[5] * 0.000061)

        #  FS gauss LSB/gauss               (raw_data)/6842 = gauss  
        #  ±4       6842        (+-4*6842) = (+-27368)/6842 = 4 gauss
        #                     (+-0.5*6842) = (+- 3421)/6842 = 0.5 gauss
        #                                   1/6842 = 0.000146
        mx = (self.data[6] * .000146)
        my = (self.data[7] * .000146)
        mz = (self.data[8] * .000146)

	# for debug
        #print('gyro radians: x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(gx,gy,gz))
        #print('accel      g: x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(ax,ay,az))
        #print('mag    gauss: x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(mx,my,mz))

        return gx,gy,gz,ax,ay,az,mx,my,mz
    
