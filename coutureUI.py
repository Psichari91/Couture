
"""

DOCUMENTATION

   Couture is a simple tool that eases the retology workflow for clothes.
   Import a piece of garment from scanned data, high poly model or marvelous designer.
   Garments must have uv unwrapped in order to process the workflow.
   Iterate quickly between 2D and 3D space.

   ### FEATURES ###

   - Outliner: Couture has a custom outliner that will make your work easier when you are looking for a specific piece of garment
   - Goz support: Thanks to zRemesher it's possible get a good base topo in few clicks. Couture allows you to quickly move from one software to another. Make sure that GOZ is already installed
   - CoutureNode: Couture creates a hidden node in your Dagobject outliner, this node will save every data needed by Couture, allowing the user to open a previous scene and restart his work instantly.
   However, if the user wants to start over in the same maya scene, this node must be deleted and the tool must be reloaded
   - Couture blendshapes: Couture automatically creates a blendshape between a pair of 2D and 3D piece of cloth. You can activate all blendshape at once or individually.
   - Couture wrap: Couture automatically creates a wrap between a pair of triangulated mesh and a retopologized one.
   - Couture edit: You can edit your geo in 3D or 2D space, this feature allows you to have a safety net in case you're not happy with your modifications.

   ### INSTALL ###

   Copy Couture's folder in your directory : C:\Users\UserName\Documents\maya\20XX-x64\scripts
   Use this code to launch Couture:

       import Couture.coutureUI as cUI
       reload(cUI)
       cUI.coutureInterface(dock=True)


   You can create a macro out of it, a custom shelf is also provided in the folder "Shelf"

   For more details, visit https://www.artstation.com/psichari/blog/z9b1/coutures-wiki

SPECIAL THANKS

   Remi Deletrain for his constant support and advices. Especially the Maya API side of Couture !
   My colleagues at EISKO,Cedric Guiard ,Gilles Gambier ,Pierre Lelievre And Romain Lopez  for their help on many different code related topics.
   Thanks to the people who were part of the Beta for their feedback.
   For all the comments, like and share from the community on the social medias, that was quite unexpected ! :)
   Big thanks to the people who created Qt.py https://github.com/mottosso/Qt.py
   Thanks to Ryan Roberts for his Wrap Deformer script


LICENSE

   See end of file for license information :  MIT License

"""


from Utils import Data as data
from functools import partial
import coutureCore as cc
reload(cc)

from maya import OpenMayaUI as omui
import pymel.core as pm
import os

folderPath = os.path.split(__file__)[0]

dialog = None

if not pm.objExists('CoutureDataNode'):
    dataNode = data.coutureDataNode()
else :
    dataNode = data.coutureDataNode("CoutureDataNode")


from vendor.qtpy import Qt
from vendor.qtpy.Qt import QtWidgets
from vendor.qtpy.Qt import QtGui as qg
from vendor.qtpy.Qt import QtCore as qc


import logging
logging.basicConfig()
logger = logging.getLogger('CoutureUI')
logger.setLevel(logging.DEBUG)

#Defining Maya API version
MAYA2014 = 20140000
MAYA2015 = 20150000
MAYA2016 = 20160000
MAYA2016_5 = 20165000
MAYA2017 = 20170000
MAYA2018 = 20180000

# Couture looks of the Qt binding is the most appropriate
if Qt.__binding__ == 'PySide':
    from shiboken import wrapInstance
    from vendor.qtpy.Qt.QtCore import Signal
    logger.debug("Pyside with shiboken")

elif Qt.__binding__.startswith("PyQt"):
    from sip import wrapinstance as wrapInstance
    from vendor.qtpy.Qt.QtCore import pyqtSignal as Signal
    logger.debug("PyQt with Sip")

else:
    from shiboken2 import wrapInstance
    from vendor.qtpy.Qt.QtCore import Signal
    logger.debug("Pyside2 with shiboken")


def maya_api_version():
    """
    return the current API version of maya

    """
    return int(str(pm.about(api=True))+"00" )

def getMayaMainWindow(size = True):
    """
    Get the Qt main window from Maya
    @return ptr :QtWidgets.QMainWindow: The Maya MainWindow
    """
    # We use the OpenMayaUI API to get a reference to Maya's MainWindow
    win = omui.MQtUtil_mainWindow()

    # Then we can use the wrapInstance method to convert it to something python can understand
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)

    if size:
        return [ptr.width(),ptr.height()]
    return ptr

def getDock(name = 'CoutureDock' ):
    """
    Get the ptr to a dockable location for Couture
    @param name: str, name of the Couture dockable window
    @return ptr: ptr the dock windows newly created
    """

    deleteDock(name)

    if maya_api_version() < MAYA2017:
        ctrl = pm.dockControl(name, area='right', content='Couture', allowedArea='all',label="Couture tool",vis=True,r=True)
        print "do ctrl"

        # And then we return the control name
        return ctrl

    else:
        # ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Couture tool")
        ctrl = pm.workspaceControl(name, dockToMainWindow=('right',1),label = "Couture tool",loadImmediately =True,vis=True,r=True )
        qtCtrl = omui.MQtUtil_findControl(ctrl)
        ptr = wrapInstance(long(qtCtrl),QtWidgets.QWidget)

        return ptr

def deleteDock (name = 'CoutureDock' ):
    """
    Delete an already existing Couture dockable windows
    @param name: str, name of the Couture dockable window
    """
    if maya_api_version() < MAYA2017:
        if pm.dockControl(name, query=True, exists=True):
            # If it does we delete it
            pm.deleteUI(name)
    else:
        if pm.workspaceControl(name,query = True,exists = True):
            pm.deleteUI(name)

class coutureInterface(QtWidgets.QWidget):
    """
    This class will build the interface
    """

    def  __init__(self, dock=True):
        """
        This function build the window
        """

        # there is two ways to manage dockable windows depending of the version of Maya is older than Maya 2017
        if maya_api_version() < MAYA2017:

            # First lets delete a dock if we have one so that we aren't creating more than we need
            deleteDock()

            try:
                pm.deleteUI('Couture')
            except:
                logger.debug('No previous UI exists')

            parent = QtWidgets.QDialog(parent=getMayaMainWindow(size=False))
            # We set its name so that we can find and delete it later

            parent.setObjectName('Couture')
            # Then we set the title
            parent.setWindowTitle('Couture tool')

            # Finally we give it a layout
            dlgLayout = QtWidgets.QVBoxLayout(parent)


            super(coutureInterface, self).__init__(parent=parent)

            # We call our buildUI method to construct our UI
            self.buildUI()


            self.parent().layout().addWidget(self)
            # Finally if we're not docked, then we show our parent
            parent.show()

            # <=Maya2016: For Maya 2016 and below we need to create the dock after we create our widget's parent window
            if dock:
                getDock()

        else:

            try:
                pm.deleteUI('Couture')
            except:
                logger.debug('No previous UI exists')


            if dock:
                parent = getDock()
            else:
                deleteDock()

                parent = QtWidgets.QDialog(parent=getMayaMainWindow(size=False))
                # We set its name so that we can find and delete it later
                parent.setObjectName('Couture')
                # Then we set the title
                parent.setWindowTitle('Couture tool')

                # Finally we give it a layout
                dlgLayout = QtWidgets.QVBoxLayout(parent)

            super(coutureInterface, self).__init__(parent=parent)

            self.buildUI()
    
            self.parent().layout().addWidget(self)
    
            parent.setStyleSheet("background-color: rgb(103, 138, 152)")

    
    
            if not dock:
                parent.show()


    def buildUI(self):


        baseLayout = QtWidgets.QVBoxLayout(self)

        self.setMinimumWidth(getMayaMainWindow(size = True)[0]*0.185)

        self.setMinimumHeight(getMayaMainWindow(size = True)[1]*0.65)

        self.setStyleSheet("background-color: rgb(103, 138, 152)")

        ### Create a scroll Area for the tool, maintain the size of the UI on various screen resolutions
        scrollMasterWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(scrollMasterWidget)
        layout.setContentsMargins(0,15,0,0)



        scrollMasterArea = QtWidgets.QScrollArea()
        scrollMasterArea.setFocusPolicy(qc.Qt.NoFocus)
        scrollMasterArea.setWidgetResizable(True)
        scrollMasterArea.setWidget(scrollMasterWidget)


        baseLayout.addWidget(scrollMasterArea)
        # __________________________________________  Logo Widget _____________________________________________________#

        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setAlignment(qc.Qt.AlignCenter)
        self.logo_pix = qg.QPixmap("%s/icons/coutureLogo.png" % folderPath)
        self.logo_label.setPixmap(self.logo_pix)

        layout.addWidget(self.logo_label)

        # _________________________________________ Outliner Widget ___________________________________________________#
        self.QframeHolder = QtWidgets.QFrame()
        self.QframeHolder.setStyleSheet("background-color: rgb(52 ,81, 97)")
        self.QframeHolder.setLayout(QtWidgets.QHBoxLayout())
        self.QframeHolder.layout().setContentsMargins(0,15,0,15)

        self.outliner_mainWidget = QtWidgets.QWidget()
        self.outliner_mainWidget.setStyleSheet("background-color: rgb(52 ,81, 97)")
        self.outliner_mainWidget.setLayout(QtWidgets.QGridLayout())

        self.QframeHolder.layout().addWidget(self.outliner_mainWidget)

        layout.addWidget(self.QframeHolder)

        # #### Title ####

        self.outlinerTitle = QtWidgets.QLabel("Outliner")
        self.outlinerTitle.setStyleSheet("color : rgb(240, 240, 240);font: bold 25px;")
        self.outlinerTitle.setAlignment(qc.Qt.AlignCenter)
        self.outliner_mainWidget.layout().addWidget(self.outlinerTitle,0,1,1,12)

        #### Scroll area ####

        scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()

        scrollArea.setFocusPolicy(qc.Qt.NoFocus)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)

        scrollArea.setStyleSheet("background-color: rgb(42, 54, 59)")
        scrollArea.setMinimumHeight(250)
        scrollArea.setMaximumHeight(350)
        scrollArea.setMinimumWidth((getMayaMainWindow(size = True)[0]*0.175))
        self.outliner_mainWidget.layout().addWidget(scrollArea, 1, 1, 1, 12)


        self.secondLine = QtWidgets.QWidget()
        self.secondLine.setLayout(QtWidgets.QHBoxLayout())
        self.secondLine.layout().setContentsMargins(0, 0, 0, 0)
        self.outliner_mainWidget.layout().addWidget(self.secondLine, 2,1, 1,12)

        self.iconDelete = qg.QPixmap("%s/icons/trash.png" % folderPath)
        self.buttonDelete = QtWidgets.QPushButton()
        self.buttonDelete.setIcon(self.iconDelete)
        self.buttonDelete.setMaximumWidth(50)

        self.iconAdd = qg.QPixmap("%s/icons/add.png" % folderPath)
        self.buttonAdd = QtWidgets.QPushButton()
        self.buttonAdd.setIcon(self.iconAdd)
        self.buttonAdd.setMaximumWidth(50)

        self.uvLayoutButton = QtWidgets.QPushButton("UV layout selected")
        self.uvLayoutButton.setStyleSheet("color: rgb(240,240,240);font: bold 18px;")
        self.loadGarmentButton= QtWidgets.QPushButton("Load garments")
        self.loadGarmentButton.setStyleSheet("color: rgb(240,240,240);font: bold 18px;")

        self.secondLine.layout().addWidget(self.uvLayoutButton)
        self.secondLine.layout().addWidget(self.loadGarmentButton)
        self.secondLine.layout().addWidget(self.buttonDelete)
        self.secondLine.layout().addWidget(self.buttonAdd)

        #
        #________________________________Garment________________________________#
        self.garmentLabel = QtWidgets.QLabel("Garments")
        self.garmentLabel.setStyleSheet("color: rgb(240, 240, 240)")
        self.garmentLabel.setAlignment(qc.Qt.AlignCenter)

        self.displayIcon = qg.QPixmap("%s/icons/eyeOn.png" % folderPath)
        self.garmentDisplayButton = QtWidgets.QPushButton()
        self.garmentDisplayButton.setIcon(self.displayIcon)
        self.garmentDisplayButton.setMaximumWidth(30)

        self.lockIcon = qg.QPixmap("%s/icons/lockOff.png" % folderPath)
        self.garmentLockButton = QtWidgets.QPushButton()
        self.garmentLockButton.setIcon(self.lockIcon)
        self.garmentLockButton.setMaximumWidth(30)

        self.selectIcon = qg.QPixmap("%s/icons/selectAll.png" % folderPath)
        self.garmentSelectButton = QtWidgets.QPushButton()
        self.garmentSelectButton.setIcon(self.selectIcon)
        self.garmentSelectButton.setMaximumWidth(30)

        #________________________________Patterns________________________________#

        self.patternLabel = QtWidgets.QLabel("Patterns")
        self.patternLabel.setStyleSheet("color: rgb(240, 240, 240)")
        self.patternLabel.setAlignment(qc.Qt.AlignCenter)

        self.patternDisplayButton = QtWidgets.QPushButton()
        self.patternDisplayButton.setIcon(self.displayIcon)
        self.patternDisplayButton.setMaximumWidth(30)

        self.patternLockButton = QtWidgets.QPushButton()
        self.patternLockButton.setIcon(self.lockIcon)
        self.patternLockButton.setMaximumWidth(30)

        self.patternSelectButton = QtWidgets.QPushButton()
        self.patternSelectButton.setIcon(self.selectIcon)
        self.patternSelectButton.setMaximumWidth(30)

        # ________________________________Retopos________________________________#

        self.retopoLabel = QtWidgets.QLabel("Retopos")
        self.retopoLabel.setStyleSheet("color: rgb(240, 240, 240)")
        self.retopoLabel.setAlignment(qc.Qt.AlignCenter)

        self.retopoDisplayButton = QtWidgets.QPushButton()
        self.retopoDisplayButton.setIcon(self.displayIcon)
        self.retopoDisplayButton.setMaximumWidth(30)

        self.retopoLockButton = QtWidgets.QPushButton()
        self.retopoLockButton.setIcon(self.lockIcon)
        self.retopoLockButton.setMaximumWidth(30)

        self.retopoSelectButton = QtWidgets.QPushButton()
        self.retopoSelectButton.setIcon(self.selectIcon)
        self.retopoSelectButton.setMaximumWidth(30)        #


        self.outliner_mainWidget.layout().addWidget(self.garmentLabel, 3, 1)
        self.outliner_mainWidget.layout().addWidget(self.garmentDisplayButton, 3, 2)
        self.outliner_mainWidget.layout().addWidget(self.garmentLockButton, 3, 3)
        self.outliner_mainWidget.layout().addWidget(self.garmentSelectButton, 3, 4)
        self.outliner_mainWidget.layout().addWidget(self.patternLabel, 3, 5)
        self.outliner_mainWidget.layout().addWidget(self.patternDisplayButton, 3, 6)
        self.outliner_mainWidget.layout().addWidget(self.patternLockButton, 3, 7)
        self.outliner_mainWidget.layout().addWidget(self.patternSelectButton, 3, 8)
        self.outliner_mainWidget.layout().addWidget(self.retopoLabel, 3, 9)
        self.outliner_mainWidget.layout().addWidget(self.retopoDisplayButton, 3, 10)
        self.outliner_mainWidget.layout().addWidget(self.retopoLockButton, 3, 11)
        self.outliner_mainWidget.layout().addWidget(self.retopoSelectButton, 3, 12)


        #########################################################################################
        # start a connexion with couture core, this class contain all the function for the tool #
        #########################################################################################
        dicButtonToRestart = [self.garmentDisplayButton,self.garmentLockButton,self.garmentSelectButton,self.patternDisplayButton,self.patternLockButton,self.patternSelectButton,self.retopoDisplayButton,self.retopoLockButton,self.retopoSelectButton,self.buttonDelete,self.buttonAdd]
        self.core = cc.core(self.scrollLayout,dataNode,dicButtonToRestart)

        # if the couture node is not empty, Couture will restart with the previous datas stored

        if dataNode.getGarmentList() != None:
            self.core.autoload(self.garmentDisplayButton,self.garmentLockButton,self.garmentSelectButton,self.patternDisplayButton,self.patternLockButton,self.patternSelectButton,self.retopoDisplayButton,self.retopoLockButton,self.retopoSelectButton,self.buttonDelete,self.buttonAdd,dicButtonToRestart)
        self.garmentSelection = self.loadGarmentButton.clicked.connect(partial(self.core.garmentSelection,self.garmentDisplayButton,self.garmentLockButton,self.garmentSelectButton,self.buttonDelete,self.buttonAdd))

        self.uvLayoutButton.clicked.connect(partial(self.core.uvLayoutSelection))

        # ___________________________________________ Tab Widget ______________________________________________________#
        tab_widget = QtWidgets.QWidget()
        tab_widget.setStyleSheet("background-color: rgb(42, 54, 59)")

        tab_widget.setLayout(QtWidgets.QVBoxLayout())
        tab_widget.layout().setContentsMargins(0, 0, 0, 0)
        tab_widget.layout().setSpacing(2)
        tab_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                 QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(tab_widget)




        tab_panel = QtWidgets.QTabWidget()
        self.patternTab = QtWidgets.QWidget()
        self.sewingTab = QtWidgets.QWidget()
        self.weavingTab = QtWidgets.QWidget()
        tab_panel.addTab(self.patternTab, "Pattern table")
        tab_panel.addTab(self.sewingTab, "Sewing machine")
        tab_panel.addTab(self.weavingTab, "Weaving workshop")

        tab_widget.layout().addWidget(tab_panel)
        self.patternTabUI()

        # _________________________________________ About Widget ___________________________________________________#
        self.aboutQframeHolder = QtWidgets.QFrame()
        self.aboutQframeHolder.setMaximumHeight(120)
        self.aboutQframeHolder.setStyleSheet("background-color: rgb(52 ,81, 97)")
        self.aboutQframeHolder.setLayout(QtWidgets.QHBoxLayout())
        self.aboutQframeHolder.layout().setContentsMargins(0, 15, 0, 15)

        self.about_mainWidget = QtWidgets.QWidget()
        self.about_mainWidget.setStyleSheet("background-color: rgb(52 ,81, 97)")
        self.about_mainWidget.setLayout(QtWidgets.QGridLayout())

        self.aboutQframeHolder.layout().addWidget(self.about_mainWidget)

        layout.addWidget(self.aboutQframeHolder)







        # #### Title ####

        self.aboutTitle = QtWidgets.QLabel("About Couture")
        self.aboutTitle.setStyleSheet("color : rgb(240, 240, 240);font: bold 25px;")
        self.aboutTitle.setAlignment(qc.Qt.AlignCenter)
        self.about_mainWidget.layout().addWidget(self.aboutTitle, 0, 1,1,4)

        self.restartButton = QtWidgets.QPushButton("Restart Couture")
        self.tutorialButton = QtWidgets.QPushButton("Tutorials")
        self.wikiButton = QtWidgets.QPushButton("Wiki")
        self.aboutButton = QtWidgets.QPushButton("About")

        self.about_mainWidget.layout().addWidget(self.restartButton, 1, 1)
        self.about_mainWidget.layout().addWidget(self.tutorialButton, 1, 2)
        self.about_mainWidget.layout().addWidget(self.wikiButton, 1, 3)
        self.about_mainWidget.layout().addWidget(self.aboutButton, 1, 4)
        self.restartButton.clicked.connect(partial(self.core.resetCoutureWindow))
        self.tutorialButton.clicked.connect(partial(data.goToWeb,'https://www.artstation.com/psichari/blog/9dq7/couture-tutorial',None))
        self.wikiButton.clicked.connect(partial(data.goToWeb,'https://www.artstation.com/psichari/blog/z9b1/coutures-wiki',None))
        self.aboutButton.clicked.connect(partial(self.core.openAboutWindow))



        layout.insertSpacerItem(1,QtWidgets.QSpacerItem(0,20,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))
        layout.insertSpacerItem(3,QtWidgets.QSpacerItem(0,35,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))
        layout.insertSpacerItem(5,QtWidgets.QSpacerItem(0,35,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))
        layout.addSpacerItem(QtWidgets.QSpacerItem(0,1,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Expanding	))

        pm.select(cl=True)

    def patternTabUI(self):
        """
        This function build the pattern tab
        """
        mainLayout = QtWidgets.QVBoxLayout()

        ### connect the layout with the pattern tab widget ###
        self.patternTab.setLayout(mainLayout)

        ### Splitter "RETOPO" ###

        retopoLabel = Splitter("RETOPO")
        mainLayout.addWidget(retopoLabel)
        flattenPatternButton = QtWidgets.QPushButton("Flatten garments")
        mainLayout.addWidget(flattenPatternButton)

        mainLayout.layout().addLayout(SplitterLayout())

        exportOptionWidget = QtWidgets.QWidget()
        exportOptionWidget.setLayout(QtWidgets.QHBoxLayout())
        exportOptionWidget.layout().setContentsMargins(0,0,0,0)

        exportOptionLabel = QtWidgets.QLabel("Export options : ")
        exportOptionGroupBox = QtWidgets.QGroupBox()
        exportOptionGroupBox.setFlat(True)

        radio1 = QtWidgets.QRadioButton("Merged pieces")
        radio2 = QtWidgets.QRadioButton("Separated pieces")
        radio1.setChecked(True)



        hbox = QtWidgets.QHBoxLayout()

        exportOptionGroupBox.setStyleSheet("""
                                            background-color: rgb(42 , 54, 59);
                                            border: 2px  rgb(33 , 45, 50);
                                            border-radius: 2px;   
                                            """)
        hbox.addWidget(radio1)
        hbox.addWidget(radio2)
        hbox.addStretch(1)
        exportOptionGroupBox.setLayout(hbox)



        exportOptionWidget.layout().addWidget(exportOptionLabel)
        exportOptionWidget.layout().addWidget(exportOptionGroupBox)


        mainLayout.addWidget((exportOptionWidget))

        exportWidget = QtWidgets.QWidget()
        exportWidget.setLayout(QtWidgets.QHBoxLayout())
        exportWidget.layout().setContentsMargins(0,0,0,0)
        exportButton = QtWidgets.QPushButton("Export pattern")
        gozButton = QtWidgets.QPushButton("GoZ")

        mainLayout.addWidget((exportWidget))

        exportWidget.layout().addWidget(exportButton)
        exportWidget.layout().addWidget(gozButton)

        mainLayout.layout().addLayout(SplitterLayout())

        importWidget = QtWidgets.QWidget()
        importWidget.setLayout(QtWidgets.QHBoxLayout())
        importWidget.layout().setContentsMargins(0,0,0,0)

        importButton = QtWidgets.QPushButton("Import retopo")
        selectRetopoButton = QtWidgets.QPushButton("Select retopo")

        importWidget.layout().addWidget(importButton)
        importWidget.layout().addWidget(selectRetopoButton)

        mainLayout.addWidget((importWidget))

        ### Splitter "PAIRING" ###

        retopoLabel = Splitter("PAIRING")
        mainLayout.addWidget(retopoLabel)

        pairWidget = QtWidgets.QWidget()
        pairWidget.setLayout(QtWidgets.QHBoxLayout())
        pairWidget.layout().setContentsMargins(0,0,0,0)

        pairingButton = QtWidgets.QPushButton("Pairing flatten geometries")
        iconManual = qg.QPixmap("%s/icons/hand.png" % folderPath)
        manualButton = QtWidgets.QPushButton()
        manualButton.setIcon(iconManual)
        manualButton.setFixedWidth(50)

        pairWidget.layout().addWidget(pairingButton)
        pairWidget.layout().addWidget(manualButton)

        mainLayout.addWidget(pairWidget)


        transfertUVButton = QtWidgets.QPushButton("Transfert UVs")
        mainLayout.addWidget(transfertUVButton)

        ### Splitter "BLENDSHAPES" ###

        blendshapesLabel = Splitter("BLENDSHAPES")
        mainLayout.addWidget(blendshapesLabel)

        blendshapeButton = QtWidgets.QPushButton("Create blendshapes")
        mainLayout.addWidget(blendshapeButton)

        blendshapesWidget = QtWidgets.QWidget()
        blendshapesWidget.setLayout(QtWidgets.QHBoxLayout())

        ### Create the blendshape slider ###
        self.textfieldBs = QtWidgets.QLineEdit()
        self.sliderBs = QtWidgets.QSlider(qc.Qt.Horizontal)
        self.sliderBs.setRange(0, 100)
        self.sliderBs.setTickInterval(1)
        sliderStyle = open("%s/Qss/Slider.qss" % folderPath).read()
        self.sliderBs.setStyleSheet(sliderStyle)
        iconSliders = qg.QPixmap("%s/icons/sliders.png" % folderPath)
        buttonSliders = QtWidgets.QPushButton()
        buttonSliders.setIcon(iconSliders)
        buttonSliders.setFixedWidth(50)
        self.textfieldBs.setText("0")
        self.textfieldBs.setFixedHeight(40)
        self.textfieldBs.setFixedWidth(40)

        blendshapesWidget.layout().addWidget(self.textfieldBs)
        blendshapesWidget.layout().addWidget(self.sliderBs)
        blendshapesWidget.layout().addWidget(buttonSliders)
        mainLayout.addWidget(blendshapesWidget)

        ### Splitter "WRAP" ###

        wrapLabel = Splitter("WRAP")
        mainLayout.addWidget(wrapLabel)
        wrapButton = QtWidgets.QPushButton("Wrap pairs")
        mainLayout.addWidget(wrapButton)

        ### Splitter "EDIT MODE" ###

        editModeLabel = Splitter("EDIT MODE")
        editModeWidget = QtWidgets.QWidget()
        editModeWidget.setLayout(QtWidgets.QHBoxLayout())
        editModeWidget.layout().setContentsMargins(0,0,0,0)
        softenNormalButton = QtWidgets.QPushButton("Soften edge selected")
        editModeButton = QtWidgets.QPushButton("Edit selected")
        cancelEditButton = QtWidgets.QPushButton("Cancel edit")
        applyEditButton = QtWidgets.QPushButton("Apply edit")


        mainLayout.addWidget(editModeLabel)
        mainLayout.addWidget(softenNormalButton)
        mainLayout.addWidget((editModeWidget))

        editModeWidget.layout().addWidget(editModeButton)
        editModeWidget.layout().addWidget(cancelEditButton)
        editModeWidget.layout().addWidget(applyEditButton)

        ###########################
        ### Connect the buttons ###
        ###########################

        flattenPatternButton.clicked.connect(partial(self.core.flattenGeo,self.patternDisplayButton,self.patternLockButton,self.patternSelectButton))
        exportButton.clicked.connect(partial(self.core.exportFlatten))
        gozButton.clicked.connect(partial(self.core.GoZExport,folderPath))
        importButton.clicked.connect(partial(self.core.importRetopo))
        selectRetopoButton.clicked.connect(partial(self.core.selectRetopo))
        pairingButton.clicked.connect(partial(self.core.pairsMatching,self.retopoDisplayButton,self.retopoLockButton,self.retopoSelectButton))
        manualButton.clicked.connect(partial(self.core.manualPairsMatchingWindow))
        transfertUVButton.clicked.connect(partial(self.core.transfertUV))
        blendshapeButton.clicked.connect(partial(self.core.createMultiBlendshapes))
        wrapButton.clicked.connect(partial(self.core.createMultiWraps))
        self.sliderBs.valueChanged.connect(partial(self.core.driveBlendnodes,self.sliderBs,self.textfieldBs))
        buttonSliders.clicked.connect(partial(self.core.nodeBsWindow, folderPath))
        softenNormalButton.clicked.connect(partial(self.core.softenEdgeSelected))
        editModeButton.clicked.connect(partial(self.core.editSelected))
        cancelEditButton.clicked.connect(partial(self.core.cancelEditWindow))
        applyEditButton.clicked.connect(partial(self.core.applyEditWindow))


        radio1.toggled.connect(partial(self.core.radio1_clicked))
        radio2.toggled.connect(partial(self.core.radio2_clicked))


class Splitter(QtWidgets.QWidget):
    def __init__(self, text=None, shadow=True, color=(200, 200, 200), marginHeight=5):


        """
        Create a title splitter 
        @param text: str,name of the title
        @param shadow: bool, turn on or off a shadow effect
        @param color: tuple, set the color 
        @param marginHeight: int, set the height of the splitter
        """
        QtWidgets.QWidget.__init__(self)

        self.setMinimumHeight(2)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, marginHeight, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)

        first_line = QtWidgets.QFrame()
        first_line.setFrameStyle(QtWidgets.QFrame.HLine)
        self.layout().addWidget(first_line)

        main_color = 'rgba( %s,  %s,  %s, 255)' % color
        shadow_color = 'rgba( 45,  45,  45, 255)'
        bottom_border = ''
        if shadow:
            bottom_border = 'border-bottom:1px solid %s;' % shadow_color

        style_sheet = "border:0px solid rgba(0,0,0,0); \
                               background-color:%s; \
                               max-height:1px; \
                               %s;" % (main_color, bottom_border)
        first_line.setStyleSheet(style_sheet)

        if text is None:
            return

        font = qg.QFont()
        font.setBold(True)
        font.setPixelSize(18)
        text_width = qg.QFontMetrics(font)
        width = text_width.width(text) + 6

        label = QtWidgets.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setAlignment(qc.Qt.AlignHCenter)

        label.setMaximumWidth(width)

        self.layout().addWidget(label)

        second_line = QtWidgets.QFrame()
        second_line.setFrameStyle(QtWidgets.QFrame.HLine)
        self.layout().addWidget(second_line)
        second_line.setStyleSheet(style_sheet)


class SplitterLayout(QtWidgets.QHBoxLayout):


    def __init__(self):
        """
        Create a subtle splitter
        """
        QtWidgets.QHBoxLayout.__init__(self)
        self.setContentsMargins(40, 2, 40, 2)

        splitter = Splitter(shadow=False, color=(60, 60, 60), marginHeight=0)
        splitter.setFixedHeight(1)

        self.addWidget(splitter)




# Copyright (c) 2018 Florian Croquet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.