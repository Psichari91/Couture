import pymel.core as pm
import sys, os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] +"\\vendor\\qtpy" )
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg

import time
dialog = None



class validationWindow(QtWidgets.QDialog):
    def __init__(self,dictionary,type,coutureCore,returnMessage):
        """
        Create a window that allow user to confirm an action
        @param dictionary: dictionary, Get a dictionnary of meshes
        @param type: String, There is 3 type 'Delete','Apply','Cancel'
        @param coutureCore: Get the current CoutureCore
        @param returnMessage: String, display a message to abord confirmation
        """

        self.type = type
        self.selectedList = []
        self.coutureCore = coutureCore
        self.clothList =[]

        self.dictionary = dictionary
        QtWidgets.QDialog.__init__(self)
        self.setStyleSheet("background-color: rgb(42, 54, 59)")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("%s panel"%type)
        self.setFixedHeight(600)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(30, 15, 30, 15)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.cloth_widget = QtWidgets.QGridLayout()

        bsNode_widget = QtWidgets.QWidget()
        bsNode_widget.setLayout(self.cloth_widget)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setFocusPolicy(qc.Qt.NoFocus)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(bsNode_widget)

        self.layout().setSpacing(20)


        self.returnButton = QtWidgets.QPushButton("%s" %returnMessage)
        if type == "Delete":
            self.actionSelected = QtWidgets.QPushButton("%s selected" % type)
        else:
            self.actionSelected = QtWidgets.QPushButton("%s to selected"%type)
        if type == "Delete":
            self.actionAll = QtWidgets.QPushButton("%s all" % type)
        else:
            self.actionAll = QtWidgets.QPushButton("%s to all" % type)

        self.layout().addWidget(scroll_area)

        buttonWidget = QtWidgets.QWidget()
        buttonWidget.setLayout(QtWidgets.QHBoxLayout())

        buttonWidget.layout().addWidget(self.returnButton)
        buttonWidget.layout().addWidget(self.actionSelected)
        buttonWidget.layout().addWidget(self.actionAll)

        self.layout().addWidget(buttonWidget)
        if type == "Delete":
            self.deleteClothLine()
        else:
            self.editClothLine()

        self.actionSelected.clicked.connect(partial(self.doSelected))
        self.actionAll.clicked.connect(partial(self.doAll))

    def closeEvent(self, event):
        delete()

    def killWindow(self):
        delete()

    def deleteClothLine(self):
        """
        Create a line in the window with a checkbox for each mesh that the user can delete

        """
        for garment in self.dictionary:
            pieceWidget = QtWidgets.QWidget()
            pieceLayout = QtWidgets.QHBoxLayout()
            pieceWidget.setLayout(pieceLayout)

            self.checkBox = QtWidgets.QCheckBox(garment.name())

            pieceLayout.addWidget(self.checkBox)
            self.cloth_widget.addWidget(pieceWidget)

            self.checkBox.stateChanged.connect(partial(self.listSelected, self.checkBox, garment))
            self.clothList.append(garment)
    def editClothLine(self):
        """
        Create a line in the window with a checkbox for each mesh that the user can modify
        """
        for pieceOrig, pieceEdited in self.dictionary.items():

            pieceWidget= QtWidgets.QWidget()
            pieceLayout = QtWidgets.QHBoxLayout()
            pieceWidget.setLayout(pieceLayout)

            self.checkBox = QtWidgets.QCheckBox(pieceOrig.rpartition("|retopoObjectsGRP|")[2])

            pieceLayout.addWidget(self.checkBox)
            self.cloth_widget.addWidget(pieceWidget)


            self.checkBox.stateChanged.connect(partial(self.listSelected,  self.checkBox ,pieceOrig))
            self.clothList.append(pieceOrig)
    def listSelected(self,value,pieceOrig,*args):
        """
        update the selection list each time a checkbox is clicked
        @param value: boolean, Get the value of the checkbox
        @param pieceOrig: String, Name of the cloth piece
        """

        valueCheck = value.isChecked()
        if valueCheck:
            self.selectedList.append(pieceOrig)
        else:
            try:
                self.selectedList.remove(pieceOrig)
            except:
                pass


    def doSelected(self):

        """
        Apply the correct modification to the user selection
        """

        if self.selectedList == []:
            pass
        else :
            if self.type == "Cancel":
                self.coutureCore.cancelEdit(self.selectedList)
                self.killWindow()
            elif self.type == "Apply":
                self.coutureCore.applyEdit(self.selectedList)
                self.killWindow()
            elif self.type == "Delete":
                self.coutureCore.applyDelete(self.selectedList)
                self.killWindow()

    def doAll(self):

        """
        Apply the correct modification to each mesh available
        """

        if self.type != "Delete":
            for pieceOrig, pieceEdited in self.dictionary.items():
                self.selectedList.append(pieceOrig)


        if self.type == "Cancel":
            self.coutureCore.cancelEdit(self.clothList)
            self.killWindow()
        elif self.type == "Apply":
            self.coutureCore.applyEdit(self.selectedList)
            self.killWindow()
        elif self.type == "Delete":
            self.coutureCore.applyDelete(self.dictionary)
            self.killWindow()

def create(dictionary,type,coutureCore,returnMessage,*args):
    global dialog
    if dialog is None:
        dialog = validationWindow(dictionary,type,coutureCore,returnMessage)

    dialog.show()
    return dialog

def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None


