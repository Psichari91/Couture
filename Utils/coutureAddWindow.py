import sys, os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)).rpartition("\\Utils")[0] +"\\vendor\\qtpy" )
from functools import partial

from Qt import QtWidgets
from Qt import QtCore as qc
from Qt import QtGui as qg

import pymel.core as pm
import coutureMessage as cm
import Data as data
import coutureShader as cs
reload(cs)

reload (cm)

import time
dialog = None



class addGarmentWindow(QtWidgets.QDialog):
    def __init__(self,folderPath,coutureCore,dataNode):
        """
        Create a specific window allowing user to add new piece of cloth in the scene, depending on the current progression this class will create all the appropriate deformers and connections
        @param folderPath: String, get the path to couture folder
        @param coutureCore: Get the current CoutureCore
        @param dataNode: CoutureNode,Get the current CoutureNode
        """


        QtWidgets.QDialog.__init__(self)

        self.coutureCore = coutureCore
        self.dataNode = dataNode

        # Those 3 variables hold the data of each new meshes added according to it state of progression
        self.soloGarment = []
        self.soloPattern = []
        self.soloRetopo = []

        # Building UI
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

        add_widget = QtWidgets.QWidget()
        add_widget.setLayout(self.gridTemplate)

        firstLine = QtWidgets.QWidget()
        firstLine.setLayout(QtWidgets.QHBoxLayout())
        firstLine.layout().setContentsMargins(0, 0, 0, 0)
        self.gridTemplate.addWidget(firstLine, 0, 0)

        titleGarment = QtWidgets.QLabel("Garment")
        self.qLineGarment = QtWidgets.QLineEdit()
        self.qLineGarment.setPlaceholderText("Select or import a geometry")



        selectGarmentIcon =  qg.QPixmap("%s/icons/arrowSelect.png" % folderPath)
        selectGarmentButton = QtWidgets.QPushButton()
        selectGarmentButton.setIcon(selectGarmentIcon)
        selectGarmentButton.setMinimumWidth(50)
        selectGarmentButton.clicked.connect(partial(self.selectSolo,"garment"))

        importGarmentIcon = qg.QPixmap("%s/icons/folder.png" % folderPath)
        importGarmentButton = QtWidgets.QPushButton()
        importGarmentButton.setIcon(importGarmentIcon)
        importGarmentButton.setMinimumWidth(50)
        importGarmentButton.clicked.connect(partial(self.browseMesh, "garment"))

        firstLine.layout().addWidget(titleGarment)
        firstLine.layout().addWidget(self.qLineGarment)
        firstLine.layout().addWidget(selectGarmentButton)
        firstLine.layout().addWidget(importGarmentButton)

        # Create an interface for the pattern mesh if user reach this step
        if self.coutureCore.boolFlattenGarment == False:
            secondLine = QtWidgets.QWidget()
            secondLine.setLayout(QtWidgets.QHBoxLayout())
            secondLine.layout().setContentsMargins(0, 10, 0, 10)
            self.gridTemplate.addWidget(secondLine, 1, 0)

            flattenButton = QtWidgets.QPushButton("Flatten Garment")
            flattenButton.clicked.connect(self.flattenSolo)

            gozButton = QtWidgets.QPushButton("GoZ pattern")
            gozButton.clicked.connect(self.gozSelPattern)
            exportButton = QtWidgets.QPushButton("Export pattern")
            exportButton.clicked.connect(self.exportSelPattern)

            self.layout().setSpacing(20)

            secondLine.layout().addWidget(flattenButton)
            secondLine.layout().addWidget(gozButton)
            secondLine.layout().addWidget(exportButton)

        # Create an interface for the retopo mesh if user reach this step
        if self.coutureCore.boolDefineRetopo == False:

            thirdLine = QtWidgets.QWidget()
            thirdLine.setLayout(QtWidgets.QHBoxLayout())
            thirdLine.layout().setContentsMargins(0, 0, 0, 0)
            add_widget.layout().addWidget(thirdLine, 0, 1)


            thirdLine = QtWidgets.QWidget()
            thirdLine.setLayout(QtWidgets.QHBoxLayout())
            thirdLine.layout().setContentsMargins(0, 0, 0, 0)
            add_widget.layout().addWidget(thirdLine, 0, 1)

            titleRetopo = QtWidgets.QLabel("Retopo  ")
            self.qLineRetopo = QtWidgets.QLineEdit()
            self.qLineRetopo.setPlaceholderText("Select or import a geometry")
            self.qLineRetopo.setFrame(True)

            selectRetopoIcon = qg.QPixmap("%s/icons/arrowSelect.png" % folderPath)
            selectRetopoButton = QtWidgets.QPushButton()
            selectRetopoButton.setIcon(selectRetopoIcon)
            selectRetopoButton.setMinimumWidth(50)
            selectRetopoButton.clicked.connect(partial(self.selectSolo,"retopo"))

            importRetopoIcon = qg.QPixmap("%s/icons/folder.png" % folderPath)
            importRetopoButton = QtWidgets.QPushButton()
            importRetopoButton.setIcon(importRetopoIcon)
            importRetopoButton.setMinimumWidth(50)
            importRetopoButton.clicked.connect(partial(self.browseMesh, "retopo"))


            thirdLine.layout().addWidget(titleRetopo)
            thirdLine.layout().addWidget(self.qLineRetopo)
            thirdLine.layout().addWidget(selectRetopoButton)
            thirdLine.layout().addWidget(importRetopoButton)

            self.gridTemplate.addWidget(thirdLine, 2, 0)


        addGarmentButton = QtWidgets.QPushButton("Add this garment")
        addGarmentButton.clicked.connect(partial(self.addConfirmed))

        cancelAddButton = QtWidgets.QPushButton("Cancel")
        cancelAddButton.clicked.connect(partial(self.killWindow))

        self.layout().addWidget(add_widget)

        buttonWidget = QtWidgets.QWidget()
        buttonWidget.setLayout(QtWidgets.QHBoxLayout())

        buttonWidget.layout().addWidget(addGarmentButton)
        buttonWidget.layout().addWidget(cancelAddButton)


        self.layout().addWidget(buttonWidget)

    def closeEvent(self, event):
        delete()

    def killWindow(self):
        delete()

    def selectSolo(self,type):

        """ !@Brief
        Use user selection to define a mesh for each step of couture and file the appropriate QLineEdit
        @param type: String, There's four type of selection "garment","retopo"
        """

        # Run basic check on the user selection
        selection = pm.selected(fl=True)
        if selection == []:
            cm.create("Nothing selected", " OK !",None,None)
            return

        if len(selection) > 1 :
            cm.create("Too many objects selected"," OK !",None,None)
        else:
            if type == "garment":
                if pm.objExists("soloGarmentObjectGRP"):
                    pm.delete("soloGarmentObjectGRP")
                sg = ""
                if pm.objExists('Garment_Shader'):
                    sg = pm.PyNode("Garment_SG")
                pm.sets(sg, edit=1, forceElement=selection[0])

                self.soloGarment = selection[0]
                self.qLineGarment.setText("%s"%selection[0])

                soloGrp = pm.group(n= "soloGarmentObjectGRP",em=True)
                selection[0].setParent(soloGrp)
            else:
                if pm.objExists("soloGarmentObjectGRP"):
                    pm.delete("soloGarmentObjectGRP")
                sg = ""
                if pm.objExists('Retopo_Shader'):
                    sg = pm.PyNode("Retopo_SG")
                pm.sets(sg, edit=1, forceElement=selection[0])

                self.soloRetopo = selection[0]
                self.qLineRetopo.setText("%s" % selection[0])

                soloGrp = pm.group(n= "soloRetopoObjectGRP",em=True)
                selection[0].setParent(soloGrp)
    def browseMesh(self,type):
        """ !@Brief
        Allow user to import and select a mesh from a file
        @param type: String, There's four type of selection "garment","retopo"
        """

        exportPath = self.dataNode.getExportPath()

        singleFilter = "*.obj;;*.fbx;;*.ma;;*.mb"
        if exportPath == "":
            selection = pm.fileDialog2(fm=1, fileFilter=singleFilter, dialogStyle=2, cap="Import object",
                                       rf=True)
        else:
            selection = pm.fileDialog2(fm=1, fileFilter=singleFilter, dialogStyle=2, cap="Import object",
                                       rf=True,
                                       dir=exportPath)
        if selection == None:
            return

        if type == "garment":
            if pm.objExists("soloGarmentObjectGRP"):
                pm.delete("soloGarmentObjectGRP")
            importedNode = pm.importFile(selection[0], i=True, returnNewNodes=True, groupReference=True,
                                         groupName="soloGarmentObjectGRP")

            grp = pm.PyNode("soloGarmentObjectGRP")
            grpChildren = pm.listRelatives(grp, c=True)
            if len(grpChildren) >1:
                cm.create("Too many objects imported", " OK !", None, None)
                return

            sg = ""
            if pm.objExists('Garment_Shader'):
                sg = pm.PyNode("Garment_SG")

            pm.sets(sg, edit=1, forceElement=grpChildren[0])
        else:
            if pm.objExists("soloRetopoObjectGRP"):
                pm.delete("soloRetopoObjectGRP")
            importedNode = pm.importFile(selection[0], i=True, returnNewNodes=True, groupReference=True,
                                         groupName="soloRetopoObjectGRP")
            grp = pm.PyNode("soloRetopoObjectGRP")
            grpChildren = pm.listRelatives(grp, c=True)
            if len(grpChildren) >1:
                cm.create("Too many objects imported", " OK !", None, None)
                return

            sg = ""
            if pm.objExists('Retopo_Shader'):
                sg = pm.PyNode("Retopo_SG")

            pm.sets(sg, edit=1, forceElement=grpChildren[0])

        geoTest = data.testGeo(grpChildren)
        for object in geoTest[1]:
            object.setParent(world=True)
            pm.delete(object)



        if len(geoTest[0]) == 1:
            try:
                separate = pm.polySeparate(grpChildren[0])
                for object in separate:
                    pm.delete(object)
                cm.create("You can import a single mesh only", "Ok")
                return

            except:

                ### Output the name of the mesh in the appropriate textflied  ###
                if type == "garment":
                    self.soloGarment = grpChildren[0]
                    self.qLineGarment.setText("%s" % grpChildren[0])
                elif type == "retopo":
                    self.soloRetopo = grpChildren[0]
                    self.qLineRetopo.setText("%s" % grpChildren[0])

                pass
        elif len(geoTest[0]) > 1:
            pm.delete(grpChildren)
            cm.create("You can import a single mesh only", "Ok")
            return

    def flattenSolo(self):

        """ !@Brief
        This function perform a flatten garment on a single garment
        """
        if pm.objExists("soloPatternObjectGRP"):
            pm.delete("soloPatternObjectGRP")

        flattenResult = self.coutureCore.flattenSoloGeo(self.soloGarment)

        self.soloPattern = flattenResult[0]

    def exportSelPattern(self):

        """ !@Brief
        Allow user to export the pattern
        """
        pm.select(cl=True)
        selGarment = pm.select("|soloPatternObjectsGRP|pattern_%s"%(self.qLineGarment.text()))

        ### user must pick a file location ###
        exportPath = self.dataNode.getExportPath()
        singleFilter = "*.obj;;*.fbx;;*.ma;;*.mb"
        if exportPath == "":
            selection = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Flatten objects exporter", rf=True)
        else:
            selection = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Flatten objects exporter", rf=True,
                                       dir=exportPath)

        exportObject = selection[0]

        ### perform the export ###

        if selection[0][-1] == "*":
            exportObject = selection[0].replace("*", "obj")

        if selection[1] == "*.obj":
            pm.exportSelected(exportObject, type='OBJexport',
                              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', f=True)

        elif selection[1] == "*.fbx":
            pm.exportSelected(exportObject, type='FBX export',
                              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', f=True)

        elif selection[1] == "*.ma":
            pm.exportSelected(exportObject, type='mayaAscii', options='v=0;', f=True)

        else:
            pm.exportSelected(exportObject, type='mayaBinary', options='v=0;', f=True)

    def gozSelPattern(self):

        """ !@Brief
        Allow user to export the pattern with Goz
        """

        pm.select(cl=True)
        selGarment = pm.select("|soloPatternObjectsGRP|pattern_%s" % (self.qLineGarment.text()))

        import maya.mel as mel
        try:
            mel.eval("""source "C:/Users/Public/Pixologic/GoZApps/Maya/GoZBrushFromMaya.mel" """)
        except:
            cm.create("""It seems like GoZ is not installed on your Maya\n You will have to export manually :( """,
                      "Ok, I got it !")

    def addConfirmed(self):

        """ !@Brief
        Definitly add to couture the pieces
        """

        ### Run a series of check to difine the current progression of the user and add the new pieces with the correct deformers
        if self.coutureCore.boolDefineRetopo == False:

            self.soloRetopo.rename("retopo_" +self.soloGarment)

            self.soloGarment.setParent(pm.PyNode("garmentObjectsGRP"))
            self.soloPattern.setParent(pm.PyNode("patternObjectsGRP"))
            self.soloRetopo.setParent(pm.PyNode("retopoObjectsGRP"))

            if self.coutureCore.boolPairFlatten == False:

                self.coutureCore.addPatternDic(["|garmentObjectsGRP|"+self.qLineGarment.text(),self.soloPattern.longName(),self.soloRetopo.longName()])

            if self.coutureCore.boolCreateBs == False:
                self.coutureCore.createSoloBlendshape(["|garmentObjectsGRP|"+self.qLineGarment.text(),self.soloPattern.longName()])

            if self.coutureCore.boolCreateWrap == False:
                self.coutureCore.createSoloWrap([self.soloPattern.longName(),self.soloRetopo.longName()])

        elif self.coutureCore.boolFlattenGarment == False:

            self.soloGarment.setParent(pm.PyNode("garmentObjectsGRP"))
            self.soloPattern.setParent(pm.PyNode("patternObjectsGRP"))

            self.coutureCore.addPatternDic(["|garmentObjectsGRP|"+self.qLineGarment.text(),self.soloPattern.longName(), None])

        elif  self.coutureCore.boolLoadGarment == False:

            self.soloGarment.setParent(pm.PyNode("garmentObjectsGRP"))

            self.coutureCore.addPatternDic(["|garmentObjectsGRP|"+self.qLineGarment.text(), None, None])

        self.killWindow()
        try:
            pm.delete("soloGarmentObjectGRP")
        except:
            pass

        try:
            pm.delete("soloPatternObjectGRP")
        except:
            pass

        try:
            pm.delete("soloRetopoObjectGRP")
        except:
            pass


def create(folderPath,coutureCore,dataNode):
    global dialog
    if dialog is None:
        dialog = addGarmentWindow(folderPath,coutureCore,dataNode)
    dialog.show()
    return dialog

def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None
