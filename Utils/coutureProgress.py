import sys, os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] +"\\vendor\\qtpy" )
print sys.path
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg
import time
dialog = None



class progressWindow(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Work in progress")
        self.setFixedHeight(200)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(30, 80, 30, 5)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setGeometry(180, 80, 250, 20)
        self.labelProgress = QtWidgets.QLabel("Progress...")

        self.layout().addWidget(self.progressBar)
        self.layout().addWidget(self.labelProgress)

        self.worker = Worker()
        self.worker.updateProgress.connect(self.setProgress)

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
    global dialog
    if dialog is None:
        dialog = progressWindow()
    dialog.show()
    return dialog

def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None


