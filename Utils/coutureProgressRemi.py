import sys
from Couture.vendor.qtpy.Qt import QtWidgets
from Couture.vendor.qtpy.Qt import QtCore as qc
from Couture.vendor.qtpy.Qt import QtGui as qg
import time

class Ui_Dialog(object):
   def setupUi(self, Dialog):
       Dialog.setObjectName("Dialog")
       Dialog.resize(400, 133)
       self.progressBar = QtWidgets.QProgressBar(Dialog)
       self.progressBar.setGeometry(qc.QRect(20, 10, 361, 23))
       self.progressBar.setProperty("value", 24)
       self.progressBar.setObjectName("progressBar")
       self.pushButton = QtWidgets.QPushButton(Dialog)
       self.pushButton.setGeometry(qc.QRect(20, 40, 361, 61))
       self.pushButton.setObjectName("pushButton")

       self.worker = Worker()
       self.worker.updateProgress.connect(self.setProgress)

       self.retranslateUi(Dialog)
       qc.QMetaObject.connectSlotsByName(Dialog)

       self.progressBar.minimum = 1
       self.progressBar.maximum = 100

   def retranslateUi(self, Dialog):
       Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, ))
       self.pushButton.setText(QtWidgets.QApplication.translate("Dialog", "PushButton", None, ))
       self.progressBar.setValue(0)
           self.pushButton.clicked.connect(self.worker.start)

   def setProgress(self, progress):
       self.progressBar.setValue(progress)

#Inherit from QThread
class Worker(qc.QThread):

   #This is the signal that will be emitted during the processing.
   #By including int as an argument, it lets the signal know to expect
   #an integer argument when emitting.
   updateProgress = qc.Signal(int)

   #You can do any extra things in this init you need, but for this example
   #nothing else needs to be done expect call the super's init
   def __init__(self):
       qc.QThread.__init__(self)

   #A QThread is run by calling it's start() function, which calls this run()
   #function in it's own "thread".
   def run(self):
       #Notice this is the same thing you were doing in your progress() function
       for i in range(1, 101):
           #Emit the signal so it can be received on the UI side.
           self.updateProgress.emit(i)
           time.sleep(0.1)

def create():
    if __name__ == "__main__":
       import sys

       Dialog = QtWidgets.QDialog()
       ui = Ui_Dialog()
       ui.setupUi(Dialog)
       Dialog.show()