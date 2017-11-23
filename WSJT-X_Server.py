#!/usr/share/python3

import sys, struct, socket, time
from PyQt4 import QtCore, QtGui, uic

import WSJTXClass

UDP_IP = "192.168.1.255"
UDP_PORT = 2237
qtCreatorFile = "WSJTX_Server.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):        # added parent = None for examplle
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.startThread()        

    def closeEvent(self, event):
        # here you can terminate your threads and do other stuff
        print("In quit...  CloseEvent")
        self.workThread.setStop()
        self.workThread.quit()
        self.workThread.sock.close()    # have to clsoe the socket.
        # and afterwards call the closeEvent of the super-class
        super(QtGui.QMainWindow, self).closeEvent(event)

        
    def add(self, text):
        self.listWidgetBandActivity.addItem(text)
        self.listWidgetBandActivity.scrollToBottom()
        self.labelBandActivity.setText("Band Activity {}".format(self.listWidgetBandActivity.count()))
        # Let's do some statistics!
        
    def startThread(self):
        self.workThread = WorkThread()
        self.connect(self.workThread, QtCore.SIGNAL("update(QString)"), self.add)
        self.workThread.uiHeartbeatMsg.connect(self.HandleHeartbeatMsg)
        self.workThread.uiStatusMsg.connect(self.HandleStatusMsg)
        self.workThread.uiDecodeMsg.connect(self.HandleDecodeMsg)
        self.workThread.uiEraseMsg.connect(self.HandleEraseMsg)
        self.workThread.uiLoggedMsg.connect(self.HandleLoggedMsg)
        self.workThread.start()

    def HandleHeartbeatMsg(self, WSJTX_Heartbeat):
        print("Got a Heartbeat message!")

    def HandleStatusMsg(self, WSJTX_Status):
        print("Got a Status message!")
        
    def HandleDecodeMsg(self, WSJTX_Decode):
        print("Got a Decode message!")

    def HandleEraseMsg(self):        
        print("Got a Decode message!")


# This kind of sucks but I expected somethingto be fucked up.
# You get a log message when you log a QSO.  Unfortunatly, it pops
# up a dialog box that required an OK... no method to tell WSJY-X
# to log a QSO without the dialog automatically.  Then the remote
# would get the logged message and full automation could be achieved.
#
# So if the server is in control of making the contacts, we have to
# watch the messages and when we get the 73 log the contact!  I need
# to look at the WSJT-X source to see if the other log files are
# written to or not.  The ADIF is not unless you OK the dialog.
#
# If alling CQ:
# Looking for these responses
#
# <mycall> <dxcall> <grid>
# <mycall> <dxcall> <report>
# <mycall> <dxcall> 73
#
# This is a completed QSO!  Log the QSO on the remote system!
# WSJT-X will not log this in it's ADIF file.  Also the
# prompt to log QSO must not be checked or the LogQSO
# dialog will pop up!
#
# Answering a CQ is:

    def HandleLoggedMsg(self, WSJTX_Logged):        
        print("Got a Logged message!")

class WorkThread(QtCore.QThread):
    uiHeartbeatMsg = QtCore.pyqtSignal(WSJTXClass.WSJTX_Heartbeat)
    uiStatusMsg = QtCore.pyqtSignal(WSJTXClass.WSJTX_Status)
    uiDecodeMsg = QtCore.pyqtSignal(WSJTXClass.WSJTX_Decode)
    uiEraseMsg = QtCore.pyqtSignal()
    uiLoggedMsg = QtCore.pyqtSignal(WSJTXClass.WSJTX_Logged)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.decodeCount = 0
        self.Stop = False
        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.sock.bind((UDP_IP, UDP_PORT))
        self.DecodeCount = 0
                              
    def run(self):
        try:
            while True:
                if not self.Stop:
                    fileContent, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
                    NewPacket = WSJTXClass.WSJTX_Packet(fileContent, 0)
                    NewPacket.Decode()

                    if NewPacket.PacketType == 0:
                        HeartbeatPacket = WSJTXClass.WSJTX_Heartbeat(fileContent, NewPacket.index)
                        HeartbeatPacket.Decode()
                        self.uiHeartbeatMsg.emit(HeartbeatPacket)

                    elif NewPacket.PacketType == 1:
                        StatusPacket = WSJTXClass.WSJTX_Status(fileContent, NewPacket.index)
                        StatusPacket.Decode()
                        self.uiStatusMsg.emit(StatusPacket)
                        
                    elif NewPacket.PacketType == 2:
                        DecodePacket = WSJTXClass.WSJTX_Decode(fileContent, NewPacket.index)
                        DecodePacket.Decode()
                        # can use PyQt4.QtCore.QTime for this as well!
                        s = int(  (DecodePacket.Time/1000) % 60 )
                        m = int( ((DecodePacket.Time/(1000*60) ) %60 ) )
                        h = int( ((DecodePacket.Time/(1000*60*60)) %24))
                        dataDecode = ("{:02}:{:02}:{:02} {:>3} {:4.1f} {:>4} {} {}".format(h,m,s,DecodePacket.snr,DecodePacket.DeltaTime,DecodePacket.DeltaFrequency,DecodePacket.Mode,DecodePacket.Message)) 
                        self.emit(QtCore.SIGNAL('update(QString)'), dataDecode)
                        self.DecodeCount += 1
                        # now we need to send it to the UI

                    elif NewPacket.PacketType == 3:
                        self.uiEraseMsg.emit()

                    elif NewPacket.PacketType == 5:
                        LoggedPacket = WSJTXClass.WSJTX_Logged(fileContent, NewPacket.index)
                        LoggedPacket.Decode()
                        self.uiLoggedMsg.emit(LoggedPacket)    
                    
                        
        finally:
            self.sock.close()

    def setStop(self):
        self.Stop = True


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
    
