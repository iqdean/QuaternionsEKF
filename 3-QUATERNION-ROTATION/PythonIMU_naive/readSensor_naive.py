#!/usr/bin/env python

from threading import Thread
import serial
import time
import struct
import numpy as np
import pandas as pd


class SerialRead:
    def __init__(self, serialPort='/dev/ttyUSB0', serialBaud=38400, dataNumBytes=2, numParams=1):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numParams = numParams
        self.rawData = bytearray(numParams * dataNumBytes)    # 9 x 2 = 18   self.raw = bytearray[18]
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float
        self.data = np.zeros(numParams)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        # self.csvData = []

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
            exit()

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

# dataNumBytes = 2  # number of bytes of 1 data point
# numParams = 9  # number of plots in 1 graph

    def getSerialData(self):
        privateData = self.rawData[:]      # self.rawData[18]
        for i in range(self.numParams):
		
            data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
			#                                                                                             data
			#                 [ 0                   :       2           + 0                   ]   [0:2]   0 1
			#                 [ 1*2                 :       2           + 1*2                 ]   [2:4]   2 3 
			#                 [ 2*2                 :       2           + 2*2                 ]   [4:6]   4 5
			#                 [ 3*2                 :       2           + 3*2                 ]   [6:8]   6 7
			#                 ...
			#                 [ 6*2]                :       2           + 6*2                 ]   [12:14] 12 13
			#                 [ 7*2                 :       2           + 7*2                 ]   [14:16] 14 15
			#                 [ 8*2                 :       2           + 8*2                 ]   [16:18] 16 17
			
# REF: https://stackoverflow.com/questions/4012340/colon-in-python-list-index
# : is the delimiter of the slice syntax to 'slice out' sub-parts in sequences , [start:end]
# [1:5] is equivalent to "from 1 to 5" (5 not included)     <<< NOTE: 5 IS NOT INCLUDED, so only [1][2][3][4]

# REF:https://docs.python.org/3/library/struct.html
#   Format C-type    Python Type    Standard Size 	
#    'h'   short      integer            2        in python, integer is always 4 bytes
#    value (4bytes) = struct.unpack('h', data)    unpacks 2 bytes from data into value
 
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

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True
            #print(self.rawData)

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')