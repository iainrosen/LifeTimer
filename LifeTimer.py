import betterconfigs
import time
import os
import sys
from PyQt5.QtWidgets import *
from LifeTimerGUI import Ui_MainWindow, QtCore
from datetime import datetime
from math import floor
import threading

def restoreSave():
    try:
        lastSave = betterconfigs.config('.ltconfig')["lastSave"]
        if os.path.exists(lastSave):
            currFile.open(lastSave)
        window.ui.lineEdit.setText(betterconfigs.config('.ltconfig')['lastTask'])
    except:
        openDiag = QFileDialog(window)
        openDiag.setFileMode(QFileDialog.FileMode.ExistingFile)
        openDiag.setNameFilter("LifeTimer Files (*.lt)")
        openDiag.exec()
        openFile(openDiag.selectedFiles())
class savefile:
    def __init__(self):
        self.recTime=0
    def open(self, filename):
        betterconfigs.config('.ltconfig')["lastSave"]=filename
        self.filename=filename
        self.bc=betterconfigs.config(filename)
        self.selfCheck()
        try:
            self.bc.encKey=betterconfigs.config('.ltconfig')["eKey"]
        except:
            self.bc.encryptFile()
            betterconfigs.config('.ltconfig')["eKey"]=self.bc.encKey
        self.bc["lastAccess"]=datetime.now().strftime("%H:%M:%S")
        self.recTime=self.bc["recordTime"]
        betterconfigs.config('.ltconfig')["lastSave"]=filename
        window.ui.label.setText(filename)
        window.ui.label_3.setText(self.bc["lastAccess"])
    def initialize(self, filename):
        self.filename=filename
        self.bc=betterconfigs.config(filename)
        self.bc["lastAccess"]=datetime.now().strftime("%H:%M:%S")
        self.bc["recordTime"]=0
        self.bc.encryptFile()
        betterconfigs.config('.ltconfig')["eKey"]=self.bc.encKey
        window.ui.label.setText(filename)
    def save(self):
        try:
            self.bc["recordTime"]=self.recTime
        except:
            newFile(QFileDialog.getSaveFileName(window, 'New LT'))
    def selfCheck(self):
        while True:
            try:
                self.bc.encKey=betterconfigs.config('.ltconfig')["eKey"]
                break
            except:
                encKeyManual, confirm = QInputDialog.getText(window, "Missing Encryption Key", "I couldn't find the encryption key for your configuration files! If you know it, enter it below:")
                if confirm:
                    try:
                        betterconfigs.config('.ltconfig')["eKey"]=encKeyManual
                        betterconfigs.config('.ltconfig')["lastSave"]
                        break
                    except:
                        pass
                if not confirm:
                    window.closeEvent()
def openFile(filename):
    if len(filename)==0:
        return
    if not os.path.exists(filename[0]):
        print("File Doesn't Exist")
    else:
       currFile.open(filename[0])
       window.updateDisplay()
def newFile(filename):
    filename=filename[0]
    if filename!="":
        if filename[len(filename)-3:len(filename)]!=".lt":
            filename=filename+".lt"
        if os.path.exists(filename):
            currFile.open(filename)
        else:
            currFile.initialize(filename)
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #setup triggers
        self.ui.lcdNumber.display("00:00:00")
        self.ui.actionOpen.triggered.connect(self.openFileDiag)
        self.ui.actionNew.triggered.connect(self.saveFileDiag)
        self.ui.lineEdit.textChanged.connect(self.updateLastTask)
        #timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.incrementTime)
        self.ui.pushButton.clicked.connect(self.start)
        self.ui.pushButton_2.clicked.connect(self.stopSave)
        self.ui.pushButton_3.clicked.connect(self.reset)
        self.ui.actionAdd_Time.triggered.connect(self.addTime)
        self.ui.actionStart.triggered.connect(self.start)
        self.ui.actionStop.triggered.connect(self.stopSave)
        self.ui.actionReset.triggered.connect(self.reset)
        self.ui.actionHard_Reset.triggered.connect(self.hardReset)
        #termination signals
        self.isTerminated=False
    def start(self):
        self.timer.start(1000)
        self.ui.pushButton_3.setText("Reset")
        self.ui.pushButton_2.setFocus()
    def openFileDiag(self):
        openDiag = QFileDialog(self)
        openDiag.setFileMode(QFileDialog.FileMode.ExistingFile)
        openDiag.setNameFilter("LifeTimer Files (*.lt)")
        openDiag.exec()
        openFile(openDiag.selectedFiles())
    def saveFileDiag(self):
        newFile(QFileDialog.getSaveFileName(self, 'New LT'))
    def updateDisplay(self):
        self.displayTime = ""
        self.hours=floor(currFile.recTime/3600)
        self.minutes=floor((currFile.recTime-(self.hours*3600))/60)
        self.seconds=floor((currFile.recTime-(self.minutes*60)-(self.hours*3600)))
        if len(str(self.hours))==1:
            self.hours="0"+str(self.hours)
        if len(str(self.minutes))==1:
            self.minutes="0"+str(self.minutes)
        if len(str(self.seconds))==1:
            self.seconds="0"+str(self.seconds)
        self.displayTime=str(self.hours)+":"+str(self.minutes)+":"+str(self.seconds)
        self.ui.lcdNumber.display(self.displayTime)
    def incrementTime(self):
        currFile.recTime=currFile.recTime+1
    def stopSave(self):
        self.ui.pushButton.setFocus()
        self.timer.stop()
        currFile.save()
        self.ui.pushButton_3.setText("Reset")
    def reset(self):
        self.ui.pushButton.setFocus()
        self.timer.stop()
        currFile.recTime=currFile.bc["recordTime"]
        currFile.save()
    def hardReset(self):
        self.ui.pushButton.setFocus()
        self.timer.stop()
        currFile.recTime=0
        currFile.save()
    def closeEvent(self, *args, **kwargs):
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        self.stopSave()
        self.isTerminated=True
    def addTime(self):
        timeToAdd, confirm = QInputDialog.getInt(self, "Add Time", "Enter the number of minutes to add")
        if confirm:
            currFile.recTime=currFile.recTime+(timeToAdd*60)
    def updateLastTask(self):
        try:
            betterconfigs.config('.ltconfig')['lastTask']=self.ui.lineEdit.text()
        except:
            pass
def thread_refresh():
    while window.isTerminated==False:
        window.updateDisplay()
        time.sleep(0.01)
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    currFile = savefile()
    restoreSave()
    window.updateDisplay()
    window.show()
    tRefresh = threading.Thread(target=thread_refresh)
    tRefresh.start()
    sys.exit(app.exec_())