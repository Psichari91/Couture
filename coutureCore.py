"""
This class include all the functions for this tool
"""

from vendor.qtpy.Qt import QtWidgets
from vendor.qtpy.Qt import QtCore as qc
from vendor.qtpy.Qt import QtGui as qg
from Utils import Data as data

from ast import literal_eval
import re
import os
import pymel.core as pm
from maya import cmds, OpenMaya
from functools import partial
import math
from Utils import odict as odict
reload (odict)

import coutureOutliner as co
reload (co)

from Utils import coutureMessage as cm
reload (cm)

from Utils import coutureBSWindow as cbsw
reload (cbsw)

from Utils import coutureWrap as cw
reload (cw)

from Utils import coutureShader as cs
reload(cs)

from Utils import coutureValidation as cv
reload(cv)

from Utils import coutureAddWindow as caw
reload(caw)

from Utils import coutureManualWindow as cmw
reload(cmw)

from Utils import coutureAboutlWindow as cAboutWindow
reload(cAboutWindow)

import time
import logging

logging.basicConfig()
logger = logging.getLogger('CoutureCore')
logger.setLevel(logging.INFO)
folderPath = os.path.split(__file__)[0].rpartition("\Couture")[0] + "/Couture"




class core():
    def __init__(self,layout,dataNode,buttonToRestart):

        """ !@Brief
        Create a class that will handle all the function performed by couture
        @param layout: Qlayout, this is the layout that will receive the couture Outliner
        @param dataNode: coutureNode, this is will hold the coutureNode in the scene
        @param buttonToRestart: list, This is a list of button that need to be disconnected during a retart of couture
        """

        self.dataNode = dataNode
        self.buttonToRestart= buttonToRestart
        self.bsSlider = ""

        ### the most important dictionnary of the tool, it stores every group of garment/pattern/retopo
        ### Data structure:
        ### self.patternDic["GarmentLongName"]:["garmentLongName","RetopoLongName"]
        self.patternDic = odict.OrderedDict()

        ### connexion with the outliner class ###
        self.outliner = co.outliner(layout)

        ### store every blendshape node created by couture
        self.blendNodeList = []

        ### set the export style format
        self.mergeBool = True
        self.separateBool = False

        self.scaleFactor = 0
        self.translateX = 0

        ### store the currently edited meshes
        self.editDic = {}


        ### store the states of visibility and lock attributes
        self.boolLockGarment = False
        self.boolVizGarment = True
        self.boolLockPattern = False
        self.boolVizPattern = True
        self.boolLockRetopo = False
        self.boolVizRetopo = True

        ### Different boolean attribute which track the user progression in the workflow
        self.boolLoadGarment = True
        self.boolSoloGarment = False
        self.boolFlattenGarment = True
        self.boolDefineRetopo = True
        self.boolPairFlatten = True
        self.boolErrorPair = False
        self.boolCreateBs = True
        self.boolCreateWrap = True

        ### Data storage for adding individual piece of new cloth
        self.soloGarment = []
        self.soloPattern = []
        self.soloRetopo = []

    def addPatternDic(self,objects):

        """ !@Brief
        According to the user selection from the add garment window, this function will add a new garment and its pattern/retopo to couture dictionnary
        @param objects: List, List of garment/pattern/retopo
        """

        #Hold data from self.patternDic before updating DataNode
        garmentListUpdate = []
        patternListUpdate = []
        retopoListUpdate = []

        if objects[2] != None:
            
            self.patternDic[str(objects[0])] = [str(objects[1]),str(objects[2])]
            
            #update coutureNode 
            for garmentName, keys in self.patternDic.items():
                garmentListUpdate.append(garmentName)
                patternListUpdate.append(keys[0])
                retopoListUpdate.append(keys[1])


            self.dataNode.addGarmentList(garmentListUpdate)
            self.dataNode.addPatternList(patternListUpdate)
            self.dataNode.addRetopoList(retopoListUpdate)
        elif objects[2] == None:
            self.patternDic[str(objects[0])] = [str(objects[1]), ""]

            for garmentName, keys in self.patternDic.items():
                garmentListUpdate.append(garmentName)
                patternListUpdate.append(keys[0])

            self.dataNode.addGarmentList(garmentListUpdate)
            self.dataNode.addPatternList(patternListUpdate)

        elif objects[1] == None:
            self.patternDic[str(objects[0])] = ["", ""]

            for garmentName, keys in self.patternDic.items():
                garmentListUpdate.append(garmentName)

            self.dataNode.addGarmentList(garmentListUpdate)


        widgetLine = self.outliner.outlinerLine(pm.PyNode(objects[0]), "garment")
        self.outliner.orderWidget[objects[0]] = [widgetLine]

        self.outliner.drawLines()

        # connect the expend button on each line of the outliner
        if objects[2] != None:
            self.outliner.updateArrowDownLine2(self.patternDic)

            self.outliner.lineNumber[objects[0]] = "three"

        elif objects[2] == None:
            self.outliner.updateArrowDownLine1(self.patternDic)
            self.outliner.lineNumber[objects[0]] = "two"

    def uvLayoutSelection(self):
        """ !@Brief
        Allow user to unfold selected mesh before using couture
        """

        pm.polyMultiLayoutUV(ps=0.2, fr=1, gv=1, gu=1, psc=0, lm=1, l=2, su=1, sv=1, ov=0, sc=1, rbf=1, ou=0)

    def mergeSavior(self,geometries):
        """ !@Brief
        Get rid of hidden duplicated geometries
        @param geometries: List, List of geometries to clean
        """

        for geo in geometries:
            pm.polyMergeVertex(geo, ch=1, am=1, d=0.0001)
            pm.select(cl=True)

    def garmentSelection(self,vizButton,lockButton,selectButton,deleteButton,addButton):

        """ !@Brief
        Add all the selected pieces of garments in the outliner UI, this will also connect the UI visbility and lock button for the "garment" meshes
        @param vizButton: QPushButton, this is the eye button for garment meshes
        @param lockButton: QPushButton, this is the lock button for garment meshes
        @param selectButton: QPushButton, this is the selection button for garment meshes
        @param deleteButton: QPushButton, this button allow the user to later delete individual piece of cloth for the outliner and from the tool
        @param addButton: QPushButton, this button allow the user to later add individual new piece of cloth
        """

        if pm.selected() == []:
            cm.create("""You have nothing selected.""",
                      """Ok !""",
                      None,
                      None)
            return

        ### create a new coutureDataNode
        if not pm.objExists('CoutureDataNode'):
            selectionSave = pm.selected(fl=True)
            self.dataNode = data.coutureDataNode()
            pm.select(cl=True)
            pm.select(selectionSave)


        ### if no garments are already loaded in the tool
        if self.boolLoadGarment == True:

            dataNodeList = []
            selectionName = []
            selectionNode = pm.selected(fl=True)
            namespaceFound = []
            ### get rid of possible Namespace
            for node in selectionNode:

                if node.rpartition(":")[0] != "":
                    if node.rpartition(":")[0]+':' in namespaceFound:
                        pass
                    else:
                        namespaceFound.append(node.rpartition(":")[0]+':')
            data.removeNamespace(namespaceFound)


            if len(selectionNode) == 1:

                tmpGrp = pm.group(n="tmpGroup", em=True)
                selectionNode[0].setParent(tmpGrp)
                try:

                    separate = pm.polySeparate(pm.selected(fl=True))
                    selectionNode = []
                    for item in separate:
                        try:
                            if pm.nodeType(item.getShape(), api=True) == "mesh":
                                item.setParent(w=True)
                                selectionNode.append(item)
                        except:

                            pass
                    pm.select(separate)
                    pm.delete(constructionHistory=True)
                except:
                    self.boolSoloGarment = True
                    self.dataNode.changeBoolSoloGarment("True")
                    pass

            pm.select(cl=True)
            self.garmentGRP = pm.group(n= "garmentObjectsGRP",em=True)

            pm.select(cl=True)

            ### create a basic shader for garment clothes ###

            sg = ""
            if pm.objExists('Garment_Shader'):
                sg = pm.PyNode("Garment_SG")
            else:
                shader = cs.createShadingNode("Garment")
                sg = shader[1]
                pm.select(cl=True)

            shadow = True
            patternNumber = 0
            for node in selectionNode:
                selectionName.append(str(node.name()))


            selection = data.humanSorting(selectionName)


            for itemName in selection:
                item = pm.PyNode(itemName)
                ### apply default shader ###
                pm.sets(sg, edit=1, forceElement=item)
                item.setParent(self.garmentGRP)

            garmentInGRP = pm.listRelatives(self.garmentGRP, c=True)

            for garment in garmentInGRP:

                ### start a dictionnary that will contain the garment geo, the flatten gen and the retopo geo ###

                self.patternDic[str(garment.longName())] = ["", ""]
                dataNodeList.append(str(garment.longName()))

                ### add a line in the outliner  ###

                widgetLine = self.outliner.outlinerLine(garment, "garment")

                self.outliner.orderWidget[str(garment.longName())] = [widgetLine]


            ### refresh outliner ###

            self.outliner.drawLines()

            pm.select(cl=True)

            ### create a layer ###

            pm.select(self.garmentGRP)

            layer = pm.createDisplayLayer(nr=1, name="garmentObjects_layer", number=1)

            vizButton.clicked.connect(partial(self.vizLayerGarment,"garmentObjects_layer",vizButton))
            lockButton.clicked.connect(partial(self.lockGarment,"garmentObjects_layer",lockButton))
            selectButton.clicked.connect(partial(self.selectAllGeo,dataNodeList))
            pm.select(cl=True)
            self.dataNode.addGarmentList(dataNodeList)

            self.boolLoadGarment = False
            self.dataNode.changeBoolLoadGarment("False")
            deleteButton.clicked.connect(self.applyDeleteWindow)
            addButton.clicked.connect(partial(self.addGarment))

            if  pm.objExists('tmpGroup'):
                pm.delete('tmpGroup')

        else :
            if self.boolFlattenGarment == True:
                cm.create("""Garments have already been loaded, use "+" button to add some more.""",
                          """Ok !""",
                          """Reset garments selection""",
                          partial(self.resetGarmentSelection,vizButton,lockButton,selectButton,deleteButton,addButton))
            else :
                cm.create("""Garments have already been loaded, use "+" button to add some more.""",
                          """Ok !""",
                          None,
                          None)

            return

    def resetGarmentSelection(self,vizButton,lockButton,selectButton,deleteButton,addButton,coutureMesage):

        """ !@Brief
        Allow user to reselect pattern if he want to change his selection before starting to work
        @param vizButton: QPushButton, this is the eye button for garment meshes
        @param lockButton: QPushButton, this is the lock button for garment meshes
        @param selectButton: QPushButton, this is the selection button for garment meshes
        @param deleteButton: QPushButton, this button allow the user to later delete individual piece of cloth for the outliner and from the tool
        @param addButton: QPushButton, this button allow the user to later add individual new piece of cloth
        """

        saveSelection = pm.selected(fl=True)
        ### Delete previous selection
        if pm.objExists('garmentObjectsGRP'):
            oldGarments = pm.listRelatives("garmentObjectsGRP", c=True)
            for garment in oldGarments:
                garment.setParent(w=True)
            pm.delete("garmentObjectsGRP")

        ### Reset values
        self.boolLoadGarment = True
        self.dataNode.changeBoolLoadGarment("True")
        self.patternDic = odict.OrderedDict()
        self.outliner.resetOutliner()

        coutureMesage.killWindow()

        pm.select(saveSelection)
        self.garmentSelection(vizButton,lockButton,selectButton,deleteButton,addButton)
    def addGarment(self):
        """ !@Brief
        Open a window to add individual new piece of cloth
        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene
        """

        caw.create(folderPath,self,self.dataNode)

    def applyDeleteWindow(self):

        """ !@Brief
        Launch a "Delete window", that allow user to delete a garment from the plugin
        """

        #create a list of garment from the main dictionary
        garmentList = []
        for garmentName, keys in self.patternDic.items():
            garmentList.append(pm.PyNode(garmentName))

        cv.create( garmentList,"Delete",self,"Return to Couture")

    def applyDelete(self,selection):

        """ !@Brief
        Get back a selection of garment from the "delete edit window" and then delete the selection from the plugin
        the same function is used by the "delete selected" and "delete all" button from the "delete edit window"

        @param selection : list, this is a list of different garments selected by the user.

        """
        for item in selection:

            try :
                blends = pm.PyNode("|patternObjectsGRP|pattern_" + item.name()).getShape().inputs(type='blendShape')
                tempBSList = literal_eval(self.dataNode.getBsNodeList())

                tempBSList.remove(str(blends[0].longName()))

                self.dataNode.addBsNodeList(tempBSList)
                self.blendNodeList = [pm.PyNode(bs) for bs in literal_eval(self.dataNode.getBsNodeList())]

            except:
                pass
            # delete the object from the main dictonary and the outliner
            pm.evalDeferred("""cmds.delete("|garmentObjectsGRP|%s")"""%item.name())
            if self.boolCreateWrap == False:
                pm.evalDeferred("""cmds.delete("|patternObjectsGRP|pattern_%sBase")""" % item.name())
            pm.evalDeferred("""cmds.delete("|patternObjectsGRP|pattern_%s")""" % item.name())
            pm.evalDeferred("""cmds.delete("|retopoObjectsGRP|retopo_%s")""" % item.name())


            self.patternDic.pop(str(item.longName()))
            self.outliner.orderWidget[str(item.longName())][0].deleteLater()
            self.outliner.orderWidget.pop(str(item.longName()))
            try:
                # clean the outliner from the expanded line of a given garment
                self.outliner.orderWidget["%s" % str(data.longNameEdit("garment",item.longName(),"garment",'retopo'))][0].deleteLater()
                self.outliner.orderWidget.pop("%s" % str(data.longNameEdit("garment",item.longName(),"garment",'retopo')))


            except:
                pass
            try:
                # clean the outliner from the expanded line of a given garment
                self.outliner.orderWidget["%s" % str(data.longNameEdit("garment",item.longName(),"garment",'pattern'))][0].deleteLater()
                self.outliner.orderWidget.pop("%s" % str(data.longNameEdit("garment",item.longName(),"garment",'pattern')))

            except:
                pass

        # redraw the outliner

        self.outliner.drawLines()
        garmentListUpdate = []
        patternListUpdate = []
        retopoListUpdate = []

        # update coutureNode
        for garmentName, keys in self.patternDic.items():
            garmentListUpdate.append(garmentName)
            patternListUpdate.append(keys[0])
            retopoListUpdate.append(keys[1])

        self.dataNode.addGarmentList(garmentListUpdate)
        self.dataNode.addPatternList(patternListUpdate)
        self.dataNode.addRetopoList(retopoListUpdate)

    def vizLayerGarment(self, layerName,button):
        """ !@Brief
        Set the visibility of the source clothes meshes
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the view button for Source meshes
        """

        if self.boolVizGarment == True:
            displayIcon = qg.QPixmap("%s/icons/eyeOff.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizGarment = False

        elif self.boolVizGarment == False:
            displayIcon = qg.QPixmap("%s/icons/eyeOn.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizGarment = True

    def vizLayerPattern(self, layerName,button):

        """ !@Brief
        Set the visibility of the pattern meshes
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the view button for pattern meshes
        """

        if self.boolVizPattern == True:
            displayIcon = qg.QPixmap("%s/icons/eyeOff.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizPattern = False

        elif self.boolVizPattern == False:
            displayIcon = qg.QPixmap("%s/icons/eyeOn.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizPattern = True

    def vizLayerRetopo(self, layerName,button):

        """ !@Brief
        Set the visibility of the Retopo meshes
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the view button for Retopo meshes
        """

        if self.boolVizRetopo == True:
            displayIcon = qg.QPixmap("%s/icons/eyeOff.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizRetopo = False

        elif self.boolVizRetopo == False:
            displayIcon = qg.QPixmap("%s/icons/eyeOn.png" % folderPath)
            button.setIcon(displayIcon)
            pm.mel.layerEditorLayerButtonVisibilityChange(layerName)
            self.boolVizRetopo = True

    def lockGarment(self, layer,button):

        """ !@Brief
        Set the garment meshes to reference
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the lock button for garment meshes
        """
        pm.select(cl=True)

        if self.boolLockGarment == False:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOn.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockGarment = True

        elif self.boolLockGarment == True:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOff.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockGarment = False

    def lockPattern(self, layer, button):

        """ !@Brief
        Set the pattern meshes to reference
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the lock button for pattern meshes
        """
        pm.select(cl=True)

        if self.boolLockPattern == False:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOn.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockPattern = True

        elif self.boolLockPattern == True:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOff.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockPattern = False

    def lockRetopo(self, layer, button):
        """ !@Brief
        Set the Retopo mesh group to reference
        @param layerName: str, this is the name of the layer
        @param button: QPushButton, this is the lock button for Retopo meshes
        """
        pm.select(cl=True)

        if self.boolLockRetopo == False:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOn.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockRetopo = True

        elif self.boolLockRetopo == True:
            pm.mel.layerEditorLayerButtonTypeChange(layer)
            lockIcon = qg.QPixmap("%s/icons/lockOff.png" % folderPath)
            button.setIcon(lockIcon)
            self.boolLockRetopo = False

    def selectAllGeo(self,geoList):
        pm.select(cl=True)
        for garment in geoList:
            pm.select(garment,tgl= True)

    def get_mobject(self,node_name):

        """ !@Brief
        !@Brief Get MObject from node name.

        @type node_name: string
        @param node_name: Node you want to transform in MObject

        @rtype: OpenMaya.MObject
        @return: MObject from node name

        """

        if not isinstance(node_name, basestring):
            raise RuntimeError("Node name must be a string !!!")

        # Get PyNode in MSelectionList
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(node_name)

        maya_object = OpenMaya.MObject()
        selection_list.getDependNode(0, maya_object)

        return maya_object

    def flattenCore(self,Geo,mfn_sg,grpName):

        """ !@Brief
        Flatten a selection of garment

        @param Geo: List, list of garment nodes
        @param mfn_sg: Shading Node, Shading node to apply on flattened mesh
        @param grpName: String, name of the group which will handle the flatten geometries

        """

        dataNodeList = []

        moa_mesh = OpenMaya.MObjectArray()

        for s_node in Geo:


            #   Check input geometry
            s_shape = s_node
            if cmds.nodeType(s_node) == "transform":
                a_shapes = cmds.listRelatives(s_node, shapes=True, fullPath=True)
                if len(a_shapes) < 1:
                    logger.debug("No Shape detected for {0}".format(s_node))
                    continue
                s_shape = a_shapes[0]

            s_shape_type = cmds.nodeType(s_shape)
            if s_shape_type != "mesh":
                logger.debug("Accept only mesh not {0}".format(s_shape_type))
                continue

            # Get mesh
            mo_mesh = self.get_mobject(s_shape)
            moa_mesh.append(mo_mesh)
            mfn_dag = OpenMaya.MFnDagNode(mo_mesh)

        ### Duplicate geometry
        mdg_mod = OpenMaya.MDGModifier()
        mfn_transform = OpenMaya.MFnTransform()
        mfn_mesh = OpenMaya.MFnMesh()

        mo_root = mfn_transform.create()
        mdg_mod.renameNode(mo_root, grpName)

        for i in xrange(moa_mesh.length()):

            #   Duplicate geometry
            mfn_dep = OpenMaya.MFnDependencyNode(moa_mesh[i])
            s_short_name = mfn_dep.name().split(":")[-1].replace('Shape', '')

            mo_transform = mfn_transform.create(mo_root)
            mdg_mod.renameNode(mo_transform, "pattern_{0}".format(s_short_name))

            mo_new_mesh = mfn_mesh.copy(moa_mesh[i], mo_transform)

            findDigit = data.extract_name_nb(s_short_name)

            if findDigit[1] == None:
                mdg_mod.renameNode(mo_new_mesh, "pattern_{0}Shape".format(findDigit[0]))
            else:
                mdg_mod.renameNode(mo_new_mesh, "pattern_{0}Shape{1}".format(findDigit[0], findDigit[1]))
            mfn_sg.addMember(mo_new_mesh)

            #   Get mesh and points position in local space
            mfn_mesh = OpenMaya.MFnMesh(mo_new_mesh)
            mit_mesh_vertex = OpenMaya.MItMeshVertex(mo_new_mesh)

            mpa_point = OpenMaya.MPointArray()
            mfn_mesh.getPoints(mpa_point, OpenMaya.MSpace.kObject)

            #   Set new point position from UV space position
            mfa_u = OpenMaya.MFloatArray()
            mfa_v = OpenMaya.MFloatArray()
            mia_face_id = OpenMaya.MIntArray()

            uv_sets = list()
            getUvSets = mfn_mesh.getUVSetNames(uv_sets)

            mit_mesh_vertex.reset()
            while mit_mesh_vertex.isDone() is False:
                mit_mesh_vertex.getConnectedFaces(mia_face_id)
                try:
                    mit_mesh_vertex.getUVs(mfa_u, mfa_v, mia_face_id, uv_sets[0])
                except:
                    cm.create("""%s can't be flatten because it has an UV error. Be sure that your\n mesh has unwrapped uvs\n Check if there is no double vertices on the mesh"""%(s_short_name),
                              """Ok !""",
                              """Help on the wiki""",
                              partial(data.goToWeb, """https://bitbucket.org/Psichari/couture/wiki/Home""")
                              )
                    if pm.objExists('transform1'):
                        pm.delete("transform1")
                    return

                mp_new_pos = OpenMaya.MPoint(mfa_u[0], mfa_v[0], 0.0)
                mpa_point.set(mp_new_pos, mit_mesh_vertex.index())
                mit_mesh_vertex.next()

            mfn_mesh.setPoints(mpa_point, OpenMaya.MSpace.kObject)
            verticesPerFaceArray = OpenMaya.MIntArray()
            verticesArray = OpenMaya.MIntArray()

            mfn_mesh.getVertices(verticesPerFaceArray, verticesArray)

            mfn_mesh.unlockVertexNormals(verticesArray)
            self.patternDic["|garmentObjectsGRP|{0}".format(s_short_name)] = ["|patternObjectsGRP|pattern_{0}".format(s_short_name), "None"]
            dataNodeList.append("|patternObjectsGRP|pattern_{0}".format(s_short_name))
            s_short_name.encode('ascii', 'ignore')
            self.outliner.lineNumber["|garmentObjectsGRP|{0}".format(s_short_name)] = "two"




        mdg_mod.doIt()


    def flattenSoloGeo(self,selectedMesh):
        """ !@Brief
        This function will lauch the function flattenCore and set the resulting mesh to a proper scene scale and position
        @param selectedMesh: transformNode, this is the individual mesh that need to be flatten
        """
        mfn_sg = OpenMaya.MFnSet()
        if pm.objExists('Pattern_Shader'):
            mfn_sg.setObject(self.get_mobject("Pattern_SG"))
        else:
            shader = cs.createShadingNode("Pattern")
            mfn_sg.setObject(self.get_mobject(shader[1].longName()))
        flatten = self.flattenCore(["%s"%selectedMesh], mfn_sg,"soloPatternObjectsGRP")

        tmpFlattenGrp = pm.PyNode("soloPatternObjectsGRP")
        ### get scale and translate factor from function "flattenGeo"
        tmpFlattenGrp.setScale([1 * self.scaleFactor, 1 * self.scaleFactor, 1 * self.scaleFactor])
        tmpFlattenGrp.setTranslation([self.translateX, 0, 0])

        pm.makeIdentity(tmpFlattenGrp, apply=True, scale=True, translate=True)

        return pm.listRelatives(tmpFlattenGrp, c=True)

    def flattenGeo(self,vizButton,lockButton,selButton):

        """ !@Brief
        This function will lauch the function flattenCore and set the resulting meshes to a proper scene scale and position
        @param vizButton: QPushButton, this is the eye button for flat pattern meshes
        @param lockButton: QPushButton, this is the lock button for flat pattern meshes
        @param selButton: QPushButton, this is the selection button for flat pattern meshes

        """

        if self.boolLoadGarment == True:
            cm.create("""You have to load garments before trying to flatten them""",
                      """Ok !""",
                      None,
                      None)
            return

        if self.boolFlattenGarment == True:
            ### create a basic shader for flat pattern clothes ###

            mfn_sg = OpenMaya.MFnSet()
            if pm.objExists('Pattern_Shader'):
                mfn_sg.setObject(self.get_mobject("Pattern_SG"))
            else:
                shader = cs.createShadingNode("Pattern")
                mfn_sg.setObject(self.get_mobject(shader[1].longName()))

            ### create feedbacks to the user if the workflow is not performed properly ###
            if pm.objExists('patternObjectsGRP'):
                cm.create("""Watch out! You already flatten your garments.\n Delete your "patternObjectsGRP" if you wish to start over """,
                          "Ok, I got it !",
                          None,
                          None)
                return

            if bool(self.patternDic) == False:
                cm.create("""Wait, first you have to add your pieces of cloth in the outliner. \nUse the button "Load cloth".""",
                          "Ok, I got it !",
                          None,
                          None)
                return
            flatten = self.flattenCore(self.patternDic.keys(),mfn_sg,"patternObjectsGRP")
            pm.select(cl=True)

            if self.boolSoloGarment == False:
                geoList = [geo for geo in self.patternDic.keys()]
                pm.select(geoList,tgl =True)

                selection = pm.selected(fl=True)
                duplicatedSelection = pm.duplicate(n="tempDuplicate")
                combineBoundingBox = pm.polyUnite(n='combineBBox')
                pm.delete(constructionHistory=True)
                pm.xform(combineBoundingBox[0].longName(), cp=1)
                pm.select(cl=True)

                patternObjectsGRP = pm.PyNode("patternObjectsGRP")
                self.scaleFactor = combineBoundingBox[0].getBoundingBox(space="world").height() / patternObjectsGRP.getBoundingBox(space="world").height()
                self.dataNode.addScaleFactor(self.scaleFactor)

                patternObjectsGRP.setScale([1 * self.scaleFactor, 1 * self.scaleFactor, 1 * self.scaleFactor])
                self.translateX = combineBoundingBox[0].getRotatePivot(worldSpace=True)[0]+ combineBoundingBox[0].getBoundingBox(space="world").width() / 2
                pm.delete("combineBBox")

            else :
                geoList = [pm.PyNode(geo) for geo in self.patternDic.keys()]
                patternObjectsGRP = pm.PyNode("patternObjectsGRP")
                pm.xform(geoList[0], cp=1)
                self.scaleFactor = geoList[0].getBoundingBox(
                    space="world").height() / patternObjectsGRP.getBoundingBox(space="world").height()
                self.dataNode.addScaleFactor(self.scaleFactor)

                patternObjectsGRP.setScale([1 * self.scaleFactor, 1 * self.scaleFactor, 1 * self.scaleFactor])
                self.translateX = geoList[0].getRotatePivot(worldSpace=True)[0]+  geoList[0].getBoundingBox(space="world").width() / 2


            self.dataNode.addScaleFactor(self.scaleFactor)
            self.dataNode.addTranslateX(self.translateX)

            patternObjectsGRP.setTranslation([self.translateX, 0, 0])
            pm.makeIdentity(patternObjectsGRP, apply=True, scale=True, translate=True)

            flattenGrpChild = [str(pm.PyNode(geo).longName()) for geo in  pm.listRelatives(patternObjectsGRP, c=True)]
            pm.select(cl=True)

            ### Update the outliner with a new subLine ###
            self.outliner.updateArrowDownLine1(self.patternDic)

            pm.select(patternObjectsGRP)
            layer = pm.createDisplayLayer(nr=1, name="patternObjects_layer", number=1)

            vizButton.clicked.connect(partial(self.vizLayerPattern, "patternObjects_layer", vizButton))
            lockButton.clicked.connect(partial(self.lockPattern, "patternObjects_layer", lockButton))
            selButton.clicked.connect(partial(self.selectAllGeo,flattenGrpChild))

            pm.select(cl=True)

            self.dataNode.addPatternList(flattenGrpChild)

            self.boolFlattenGarment = False
            self.dataNode.changeBoolFlattenGarment("False")

        else:

            cm.create("""This step has already been performed, use "+" button to add new garments.""",
                      """Ok !""",
                      None,
                      None)
            return


    def exportFlatten(self):

        """ !@Brief
        This function allow user to export the flatten geometry if he wants to create a new topology in another software
        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene
        """
        if self.boolFlattenGarment == False:
            ### create feedbacks to the user if the workflow is not performed properly ###
            if not pm.objExists('patternObjectsGRP'):
                cm.create("""Wait you don't have any "patternObjectsGRP" to export.""",
                          """Ok I will use the "Flatten pattern" button""",
                          None,
                          None)
                return

            previousPath = self.dataNode.getExportPath()

            pm.select(cl= True)

            geoList = [geo[0] for geo in self.patternDic.values()]




            for piece in geoList:
                pm.select(piece,tgl=True)

            if self.mergeBool == True:
                exportDouble = pm.duplicate()
                combineExport = pm.polyUnite(n='combineExport')
                pm.delete(constructionHistory=True)

                pm.select(cl=True)

                pm.select(combineExport[0])


            ### user must pick a file location ###

            singleFilter = "*.obj;;*.fbx;;*.ma;;*.mb"
            if previousPath == "":
                selection = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Flatten objects exporter", rf=True)
            else :
                selection = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Flatten objects exporter", rf=True,dir =previousPath )
            if selection == None:
                if self.mergeBool:
                    pm.delete(combineExport[0])
                return

            exportObject = selection[0]


            ### perform the export ###

            if selection[0][-1] == "*":
                exportObject = selection[0].replace("*", "obj")

            if selection[1] == "*.obj":
                pm.exportSelected(exportObject, type='OBJexport',options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', f=True)

            elif selection[1] == "*.fbx":
                pm.exportSelected(exportObject, type='FBX export',options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', f=True)

            elif selection[1] == "*.ma":
                pm.exportSelected(exportObject, type='mayaAscii', options='v=0;', f=True)

            else:
                pm.exportSelected(exportObject, type='mayaBinary', options='v=0;', f=True)

            self.dataNode.addExportPath("/".join(exportObject.split('/')[:-1]))
            if self.mergeBool == True:
                pm.delete(combineExport[0])
        else:

            cm.create("""You must flatten the garment before exporting them""",
                      """Ok !""",
                      None,
                      None)
            return
    def GoZExport(self,folderPath):
        """ !@Brief
        This function allow user to export the flatten geometry if he wants to create a new topology in Zbrush
        @param folderPath: str, this variable give the path to Couture's folder
        """
        if self.boolFlattenGarment == False:

            ### create feedbacks to the user if the workflow is not performed properly ###


            if not pm.objExists('patternObjectsGRP'):
                cm.create("""Wait you don't have any "patternObjectsGRP" to export.""",
                          """Ok I will use the "Flatten pattern" button""",
                          None,
                          None)
                return

            geoList = [geo[0] for geo in self.patternDic.values()]
            pm.select(cl=True)

            for piece in geoList:

                pm.select(piece, tgl=True)


            if self.mergeBool == True:
                exportDouble = pm.duplicate()
                combineExport = pm.polyUnite(n='combineExport')
                pm.delete(constructionHistory=True)

                ### create a tempoary combined mesh ###

                pm.select(cl=True)
                pm.select(combineExport[0])

                pm.polyAutoProjection()


            elif self.separateBool == True:
                duplicatedPieces = pm.duplicate()
                exportGrp = pm.group(name="exportTempGrp", empty=True)
                pm.select(cl=True)
                for piece in duplicatedPieces:
                    piece.setParent(exportGrp)

                pm.select(cl=True)
                for piece in duplicatedPieces:
                    pm.select(piece, tgl=True)

            import maya.mel as mel
            try:
                mel.eval("""source "C:/Users/Public/Pixologic/GoZApps/Maya/GoZBrushFromMaya.mel" """)
            except:
                cm.create("""It seems like GoZ is not installed on your Maya\n You will have to export manually :( """,
                          "Ok, I got it !",
                          None,
                          None)

            if self.mergeBool == True:
                pm.select("combineExport*")
                pm.delete()
            elif self.separateBool == True:
                pm.delete(exportGrp)


        else:

            cm.create("""You must flatten the garment before exporting them""",
                      """Ok !""",
                      None,
                      None)
            return

    def radio1_clicked(self,*args):
        """ !@Brief
        change export status boolean attributes
        """
        self.mergeBool = True
        self.separateBool = False


    def radio2_clicked(self,*args):
        """ !@Brief
        change export status boolean attributes
        """
        self.mergeBool = False
        self.separateBool = True



    def importRetopo(self):

        """ !@Brief
        This function allow user to bring back his retopologized topology in the scene and parent it to the "retopoObjectsGRP" group
        @param self.dataNode: coutureNode, this node save the export path which might be also the place where the user export his new topology
        """


        if self.boolFlattenGarment == False:

            if self.boolDefineRetopo == True:
                if pm.objExists("retopoObjectsGRP"):
                    pm.delete("retopoObjectsGRP")

                exportPath = self.dataNode.getExportPath()


                singleFilter = "*.obj;;*.fbx;;*.ma;;*.mb"
                if exportPath == "":
                    selection = pm.fileDialog2(fm =1,fileFilter=singleFilter, dialogStyle=2, cap="Retopo objects importer", rf=True)
                else:
                    selection = pm.fileDialog2(fm =1,fileFilter=singleFilter, dialogStyle=2, cap="Retopo objects importer", rf=True,
                                               dir=exportPath)
                if selection == None:
                    return
                importedNode = pm.importFile(selection[0], i=True, returnNewNodes=True, groupReference=True,groupName="retopoObjectsGRP")

                self.retopoSetUp()
                self.boolDefineRetopo=False
                self.dataNode.changeBoolDefineRetopo("False")

            else:
                cm.create("""You already imported your retopology.""",
                          """Ok !""",
                          """Reset import""",
                          partial(self.restartRetopo, "import")
                          )
                return

        else:
            cm.create("""You must flatten the geometry before importing a retopo.""",
                      """Ok !""",
                      None,
                      None)
            return
    def restartRetopo(self,type,coutureMessage):

        if type == "select":
            saveSelection = pm.selected(fl=True)

        if pm.objExists("retopoObjectsGRP"):
            grp = pm.PyNode("retopoObjectsGRP")
            grpChildren = pm.listRelatives(grp, c=True)
            cancelGrp = pm.group(name="cancelRetopoGrp", empty=True)
            pm.hide(cancelGrp)
            for child in grpChildren:
                child.setParent(cancelGrp)
            pm.delete(grp)

        self.boolDefineRetopo = True
        self.dataNode.changeBoolDefineRetopo("True")



        self.boolPairFlatten = True
        self.dataNode.changeBoolPairFlatten("True")

        if self.boolCreateBs == False:
            for bs in self.blendNodeList:
                pm.delete(bs)
            self.blendNodeList = []
            self.boolCreateBs = True
            self.bsSlider.setValue(0)

        pm.select(cl=True)
        if self.boolCreateWrap == False:
            pm.select(cancelGrp)
            pm.delete(ch=True)
            pm.select(cl=True)
            self.boolCreateWrap = True

        self.editDic = {}

        coutureMessage.killWindow()
        if type == "select":
            pm.select(saveSelection)
            self.selectRetopo()
        else :
            self.importRetopo()

    def selectRetopo(self):

        """ !@Brief
        This function allow user to define the retopologized topo and parent it to the "retopoObjectsGRP" group
        """
        if pm.selected() == []:
            cm.create("""You have nothing selected.""",
                      """Ok !""",
                      None,
                      None)
            return
        if self.boolFlattenGarment == False:

            if self.boolDefineRetopo == True:
                selection= pm.selected(fl=True)
                pm.select(cl=True)
                retopoGrp = pm.group(name="retopoObjectsGRP", empty=True)

                for item in selection:
                    item.setParent(retopoGrp)
                self.retopoSetUp()
                self.boolDefineRetopo = False
                self.dataNode.changeBoolDefineRetopo("False")

            else:
                cm.create("""You already selected your retopology.""",
                          """Ok !""",
                          """Reset selection""",
                          partial(self.restartRetopo, "select")
                          )
                return

        else:
            cm.create("""You must flatten the geometry before importing a retopo.""",
                      """Ok !""",
                      None,
                      None)
    def retopoSetUp(self):

        """ !@Brief
        this function verify if the object provided is a mesh.
        If it's a single mesh, this mesh will be split in different mesh
        """

        grp = pm.PyNode("retopoObjectsGRP")
        grpChildren = pm.listRelatives(grp, c=True)

        geoTest = data.testGeo(grpChildren)
        for object in geoTest[1]:
            object.setParent(world=True)


        ### Separate the mesh between several meshes ###

        if len(geoTest[0]) == 1:
            try:
                separate = pm.polySeparate(grpChildren[0])
                for object in separate:
                    object.setParent(grp)
                    pm.delete(object, constructionHistory=True)


            except:
                pass

        pm.select(cl=True)
        sg = ""
        if pm.objExists('Retopo_Shader'):
            sg = pm.PyNode("Retopo_SG")
        else:
            shader = cs.createShadingNode("Retopo")
            sg = shader[1]
            pm.select(cl=True)

        grpChildren = pm.listRelatives(grp, c=True)
        self.mergeSavior(grpChildren)
        for child in grpChildren:

            pm.sets(sg, edit=1, forceElement=child)
            pm.xform(child, cp=1)


    def pairsMatching(self,vizButton,lockButton,selButton):
        """ !@Brief
        This function detect a pair between a pattern mesh and a retopologized mesh
        @param vizButton: QPushButton, this is the eye button for garment meshes
        @param lockButton: QPushButton, this is the lock button for garment meshes
        @param selectButton: QPushButton, this is the selection button for garment meshes
        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene
        """

        if self.boolDefineRetopo == False:
            if self.boolPairFlatten == True:
                dataNodeList = []
                failList = []
                failCount = {}
                flatPatternDic={}
                patternGeoList = [geo[0] for geo in self.patternDic.values()]
                flatRetopoGeos = pm.listRelatives("retopoObjectsGRP", children=True)
                if len(patternGeoList) != len(flatRetopoGeos):
                    cm.create("""Your number of pattern meshes is different from your number of retopo meshes. \nOperation can't be performed. Replace your retopo meshes.""",
                              """Ok !""",
                              None,
                              None)
                    return

                i=0

                ### Get the pivot bounding box for each pattern mesh ###
                for geo in patternGeoList:
                    try:
                        geoNode =pm.PyNode(geo)
                    except:
                        geoNode = pm.PyNode("patternObjectsGRP|"+geo)
                    pm.xform(geoNode,cp=True)
                    centerBBox = geoNode.getBoundingBox(space="world").center()
                    roundX = round(centerBBox[0], 2)
                    roundY = round(centerBBox[1], 2)

                    flatPatternDic[geoNode.longName()] = [roundX, roundY]

                ### Get the pivot bounding box for each retopo mesh, then find a pivot match from the pattern mesh ###
                flatRetopoGeos = pm.listRelatives("retopoObjectsGRP", children=True)
                for geo in flatRetopoGeos:
                    pm.xform(geo, cp=True)
                    centerBBox = geo.getBoundingBox(space="world").center()
                    roundX = round(centerBBox[0], 2)
                    roundY = round(centerBBox[1], 2)

                    for mesh, pivot in flatPatternDic.items():


                        if [roundX, roundY] == pivot:

                            pm.rename("{}".format(geo.longName()),
                                          "{}".format(data.longNameEdit("pattern", mesh, "pattern", "retopo")[1:]))


                            pm.select(mesh, geo)

                            pm.delete(ch=True)

                            pm.select(cl=True)
                            pm.select(mesh, geo)

                            self.patternDic[data.longNameEdit("pattern",mesh,"pattern","garment" )] = [str(mesh),str(geo.longName())]

                            self.outliner.lineNumber[data.longNameEdit("pattern",mesh,"pattern","garment" )] = "three"
                            logger.debug("geo name")
                            logger.debug(geo.longName())
                            i = 0



                        elif [roundX, roundY]  !=  pivot:

                            roundToleranceX = pivot[0]-roundX
                            logger.debug( " rount toleranceX %s"%roundToleranceX)
                            roundToleranceY = pivot[1] - roundY
                            logger.debug( " rount toleranceY %s"%roundToleranceY)

                            if -0.10<= roundToleranceX <= 0.10 and -0.10<= roundToleranceY <=0.10:

                                pm.rename("{}".format(geo.longName()),
                                          "{}".format(data.longNameEdit("pattern", mesh, "pattern", "retopo")[1:]))

                                pm.select(mesh, geo)

                                pm.delete(ch=True)

                                pm.select(cl=True)
                                pm.select(mesh, geo)

                                self.patternDic[data.longNameEdit("pattern", mesh, "pattern", "garment")] = [str(mesh),str(geo.longName())]

                                self.outliner.lineNumber[data.longNameEdit("pattern", mesh, "pattern", "garment")] = "three"
                                i=0

                for garment, type in self.outliner.lineNumber.items():
                    if type == "two":
                        failList.append(data.longNameEdit("garment",garment,"garment","pattern"))


                if len(failList)>0:
                    cm.create("Those pattern was not paired automaticly : \n%s"%(data.strLineReturn(self.outliner.lineNumber)), "Ok, I will do that manually",
                      None,
                      None)
                    self.boolErrorPair = True
                    self.dataNode.changeBoolErrorPair("True")

                self.outliner.updateArrowDownLine2(self.patternDic)


                for garmentName, keys in self.patternDic.items():
                    dataNodeList.append(str(keys[1]))
                self.dataNode.addRetopoList(dataNodeList)

                self.boolPairFlatten = False
                self.dataNode.changeBoolPairFlatten("False")

                grp = pm.PyNode("retopoObjectsGRP")
                pm.select(grp)
                layer = pm.createDisplayLayer(nr=1, name="retopoObjects_layer", number=1)
                vizButton.clicked.connect(partial(self.vizLayerRetopo, "retopoObjects_layer", vizButton))
                lockButton.clicked.connect(partial(self.lockRetopo, "retopoObjects_layer", lockButton))
                selButton.clicked.connect(partial(self.selectAllGeo, dataNodeList))
            else:
                cm.create("""This step has already been performed, use "+" button to add new garments.""",
                          """Ok !""",
                          None,
                          None)
                return
        else:
            cm.create("""You must import or select a retopo before this step""",
                      """Ok !""",
                      None,
                      None)
            return

        self.sortedRetopo()
    def manualPairMatching(self,objects,window):

        retopo = pm.PyNode(objects[2])
        retopo.rename(data.longNameEdit("garment",objects[0],"garment","retopo").rpartition("retopoObjectsGRP|")[2])
        retopo.setParent(pm.PyNode('retopoObjectsGRP'))
        self.patternDic[objects[0]] = [objects[1], retopo.longName()]

        self.outliner.lineNumber[objects[0]] = "three"
        self.outliner.updateArrowDownLine2(self.patternDic)
        dataNodeList = []
        for garmentName, keys in self.patternDic.items():
            dataNodeList.append(str(keys[1]))
        self.dataNode.addRetopoList(dataNodeList)
        self.sortedRetopo()
        # for keys,type in
        if data.strLineReturn(self.outliner.lineNumber) != "":
            cm.create("""Some geo must be paired if you want to continue\n%s""" % (
            data.strLineReturn(self.outliner.lineNumber)),
                      """Ok !""",
                      """Continue manual matching""",
                      window.resetWindow)
            return
        else:
            self.boolErrorPair = False
            self.dataNode.changeBoolErrorPair("False")
            window.killWindow()
            cm.create("""Everything is paired and you are ready to go ! """,
                      """Ok !""",
                      None,
                      None)


        pm.select(cl=True)

    def manualPairsMatchingWindow(self):
        if self.boolErrorPair == False:
            cm.create(
                """You have nothing to pair manually """,
                """Ok !""",
                None,
                None)
            return

        if self.boolPairFlatten == False:
            cmw.create(folderPath,self,self.dataNode)
        else:
            cm.create("""You should start with "Pairing flatten geometry" button, then if some\n pieces are not properly matched you will be allowed to use this button """,
                      """Ok !""",
                      None,
                      None)
            return

    def sortedRetopo(self):
        retopoGrp = pm.PyNode("retopoObjectsGRP")
        retopoMeshes = [pm.PyNode(item).longName() for item in pm.listRelatives(retopoGrp, c=True)]
        humanSortedRetopo = data.humanSorting(retopoMeshes)
        for mesh in humanSortedRetopo:
            retopo = pm.PyNode(mesh)
            retopo.setParent(w=True)
            retopo.setParent(retopoGrp)

    def transfertUV(self):

        """ !@Brief
        This function automaticly transfert UV between a pair of pattern mesh and and retopologized mesh
        """
        if self.boolErrorPair == True :

            cm.create("""Some geo must be paired if you want to continue\n%s"""%(data.strLineReturn(self.outliner.lineNumber)),
                      """Ok !""",
                      None,
                      None)
            return

        if self.boolPairFlatten == False:
            for garmentName,keys in self.patternDic.items():

                pm.select(keys[0])
                sourceUVset = pm.polyUVSet(query=True, allUVSets=True)
                pm.select(cl=True)

                pm.select(keys[1])
                targetUVset = pm.polyUVSet(query=True, allUVSets=True)
                pm.select(cl=True)

                pm.select(keys[0], keys[1])

                pm.transferAttributes(flipUVs=0, transferPositions=0, transferUVs=1, sourceUvSpace=sourceUVset[0],
                                      searchMethod=3, sourceUvSet=sourceUVset[0], transferNormals=0, targetUvSet=targetUVset[0],
                                      sampleSpace=0, targetUvSpace=targetUVset[0], colorBorders=1, transferColors=0)

                pm.delete(ch=True)
                pm.select(cl=True)
        else:
            cm.create("""Pattern and retopo must be paired""",
                      """Ok !""",
                      None,
                      None)
            return

    def createSoloBlendshape(self,objects):

        currentBSList = literal_eval(self.dataNode.getBsNodeList())
        pm.select(objects[0], objects[1])
        blendNode = pm.blendShape()
        pm.select(cl=True)
        self.blendNodeList.append(blendNode[0])
        currentBSList.append(str(blendNode[0].longName()))
        self.dataNode.addBsNodeList(currentBSList)

    def createMultiBlendshapes(self):
        """ !@Brief
        This function create a blendshape node between a garment and a pattern
        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene
        """

        if self.boolErrorPair == True :

            cm.create("""Some geo must be paired if you want to continue\n%s"""%(data.strLineReturn(self.outliner.lineNumber)),
                      """Ok !""",
                      None,
                      None)
            return


        if self.boolPairFlatten == False:

            if self.boolCreateBs == True:
                bsNodeName = []
                for garmentName, keys in self.patternDic.items():
                    pm.select(garmentName,keys[0])
                    blendNode = pm.blendShape()
                    pm.select(cl=True)
                    self.blendNodeList.append(blendNode[0])
                    bsNodeName.append(str(blendNode[0].longName()))

                self.dataNode.addBsNodeList(bsNodeName)

                logger.debug(self.blendNodeList)
                self.boolCreateBs = False
                self.dataNode.changeBoolCreateBs("False")

            else:
                cm.create("""Blendshapes have already been created, use "+" button to add new garments.""",
                          """Ok !""",
                          None,
                          None)
                return

        else:
            cm.create("""Pattern and retopo must be paired""",
                      """Ok !""",
                      None,
                      None)
            return
    def createSoloWrap(self,objects):

        if self.bsSlider != "":
            self.bsSlider.setValue(0)

        cw.createWrap(objects[0], objects[1])
        pm.select(cl=True)


    def createMultiWraps(self):

        """ !@Brief
        Create a wrap between a pattern and a retopo mesh

        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene
        """

        if self.boolErrorPair == True :

            cm.create("""Some geo must be paired if you want to continue\n%s"""%(data.strLineReturn(self.outliner.lineNumber)),
                      """Ok !""",
                      None,
                      None)
            return


        if self.boolCreateWrap == True:

            if self.bsSlider != "":
                self.bsSlider.setValue(0)



            # create a wrap for every keys in self.patternDic
            for garmentName, keys in self.patternDic.items():

                cw.createWrap(keys[0],keys[1])

                pm.select(cl=True)

            self.boolCreateWrap = False
            self.dataNode.changeBoolCreateWrap("False")

        else:
            cm.create("""Wraps have already been created, use "+" button to add new garments.""",
                      """Ok !""",
                      None,
                      None)
            return 

    def driveBlendnodes(self,slider,textfield,*args):


        """ !@Brief
        When the slider move, it will drive all the blendshape created by the plugin

        @param slider: QSlider, this is the slider in the blendshape panel
        @param textfield: QLineEdit, this textfield will handle the value of the slider
        """
        self.bsSlider = slider
        # fill the slider with the default value

        value = float(slider.value())
        dividedValue = value / float(100)
        textfield.setText(str(dividedValue))

        if self.blendNodeList == []:
            pass
        else:

            # update the value of the blendshape node created by the plugin

            for node in self.blendNodeList:
                bsName = node.listAliases()
                pm.setAttr("%s.%s" % (node.longName(), bsName[0][0]), dividedValue)

    def nodeBsWindow(self,folderPath):

        """ !@Brief
        Create a blendshape window that allow user to move each blendshape one by one

        @param folderPath : str, this is the path to the folder of the plugin.

        """

        if self.blendNodeList == []:
            cm.create("No blendshape created yet","Ok I got it !",
                      None,
                      None)
        else :
            cbsw.create(self.blendNodeList,folderPath)

    def softenEdgeSelected(self):

        """ !@Brief
        Perform a soften edge on the selected geo
        """

        selection = pm.selected(fl=True)

        # Check if the selected object is a geometry
        geoTest = data.testGeo(selection)

        for object in geoTest[1]:
            pass
        for object in geoTest[0]:

            pm.polyNormalPerVertex(object, ufn=True)
            pm.polySoftEdge(object, a=180, ch=1)
            pm.select(object)
            pm.mel.doBakeNonDefHistory(1, ["prePost"])
            pm.select(cl=True)
        pm.select(cl=True)

    def editSelected(self):

        """ !@Brief
        Launch an "Edit window", that allow user to edit a reopologized mesh selected
        """

        # get the selection from the user
        selection = pm.selected(fl=True)

        # manage the Edit mode shader
        sg = ""
        if pm.objExists('Edit_Mode_Shader'):
            sg = pm.PyNode("Edit_Mode_SG")
        else :
            shader = cs.createShadingNode("Edit_Mode")
            sg = shader[1]



        pm.select(cl=True)
        for item in selection:

            if not "retopo_" in item.longName():
                pass
            else:

                bsGeo = pm.PyNode(str(data.longNameEdit ("retopo",item.longName(),"retopo","pattern") ))
                blend = bsGeo.getShape().inputs(type='blendShape')
                bsOrigValue = blend[0].getWeight(0)
                if bsOrigValue < 0.5:
                    blend[0].setWeight(0, 0)
                    bsValue = 0

                elif bsOrigValue == 0.5:
                    cm.create("%s is not set to 2D or 3D space, please update the blendshape and start again"%(item.longName()), "Ok I got it !",
                              None,
                              None)
                else:
                    blend[0].setWeight(0, 1)
                    bsValue = 1
                editPiece = pm.duplicate(item.longName(),n="%s_EditMode"%(str(item.name())))
                pm.hide(item)
                pm.sets(sg, edit=1, forceElement=editPiece)

                # add the garment to a temporary edit dictionary
                self.editDic[str((item).longName())] = [str(editPiece[0].longName()),str(blend[0]),bsValue]
                pm.select(cl=True)


        #stringDic = self.editDictToString()

        self.dataNode.addEditSelectionDic(self.editDic)

    def cancelEditWindow(self):

        """ !@Brief
        Launch a "cancel edit window", that allow user to cancel his modifications
        """

        cv.create( self.editDic,"Cancel",self,"Return to edit mode")

    def cancelEdit(self,selection):

        """ !@Brief
        Get back a selection of retopo meshes from the "cancel edit window" and then stop the edit cloth mode for the selection
        the same function is used by the "cancel selected" and "cancel all" button from the "cancel edit window"

        @param selection : list of different retopo_edit meshes selected by the user.

        """


        for item in selection:

            # delete the EditMode mesh
            try:
                pm.PyNode(self.editDic[item][1]).setWeight(0, int(self.editDic[item][2]))
            except:
                pass

            itemNode = pm.PyNode(item)
            pm.showHidden(itemNode)
            pm.delete(itemNode.longName()+"_EditMode")


            # remove the canceled item from self.editDic

            self.editDic.pop(str(itemNode.longName()))



        self.dataNode.addEditSelectionDic(self.editDic)
    def applyEditWindow(self):

        """ !@Brief
        Launch an "apply edit window", that allow user to confirm his modifications
        """
        cv.create(self.editDic, "Apply", self,"Return to edit mode")

    def applyEdit(self, selection):

        """ !@Brief
        Get back a selection of retopo meshes from the "apply edit window" and then apply the modification on the meshes and connect it back to it's blendshape/wrap setup.
        the same function is used by the "apply selected" and "apply all" button from the "apply edit window"

        @param selection : list,list of different retopo_edit meshes selected by the user.

        """


        for item in selection:
            pm.PyNode(self.editDic[item][1]).setWeight(0, int(self.editDic[item][2]))
            try:
                pm.PyNode(self.editDic[item][1]).setWeight(0, int(self.editDic[item][2]))
            except:
                pass



            # delete the previous iteration and rename the edited mesh
            originalPiece = pm.PyNode(item)
            originalPieceName = originalPiece.name()



            pm.delete("|patternObjectsGRP|pattern_%s"%(originalPieceName.rpartition("retopo_")[2])+"Base")
            pm.delete(item)
            pm.rename(self.editDic[item][0], originalPieceName)

            # create a new wrap between the pattern mesh and the newly edited retopo mesh


            # set back the correct shader


            sg = ""
            if pm.objExists('Retopo_Shader'):
                sg = pm.PyNode("Retopo_SG")
            else:
                shader = cs.createShadingNode("Retopo")
                sg = shader[1]
                pm.select(cl=True)

            itemNode= pm.PyNode(item)
            pm.sets(sg, edit=1, forceElement=itemNode.longName())

            pm.select(cl=True)

            # remove the edited item from self.editDic

            self.editDic.pop(str(itemNode.longName()))

            cw.createWrap(data.longNameEdit("retopo",itemNode.longName(),"retopo","pattern"), itemNode.longName())

        self.dataNode.addEditSelectionDic(self.editDic)

    def autoload (self,garmentVizButton,garmentLockButton,garmentSelButton,patternVizButton,patternLockButton,patternSelButton,retopoVizButton,retopoLockButton,retopoSelButton,deleteButton,addButton,dicButtonToRestart):

        """ !@Brief
        Read the couture data node and start the plugin where the user stopped

        @param self.dataNode : CoutureNode, this node hold the data of the script, allow the user to reload an existing scene

        @param garmentVizButton: QPushButton, this is the view button for Garment meshes
        @param garmentLockButton: QPushButton, this is the lock button for Garment meshes
        @param garmentSelButton: QPushButton, this is the select button for Garment meshes

        @param patternVizButton: QPushButton, this is the view button for Pattern meshes
        @param patternLockButton: QPushButton, this is the lock button for Pattern meshes
        @param patternSelButton: QPushButton, this is the select button for Pattern meshes

        @param retopoVizButton: QPushButton, this is the view button for Retopo meshes
        @param retopoLockButton: QPushButton, this is the lock button for Retopo meshes
        @param retopoSelButton: QPushButton, this is the select button for Retopo meshes


        @param deleteButton: QPushButton, this button allow the user to delete a piece of cloth from the plugin
        @param addButton: QPushButton, this button allow the user to add a piece of cloth to the plugin
        """

        # use literal_val to convert a string into a list
        self.buttonToRestart = dicButtonToRestart

        self.boolLoadGarment = literal_eval(self.dataNode.getBoolLoadGarment())
        self.boolSoloGarment = literal_eval(self.dataNode.getBoolSoloGarment())
        self.boolFlattenGarment = literal_eval(self.dataNode.getBoolFlattenGarment())
        self.boolDefineRetopo = literal_eval(self.dataNode.getBoolDefineRetopo())
        self.boolPairFlatten = literal_eval(self.dataNode.getBoolPairFlatten())
        self.boolErrorPair = literal_eval(self.dataNode.getBoolErrorPair())
        self.boolCreateBs = literal_eval(self.dataNode.getBoolCreateBs())
        self.boolCreateWrap = literal_eval(self.dataNode.getBoolCreateWrap())



        # check if the garment attribute is empty, then it will connect the different buttons for the UI

        if self.dataNode.getGarmentList() != None:
            garmentList = literal_eval(self.dataNode.getGarmentList())
            garmentVizButton.clicked.connect(partial(self.vizLayerGarment, "garmentObjects_layer", garmentVizButton))
            garmentLockButton.clicked.connect(partial(self.lockGarment, "garmentObjects_layer", garmentLockButton))
            garmentSelButton.clicked.connect(partial(self.selectAllGeo, garmentList))
            addButton.clicked.connect(partial(self.addGarment))

        # check if the pattern attribute is empty, then it will connect the different buttons for the UI

        if self.dataNode.getPatternList() != None:
            patternList = literal_eval(self.dataNode.getPatternList())
            patternVizButton.clicked.connect(partial(self.vizLayerPattern, "patternObjects_layer", patternVizButton))
            patternLockButton.clicked.connect(partial(self.lockPattern, "patternObjects_layer", patternLockButton))
            patternSelButton.clicked.connect(partial(self.selectAllGeo, patternList))

        # check if the retopo attribute is empty, then it will connect the different buttons for the UI

        if self.dataNode.getRetopoList() != None:
            retopoList = literal_eval(self.dataNode.getRetopoList())
            retopoVizButton.clicked.connect(partial(self.vizLayerRetopo, "retopoObjects_layer", retopoVizButton))
            retopoLockButton.clicked.connect(partial(self.lockRetopo, "retopoObjects_layer", retopoLockButton))
            retopoSelButton.clicked.connect(partial(self.selectAllGeo, retopoList))


        # check if the blendshape node attribute is empty, then it will add the blendshape nodes to the variable self.blendNodeList
        if self.dataNode.getScaleFactor() != None:
            self.scaleFactor = literal_eval(self.dataNode.getScaleFactor())

        if self.dataNode.getTranslateX() != None:
            self.translateX = literal_eval(self.dataNode.getTranslateX())

        if self.dataNode.getBsNodeList() != None:
            self.blendNodeList =  [pm.PyNode(bs) for bs in literal_eval(self.dataNode.getBsNodeList()) ]


        # check if the wrap attribute is empty



        ### fill self.patternDic with the data collected from the coutureself.dataNode

        try :
            for index in range(len(garmentList)):
                self.patternDic[str(garmentList[index])] = ["", ""]
        except:
            pass
        try :
            for index in range(len(garmentList)):
                self.patternDic[str(garmentList[index])] = [str(patternList[index]),""]
        except:
            pass
        try :
            for index in range(len(garmentList)):
                self.patternDic[str(garmentList[index])] = [str(patternList[index]), str(retopoList[index])]
        except:
            pass

        deleteButton.clicked.connect(partial(self.applyDeleteWindow))

        # load the outliner with the garment meshes

        for item in garmentList:

            widgetLine = self.outliner.outlinerLine(pm.PyNode(item), "garment")
            self.outliner.orderWidget[item] = [widgetLine]


        self.outliner.drawLines()

        # connect the expend button on each line of the outliner

        if self.dataNode.getRetopoList() != None:
            self.outliner.updateArrowDownLine2(self.patternDic)

            for keys,items in self.patternDic.items():

                if items[1] in retopoList and items[1] != "None":
                    self.outliner.lineNumber[keys] = "three"
                else:
                    self.outliner.lineNumber[keys] = "two"


        elif self.dataNode.getPatternList() != None:
            self.outliner.updateArrowDownLine1(self.patternDic)

            for keys, items in self.patternDic.items():

                if items[0] in patternList :
                    self.outliner.lineNumber[keys] = "two"


        if self.dataNode.getEditSelectionDic() != None:
            self.editDic = literal_eval(self.dataNode.getEditSelectionDic())



    def resetCouture(self,coutureMessage):
        coutureMessage.killWindow()
        if self.boolLoadGarment == True:
            return

        from datetime import datetime
        backupPath = folderPath + "/Backup/"
        now = datetime.now()
        backupFile = "%sCoutureBackup_%s%s%s_%s%s.mb" % (backupPath,now.year, data.twoDigitStr(now.month),data.twoDigitStr(now.day), data.twoDigitStr(now.hour), data.twoDigitStr(now.minute))
        pm.renameFile(backupFile)
        pm.saveFile(f=True)

        if self.editDic != "":
            for keys, items in self.editDic.items():
                pm.delete(self.editDic[keys][0])


        meshes = []
        if self.boolLoadGarment == False and self.boolPairFlatten == True and self.boolDefineRetopo == True :
            meshes = pm.listRelatives("garmentObjectsGRP", c=True)
            for mesh in meshes:
                mesh.setParent(world=True)
            pm.delete("garmentObjectsGRP")
            pm.delete("garmentObjects_layer")
        elif self.boolLoadGarment == False and self.boolPairFlatten == False and self.boolDefineRetopo == True :
            meshes = pm.listRelatives("garmentObjectsGRP", c=True) + pm.listRelatives("patternObjectsGRP",c=True)
            renameList = pm.listRelatives("patternObjectsGRP", c=True)
            for mesh in renameList:
                mesh.rename("Old_" + mesh.name())
            for mesh in meshes:
                mesh.setParent(world=True)
            pm.delete("garmentObjectsGRP")
            pm.delete("garmentObjects_layer")
            pm.delete("patternObjectsGRP")
            pm.delete("patternObjects_layer")


        elif self.boolLoadGarment == False and self.boolPairFlatten == False and  self.boolDefineRetopo == False:
            meshes = pm.listRelatives("garmentObjectsGRP", c=True) + pm.listRelatives("patternObjectsGRP",c=True) + pm.listRelatives("retopoObjectsGRP", c=True)
            renameList = pm.listRelatives("patternObjectsGRP", c=True) + pm.listRelatives("retopoObjectsGRP", c=True)
            for mesh in renameList:
                mesh.rename("Old_" + mesh.name())
            for mesh in meshes:
                mesh.setParent(world=True)
            pm.delete("garmentObjectsGRP")
            pm.delete("garmentObjects_layer")
            pm.delete("patternObjectsGRP")
            pm.delete("patternObjects_layer")
            pm.delete("retopoObjectsGRP")
            pm.delete("retopoObjects_layer")





        # pm.newFile(f=True)
        self.dataNode.resetNode()



        self.patternDic = odict.OrderedDict()
        self.outliner.resetOutliner()
        self.boolLoadGarment = True
        self.boolSoloGarment = False
        self.boolFlattenGarment = True
        self.boolDefineRetopo = True
        self.boolPairFlatten = True
        self.boolErrorPair = False
        self.boolCreateBs = True
        self.boolCreateWrap = True

        self.scaleFactor = 0
        self.translateX = 0

        self.blendNodeList = []

        ### set the export style format
        self.mergeBool = True
        self.separateBool = False

        ### store the currently edited meshes
        self.editDic = {}

        ### store the states of visibility and lock attributes
        self.boolLockGarment = False
        self.boolVizGarment = True
        self.boolLockPattern = False
        self.boolVizPattern = True
        self.boolLockRetopo = False
        self.boolVizRetopo = True

        ### Data storage for adding individual piece of new cloth
        self.soloGarment = []
        self.soloPattern = []
        self.soloRetopo = []


        for button in self.buttonToRestart:
            try:
                button.clicked.disconnect()
            except:
                pass


        cm.create("""Back up file saved in the folder: \n %s"""%backupPath,
                  """ OK """,
                  """Show file in folder""",
                  partial(self.revealFile, backupFile))
        return

    def revealFile(self,path,coutureMessage):
        newPath = path.replace("/","\\")
        import subprocess
        subprocess.Popen('explorer /select,  "%s"'%(newPath))


    def resetCoutureWindow(self):
        cm.create("""You're about to restart Couture, are you sure ? UNDOABLE ACTION !!!""",
                  """Cancel !""",
                  """Yes, reset it ! """,
                  partial(self.resetCouture))
        return

    def openAboutWindow(self):

        cAboutWindow.create(folderPath,self)
