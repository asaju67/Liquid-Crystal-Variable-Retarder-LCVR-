
"""
Created on Fri June 7

LCR Control code

@author: as37272
"""


#import section
import os
import sys
from ctypes import *
from ctypes.wintypes import *


class D5020(object):
    #Device variables
    usb_pid = c_uint(5020) #Device PID for D5020
    numdevices = c_uint(0)
    devhandle = HANDLE();
    flagsandattrs = c_uint(1073741824)
    devnumber = c_uint(1)
    writepipe = c_uint(1)
    readpipe = c_uint(0)
    bytecount = c_uint(0);

    #command variables
    cmdstr = "" #string of command
    cmdlen = c_uint(0); #command length variable
    usbbuffer = c_byte * 64 #controller response buffer definition
    cmdstatus = usbbuffer() #variable to hold controller response
    bufferlen = c_uint(64) #buffer size variable, set to default size of butter
    cmdresponsestr = "" #Blank command response string variable.
    
    # usbdrvdpath = ""
    mlousb = None
   
        
    def __init__(self):
        #DLL Setup
        usbdrvdpath = os.path.dirname(__file__) + r"\usbdrvd" #Find usbdrvd.dll at path of this example file.
        self.mlousb = WinDLL(usbdrvdpath) #Load the DLL.
        #Set up return and argument defines for DLL Functions
        self.mlousb.USBDRVD_OpenDevice.restype = HANDLE
        self.mlousb.USBDRVD_InterruptWrite.argtypes = [HANDLE, c_uint, POINTER(c_byte), c_uint]
        self.mlousb.USBDRVD_InterruptRead.argtypes = [HANDLE, c_uint, POINTER(c_byte), c_uint]
        self.mlousb.USBDRVD_CloseDevice.argtypes = [HANDLE]
        
        self.findDevices()
        self.setCommand("ver:?")
        self.sendCommand()
        self.readCommand()
        
        # self.setTemp(1,24)
        


    def setCommand(self,cmd):
        self.cmdstr = cmd

    def findDevices(self):
        # Find devices.  This example only talks to the first device found.
        self.numdevices = self.mlousb.USBDRVD_GetDevCount(self.usb_pid)
        if(self.numdevices == 0):
            sys.exit("No Devices Found.")
        devicesfound = "Found "+str(self.numdevices)+" device(s)."
        print(" ") #Print blank line
        print (devicesfound) #then number of devices found
        print(" ") #Print blank line
        #Open Device
        self.devhandle = self.mlousb.USBDRVD_OpenDevice(self.devnumber,self.flagsandattrs,self.usb_pid)


    def sendCommand(self):
        #Prep command to send
        #cmdstr = "inv:1,3000"
        (cmdtosend,self.cmdlen) = self.makecmd(self.cmdstr)
        cmdptr = (c_byte * len(cmdtosend))(*cmdtosend)

        #send command
        self.bytecount = self.mlousb.USBDRVD_InterruptWrite(self.devhandle,self.writepipe,cmdptr,self.cmdlen)
        # print("sent command")
        # print(" ") #Print blank line
        
    def readCommand(self):
        #Read controller's response to command
        self.mlousb.USBDRVD_InterruptRead(self.devhandle,self.readpipe,self.cmdstatus,self.bufferlen)
        self.cmdresponsestr = self.buffer2str(self.cmdstatus) #Convert to string
        print(self.cmdresponsestr) #Print controller's response
        # print("read controller")
        # print(" ") #Print blank line

    def closeDevice(self):
        #Close device.  Device should be opened at the beginning
        #of the program and closed at the end of the program.
        #Closing and reopening in the same program can cause issues.
        self.mlousb.USBDRVD_CloseDevice(self.devhandle)
        print(" ") #Print blank line


    def readWaveform(self,channel):
        self.setCommand("wvf:"+str(channel)+",?<CR>")
        self.sendCommand()
        self.readCommand()
        val = self.cmdresponsestr.split(',')
        return int(val[2])/1000.0


    ###TEMPERATURE###
    #T (ºC) = (i*500/65535) - 273.15
    def readCurrentTemp(self,channel):
        self.setCommand("tmp:"+str(channel)+",?<CR>")
        self.sendCommand()
        self.readCommand()
        val = self.cmdresponsestr.split(',')
       
        temp = int(val[1])*500.0/65535 - 273.15
        
        return temp

    def setTemp(self,channel, temp):
        val = int((temp + 273.15)*65535/500)
        # print(val)
        self.setCommand("tsp:"+str(channel)+","+str(val)+"<CR>")
        self.sendCommand()
        self.readCommand()

    def readSetTemp(self,channel):
        self.setCommand("tsp:"+str(channel)+",?<CR>")
        self.sendCommand()
        self.readCommand()
        val = self.cmdresponsestr.split(',')
        temp = int(val[1])*500.0/65535 - 273.15
        
        return temp



    ###WAVEFORM###
    def setINV(self,channel, vl):
        self.setCommand("inv:"+str(channel)+","+str(vl))
        self.sendCommand()
        # self.readCommand()

    def setSIN(self,channel, v1, v2, period, phase):
        self.setCommand("sin:"+str(channel)+","+str(v1)+","+str(v2)+","+str(period)+","+str(phase))
        self.sendCommand()
        self.readCommand()

    def setSAW(self,channel, v1, v2, period, phase):
        self.setCommand("saw:"+str(channel)+","+str(v1)+","+str(v2)+","+str(period)+","+str(phase))
        self.sendCommand()
        self.readCommand()

    def setTRI(self,channel, v1, v2, period, phase):
        self.setCommand("tri:"+str(channel)+","+str(v1)+","+str(v2)+","+str(period)+","+str(phase))
        self.sendCommand()
        self.readCommand()

    def setSQR(self,channel, v1, v2, period, phase, dc):
        self.setCommand("sqr:"+str(channel)+","+str(v1)+","+str(v2)+","+str(period)+","+str(phase)+","+str(dc))
        self.sendCommand()
        self.readCommand()


    #helper function definitions
    def makecmd (self, cmdstr):
    #This function converts a command string to a byte array and adds the carriage return character to the end.
        cmdlen = len(cmdstr) + 1 #set up length
        cmdarr = c_byte * cmdlen #and command byte array
        cmdtosend = cmdarr()
        chartmp = 0  #temp char variable
        for x in range(cmdlen - 1):#go through command string
            chartmp = ord(cmdstr[x]) #and get current character and convert to byte
            cmdtosend[x] = chartmp #then put it as the current character in the array.
        cmdtosend[cmdlen-1] = 13 #add CR
        return (cmdtosend,cmdlen) #return the command array and length.
    

    

    def buffer2str (self,cmdstatus):
    #This function converts a char array to a string, finishing when it sees a carriage return.
        responsestr = "" #make empty string
        for x in range (64): #Go through response buffer.
            if cmdstatus[x] == 13: #if found carriage return
                break #function is done
            responsestr = responsestr + chr(cmdstatus[x]) #otherwise add current character to string.
        return responsestr #return the response string
    



# if __name__ == "__main__":
#     device = D5020()
    
#     device.setINV(1,3000)
#     device.setTemp(1,24)
    
#     x = input()
    
#     i = 100
    
#     for k in range(1,i):
        
        
#         if(input() =="r"):
#             device.readWaveform(1)
#             device.readCurrentTemp(1)
#         i += 1
        
#         if input() == "STOP":
#             break
        

    
#     # while input() != "STOP" :
#     #     device.readWaveform(1)
#     #     device.readCurrentTemp(1)
        
#     # device.readWaveform(1)
#     # device.readCurrentTemp(1)
    
    
    
    
#     device.closeDevice()





