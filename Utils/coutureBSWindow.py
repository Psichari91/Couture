import pymel.core as pm
import sys, os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] +"\\vendor\\qtpy" )
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg

import time
dialog = None



class bsWindow(QtWidgets.QDialog):
    def __init__(self,blendNodeList,folderPath):
        """
        Create a specific window allowing user to use individual blendshapes.
        @param folderPath: String, get the path to couture folder
        @param folderPath: List of blendshapeNodes, get the list of all blendshapes created by Couture
        """
        self.folderPath = folderPath
        self.blendNodeList = blendNodeList
        QtWidgets.QDialog.__init__(self)
        self.setStyleSheet("background-color: rgb(42, 54, 59)")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Blendshape panel")
        self.setFixedHeight(600)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(30, 15, 30, 15)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.bs_widget = QtWidgets.QGridLayout()

        bsNode_widget = QtWidgets.QWidget()
        bsNode_widget.setLayout(self.bs_widget)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setFocusPolicy(qc.Qt.NoFocus)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(bsNode_widget)

        self.layout().setSpacing(20)


        self.killbutton = QtWidgets.QPushButton("Close button")
        self.layout().addWidget(scroll_area)
        self.layout().addWidget(self.killbutton)
        self.blendshapeListProcess()

        self.killbutton.clicked.connect(partial(self.killWindow))

    def closeEvent(self, event):
        delete()

    def killWindow(self):
        delete()

    def blendshapeListProcess(self):
        """
        Create a blendshape slider for each blendshape node
        """

        for node in self.blendNodeList:
            bsNodeName  = node.name()
            bsName = node.listAliases()
            sliderWidget= QtWidgets.QWidget()
            sliderLayout = QtWidgets.QHBoxLayout()
            sliderWidget.setLayout(sliderLayout)

            objectName = node.getTarget()
            objectNameLabel = QtWidgets.QLabel(objectName[0])
            self.textfieldBs = QtWidgets.QLineEdit()
            self.sliderBs = QtWidgets.QSlider(qc.Qt.Horizontal)

            initValue = pm.getAttr("%s.%s" % (node.name(), bsName[0][0]))

            self.sliderBs.setValue(initValue * 100)
            self.sliderBs.setRange(0, 100)
            self.sliderBs.setTickInterval(1)
            sliderStyle = open("%s/Qss/Slider.qss" % self.folderPath).read()
            self.sliderBs.setStyleSheet(sliderStyle)
            self.sliderBs.setFixedWidth(250)

            self.textfieldBs.setText(str(initValue))
            self.textfieldBs.setFixedHeight(40)
            self.textfieldBs.setFixedWidth(40)

            sliderLayout.addWidget(objectNameLabel)
            sliderLayout.addWidget(self.textfieldBs)
            sliderLayout.addWidget(self.sliderBs)
            self.bs_widget.addWidget(sliderWidget)



            self.sliderBs.valueChanged.connect(partial(self.blendshapeCtrl,  self.sliderBs, self.textfieldBs, node,bsName[0][0]))

    def blendshapeCtrl(self,slider,textfield,blendNode,blendshape,*args):
        """
        Control an individual blendshape and update the blendshape UI.
        @param slider: QSlider, get the slider to extract it value
        @param textfield: QLineEdit , get the textflied to output the value of the blendshape
        @param blendNode: String , get the name of the blendshape node
        @param blendshape: String , get the name of the blendshape activated

        """

        value = float(slider.value())

        dividedValue = value / float(100)
        textfield.setText(str(dividedValue))

        pm.setAttr("%s.%s" % (blendNode,blendshape), dividedValue)

def create(blendNodeList,folderPath):
    global dialog
    if dialog is None:
        dialog = bsWindow(blendNodeList,folderPath)
    dialog.show()
    return dialog

def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None


