"""
Created on Fri June 7 

Template tester

@author: as37272
"""


import sys, time, os
sys.path.append(r'C:/Users/Public/Documents/python_code/nlsim_sona_p38')


import LCVRcontroller as lc
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic



class Form(QDialog):
    
    LCVR = lc.D5020()
   
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        uic.loadUi('LCVRgui.ui', self)
        self.LCVRin.setSingleStep(0.01)
        self.TEMPin.setSingleStep(0.5)
        self.TEMPout.setText(str(self.LCVR.readSetTemp(1)))
        self.LCVRin.valueChanged.connect(self.setLCVR)
        self.TEMPin.valueChanged.connect(self.setTEMP)
        
        self.quitButton.clicked.connect(self.quit)
        self.refreshButton.clicked.connect(self.readTEMP)
        
        
        
    def setLCVR(self):
        self.LCVR.setINV(1,int(self.LCVRin.value()*1000))
        print("set waveform")
        s = self.LCVR.readWaveform(1)
        self.VoltageLCD.display(s)
        print("read waveform")

    def setTEMP(self):
        #T (ºC) = (i*500/65535) - 273.15
        self.LCVR.setTemp(1, float(self.TEMPin.value()))
        print("set temperature")
        self.readTEMP()
        
    def readTEMP(self):
        #T (ºC) = (i*500/65535) - 273.15
        s = self.LCVR.readCurrentTemp(1)
        self.TempLCD.display(s)
        self.TEMPout.setText(str(self.LCVR.readSetTemp(1)))
        print("read temperature")
    
    def quit(self):
        # self.timer.stop()
        self.LCVR.closeDevice()
        self.close()
        
        
if __name__ == "__main__":
    print(sys.argv)
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
