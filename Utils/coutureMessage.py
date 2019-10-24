import sys, os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] +"\\vendor\\qtpy" )
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg

import time
dialog = None



class messageWindow(QtWidgets.QDialog):
    def __init__(self,message,button,button2,coutureCoreFunction):
        """ !@Brief
        Create a generic window that can display a message and can launch another function if needed
        @param message: String, get the message to display
        @param button: String, get the message to display on the closing button
        @param button2: String, get the button name of the optional function
        @param coutureCoreFunction: get the optional function to launch
        """
        QtWidgets.QDialog.__init__(self)
        self.setStyleSheet("background-color: rgb(42, 54, 59)")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Couture help")
        self.setFixedHeight(150)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(30, 15, 30, 15)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)


        self.labelMessage = QtWidgets.QLabel(message)
        self.buttonMessage = QtWidgets.QPushButton(button)
        if button2 != None:
            self.button2Message = QtWidgets.QPushButton(button2)

        self.layout().setSpacing(20)

        self.buttonHLayout = QtWidgets.QHBoxLayout()


        self.layout().addWidget(self.labelMessage)
        self.layout().addLayout(self.buttonHLayout)
        self.buttonHLayout.addWidget(self.buttonMessage,1)
        if button2 != None:
            self.buttonHLayout.addWidget(self.button2Message,1)
            self.button2Message.clicked.connect(partial(coutureCoreFunction,self))

        self.buttonMessage.clicked.connect(partial(self.killWindow))

    def closeEvent(self, event):
        delete()
    def killWindow(self):
        delete()




def create(message,button,button2,coutureCoreFunction):

    global dialog
    if dialog is None:
        dialog = messageWindow(message,button,button2,coutureCoreFunction)
    dialog.show()
    return dialog

def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None



