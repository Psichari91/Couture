import sys, os.path

sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] + "\\vendor\\qtpy")
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg

import pymel.core as pm
import coutureMessage as cm
import Data as data
import coutureShader as cs

reload(cs)

reload(cm)

import time

dialog = None


class manualPairingWindow(QtWidgets.QDialog):
    def __init__(self, folderPath, coutureCore, dataNode):

        """
        Create a specific window allowing user to manually pair meshes if automatic pairing failed
        @param folderPath: String, get the path to couture folder
        @param coutureCore: Get the current CoutureCore
        @param dataNode: CoutureNode,Get the current CoutureNode
        """

        QtWidgets.QDialog.__init__(self)

        self.coutureCore = coutureCore
        self.dataNode = dataNode

        # Those two boolean will be check as final validation before launching the function
        self.lockPair = False
        self.lockRetopo = False

        # Build UI

        self.setStyleSheet("background-color: rgb(42, 54, 59)")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Add a garment")
        self.setFixedHeight(300)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(30, 15, 30, 15)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.gridTemplate = QtWidgets.QGridLayout()

        self.tickNeutralIcon = qg.QPixmap("%s/icons/tickNeutral.png" % folderPath)
        self.tickGreenlIcon = qg.QPixmap("%s/icons/tickGreen.png" % folderPath)
        self.xRedIcon = qg.QPixmap("%s/icons/xRed.png" % folderPath)
        
        manual_widget = QtWidgets.QWidget()
        manual_widget.setLayout(self.gridTemplate)

        firstLine = QtWidgets.QWidget()
        firstLine.setLayout(QtWidgets.QHBoxLayout())
        firstLine.layout().setContentsMargins(0, 0, 0, 0)
        self.gridTemplate.addWidget(firstLine, 0, 0)

        titleGarment = QtWidgets.QLabel("Garment")
        self.qLineGarment = QtWidgets.QLineEdit()
        self.qLineGarment.setPlaceholderText("Select a garment")

        selectGarmentIcon = qg.QPixmap("%s/icons/arrowSelect.png" % folderPath)
        selectGarmentButton = QtWidgets.QPushButton()
        selectGarmentButton.setIcon(selectGarmentIcon)
        selectGarmentButton.setMinimumWidth(50)
        selectGarmentButton.clicked.connect(partial(self.selectPiece, "garment"))

        self.statusGarment = QtWidgets.QLabel()
        self.statusGarment.setAlignment(qc.Qt.AlignCenter)
        self.statusGarment.setPixmap(self.tickNeutralIcon)
        self.statusGarment.setMinimumWidth(50)

        firstLine.layout().addWidget(titleGarment)
        firstLine.layout().addWidget(self.qLineGarment)
        firstLine.layout().addWidget(selectGarmentButton)
        firstLine.layout().addWidget(self.statusGarment)

        secondLine = QtWidgets.QWidget()
        secondLine.setLayout(QtWidgets.QHBoxLayout())
        secondLine.layout().setContentsMargins(0, 0, 0, 0)
        self.gridTemplate.addWidget(secondLine, 1   , 0)

        titlePattern = QtWidgets.QLabel("Pattern")
        self.qLinePattern = QtWidgets.QLineEdit()
        self.qLinePattern.setPlaceholderText("Select a pattern")

        selectPatternIcon = qg.QPixmap("%s/icons/arrowSelect.png" % folderPath)
        selectPatternButton = QtWidgets.QPushButton()
        selectPatternButton.setIcon(selectPatternIcon)
        selectPatternButton.setMinimumWidth(50)
        selectPatternButton.clicked.connect(partial(self.selectPiece, "pattern"))

        self.statusPattern = QtWidgets.QLabel()
        self.statusPattern.setAlignment(qc.Qt.AlignCenter)
        self.statusPattern.setPixmap(self.tickNeutralIcon)
        self.statusPattern.setMinimumWidth(50)

        secondLine.layout().addWidget(titlePattern)
        secondLine.layout().addWidget(self.qLinePattern)
        secondLine.layout().addWidget(selectPatternButton)
        secondLine.layout().addWidget(self.statusPattern)

        thirdLine = QtWidgets.QWidget()
        thirdLine.setLayout(QtWidgets.QHBoxLayout())
        thirdLine.layout().setContentsMargins(0, 0, 0, 0)
        self.gridTemplate.addWidget(thirdLine, 2, 0)

        titleRetopo = QtWidgets.QLabel("Retopo")
        self.qLineRetopo = QtWidgets.QLineEdit()
        self.qLineRetopo.setPlaceholderText("Select a retopo")

        selectRetopoIcon = qg.QPixmap("%s/icons/arrowSelect.png" % folderPath)
        selectRetopoButton = QtWidgets.QPushButton()
        selectRetopoButton.setIcon(selectRetopoIcon)
        selectRetopoButton.setMinimumWidth(50)
        selectRetopoButton.clicked.connect(partial(self.selectPiece, "retopo"))

        self.statusRetopo = QtWidgets.QLabel()
        self.statusRetopo.setAlignment(qc.Qt.AlignCenter)
        self.statusRetopo.setPixmap(self.tickNeutralIcon)
        self.statusRetopo.setMinimumWidth(50)

        thirdLine.layout().addWidget(titleRetopo)
        thirdLine.layout().addWidget(self.qLineRetopo)
        thirdLine.layout().addWidget(selectRetopoButton)
        thirdLine.layout().addWidget(self.statusRetopo)

        addGarmentButton = QtWidgets.QPushButton("Pair meshes")
        addGarmentButton.clicked.connect(partial(self.pairConfirmed))

        resetButton = QtWidgets.QPushButton("Reset window")
        resetButton.clicked.connect(partial(self.resetWindow))

        cancelAddButton = QtWidgets.QPushButton("Cancel")
        cancelAddButton.clicked.connect(partial(self.killWindow))


        self.layout().addWidget(manual_widget)

        buttonWidget = QtWidgets.QWidget()
        buttonWidget.setLayout(QtWidgets.QHBoxLayout())

        buttonWidget.layout().addWidget(addGarmentButton)
        buttonWidget.layout().addWidget(resetButton)
        buttonWidget.layout().addWidget(cancelAddButton)

        self.layout().addWidget(buttonWidget)

    def closeEvent(self, event):
        delete()

    def killWindow(self):
        delete()

    def selectPiece(self, type):

        """ !@Brief
        Use user selection to define a mesh for each step of couture and file the appropriate QLineEdit
        @param type: String, There's four type of selection "garment", "pattern","retopo"
        """

        
        selection = pm.selected(fl=True)
        # run basic safety checks on the user selection
        if selection == []:
            cm.create("Nothing selected",
                      " OK !",
                      None,
                      None)
            return

        if len(selection) > 1:
            cm.create("Too many objects selected",
                      " OK !",
                      None,
                      None)
            return
        # test if selection is a geometry
        testResults = data.testGeo(selection)

        if len(testResults[1]) > 0:
            cm.create("You have selected a non polygonal object",
                      " OK !",
                      None,
                      None)
            return

        else:
            if type == "garment":
                # Check if selected mesh is not a exhisting pattern or retopo
                arr = ['pattern_', 'retopo_']
                if any(c in selection[0].longName()for c in arr):
                    cm.create("You didn't select a garment mesh",
                              " OK !",
                              None,
                              None)
                    return
                if self.lockPair == False:
                    if selection[0].longName() in self.coutureCore.patternDic.keys():
                        # Check if a mesh with the same name is already loaded and paired in Couture
                        if self.coutureCore.patternDic[selection[0].longName()][1] != "" and self.coutureCore.patternDic[selection[0].longName()][1] != "None":
                            cm.create("This garment already have a pattern and a retopo.",
                                      " OK !",
                                      None,
                                      None)
                            return


                        self.statusGarment.setPixmap(self.tickGreenlIcon)
                        self.qLineGarment.setText("%s" % selection[0].longName())
                        self.qLineGarment.setReadOnly(True)

                        self.qLinePattern.setText(self.coutureCore.patternDic[selection[0].longName()][0])
                        self.qLinePattern.setReadOnly(True)
                        self.statusPattern.setPixmap(self.tickGreenlIcon)
                        self.lockPair = True


                    else:
                        cm.create("This garment has not been loaded in the tool previously, use the "+" button",
                                  " OK !",
                                  None,
                                  None)
                        self.statusGarment.setPixmap(self.xRedIcon)
                else:
                    return

            elif type == "pattern":
                print "pattern"
                if self.lockPair == False:
                    if selection[0] in [x for v in self.coutureCore.patternDic.values() for x in v]:
                        # Check if a mesh with the same name is already loaded and paired in Couture
                        print data.longNameEdit("pattern",selection[0].longName(),"pattern","garment")
                        print self.coutureCore.patternDic[data.longNameEdit("pattern",selection[0].longName(),"pattern","garment")]
                        if self.coutureCore.patternDic[data.longNameEdit("pattern",selection[0].longName(),"pattern","garment")][1] != "None":
                            cm.create("This garment already have a pattern and a retopo",
                                      " OK !",
                                      None,
                                      None)
                            return

                        self.qLinePattern.setText("%s" % selection[0].longName())
                        self.qLinePattern.setReadOnly(True)
                        self.statusPattern.setPixmap(self.tickGreenlIcon)


                        self.qLineGarment.setText(data.longNameEdit("pattern",selection[0].longName(),"pattern","garment"))
                        self.qLineGarment.setReadOnly(True)
                        self.statusGarment.setPixmap(self.tickGreenlIcon)
                        self.lockPair = True
                    else:
                        cm.create("This garment has not been loaded in the tool previously, use the " + " button",
                                  " OK !",
                                  None,
                                  None)
                        self.statusPattern.setPixmap(self.xRedIcon)
                else :
                    return
            elif type == "retopo":
                if self.lockRetopo == False:
                    self.qLineRetopo.setText("%s" % selection[0])
                    self.qLineRetopo.setReadOnly(True)
                    self.statusRetopo.setPixmap(self.tickGreenlIcon)
                    self.lockRetopo = True
                else:
                    return
    
    def pairConfirmed(self):

        """ !@Brief
        This function make sure that privious condition "self.lockPair" and "self.lockRetopo" are set to True
        """

        rules = [self.lockPair == True,
                 self.lockRetopo == True]
        if rules:

            self.coutureCore.manualPairMatching([self.qLineGarment.text(),self.qLinePattern.text(),self.qLineRetopo.text()],self)
        else:
            cm.create("You need to select a garment, a pattern and a retopo",
                      " OK !",
                      None,
                      None)

    def resetWindow(self,*args):

        """ !@Brief
        This function reset the window if user want to start over
        """
        self.lockRetopo = False
        self.lockPair = False
        self.qLineGarment.setText("")
        self.qLinePattern.setText("")
        self.qLineRetopo.setText("")
        self.statusGarment.setPixmap(self.tickNeutralIcon)
        self.statusPattern.setPixmap(self.tickNeutralIcon)
        self.statusRetopo.setPixmap(self.tickNeutralIcon)
        self.qLineGarment.setReadOnly(False)
        self.qLinePattern.setReadOnly(False)
        self.qLineRetopo.setReadOnly(False)



def create(folderPath, coutureCore, dataNode):
    global dialog
    if dialog is None:
        dialog = manualPairingWindow(folderPath, coutureCore, dataNode)
    dialog.show()
    return dialog


def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None
