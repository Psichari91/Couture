from vendor.qtpy.Qt import QtWidgets
from vendor.qtpy.Qt import QtCore as qc
from vendor.qtpy.Qt import QtGui as qg
import pymel.core as pm
from functools import partial
import os

from Utils import Data as dt
reload (dt)
from Utils import odict as odict
reload (odict)
folderPath = os.path.split(__file__)[0].rpartition("\Couture")[0]+"/Couture"


class outliner():
    def __init__(self , layout):
        self.layout = layout
        self.orderWidget = odict.OrderedDict()
        self.displayedWidget = []
        self.arrowButtonList = {}
        self.lineNumber = {}


    def drawLines(self):

        row = 0
        try:
            for widget in (range(len( self.displayedWidget))):

                self.layout.removeWidget(self.displayedWidget[row])
                row +=1
        except:
            pass

        self.displayedWidget = []
        number = 0
        for key, value in self.orderWidget.items():

            try:
                self.layout.addWidget(value[0],number,0)
            except:
                pass
            number +=1
            self.displayedWidget.append(value[0])

    def favEdit(self, itemName, itemWidget):
        if self.lineNumber[itemName] == "one":

            #Test if the widget is already a favorite
            firstWidget =[elem[0] for elem in self.orderWidget.values()]
            if itemWidget == firstWidget[0]:
                return
            self.orderWidget.insert(0, itemName,[itemWidget])
            self.drawLines()

        elif self.lineNumber[itemName] == "two":
            # Test if the widget is already a favorite
            firstWidget = [elem[0] for elem in self.orderWidget.values()]
            if itemWidget == firstWidget[0]:
                return
            try:
                self.orderWidget.insert(0, itemName ,[itemWidget])
                self.orderWidget.insert(1, dt.longNameEdit("garment",itemName,"garment","pattern"), self.orderWidget[dt.longNameEdit("garment",itemName,"garment","pattern")])
            except:
                self.orderWidget.insert(0, itemName, [itemWidget])

            self.drawLines()

        elif self.lineNumber[itemName] == "three":
            # Test if the widget is already a favorite
            firstWidget = [elem[0] for elem in self.orderWidget.values()]
            if itemWidget == firstWidget[0]:
                return


            try:
                self.orderWidget.insert(0, itemName, [itemWidget])
                self.orderWidget.insert(1,dt.longNameEdit("garment",itemName,"garment","pattern"), self.orderWidget[dt.longNameEdit("garment",itemName,"garment","pattern")])
                self.orderWidget.insert(2,dt.longNameEdit("garment",itemName,"garment","retopo"), self.orderWidget[dt.longNameEdit("garment",itemName,"garment","retopo")])
            except:
                self.orderWidget.insert(0, itemName, [itemWidget])

            self.drawLines()


    def viewFit(self, item):
        pm.select(cl=True)
        pm.select(item)
        pm.viewFit()

    def outlinerLine(self, item, lineType):
        itemQVFrame = QtWidgets.QWidget()
        itemQVFrame.setContentsMargins(0,0,0,0)
        if lineType == "pattern":
            itemQVFrame.setStyleSheet("background-color: rgb(76, 98, 107)")

        elif lineType == "pattern_end":
            itemQVFrame.setStyleSheet("background-color: rgb(76, 98, 107)")

        elif lineType == "retopo":
            itemQVFrame.setStyleSheet("background-color: rgb(113, 145, 158)")

        itemQVFrame.setLayout(QtWidgets.QVBoxLayout())
        itemQVFrame.setContentsMargins(-5, -5, -5, -5)
        itemQHFrame = QtWidgets.QFrame()




        if lineType == "garment":

            itemSpacer = QtWidgets.QFrame()
            itemSpacer.setFrameStyle(QtWidgets.QFrame.HLine)
            itemQVFrame.layout().addWidget(itemSpacer)

            main_color = 'rgba( 150, 150,  150, 255)'
            shadow_color = 'rgba( 45,  45,  45, 255)'
            bottom_border = 'border-bottom:1px solid %s;' % shadow_color

            style_sheet = "border:0px solid rgba(0,0,0,0); \
                                                   background-color:%s; \
                                                   max-height:1px; \
                                                   %s;" % (main_color, bottom_border)
            itemSpacer.setStyleSheet(style_sheet)

        itemQVFrame.layout().addWidget(itemQHFrame)
        itemQHFrame.setLayout(QtWidgets.QHBoxLayout())

        if lineType == "garment":

            selIconOff = "%s/icons/TshirtOff.png" % folderPath
            selIconHover = "%s/icons/TshirtHover.png" % folderPath
            selIconOn = "%s/icons/TshirtOn.png" % folderPath

        elif lineType == "pattern":

            selIconOff = "%s/icons/patternOff.png" % folderPath
            selIconHover = "%s/icons/patternHover.png" % folderPath
            selIconOn = "%s/icons/patternOn.png" % folderPath

        elif lineType == "pattern_end":

            selIconOff = "%s/icons/patternOff.png" % folderPath
            selIconHover = "%s/icons/patternHover.png" % folderPath
            selIconOn = "%s/icons/patternOn.png" % folderPath

        elif lineType == "retopo":

            selIconOff = "%s/icons/retopoOff.png" % folderPath
            selIconHover = "%s/icons/retopoHover.png" % folderPath
            selIconOn = "%s/icons/retopoOn.png" % folderPath

        selButton = QtWidgets.QPushButton()
        selButton.setFixedWidth(25)
        selButton.setStyleSheet("""QPushButton {qproperty-icon: url(" ");\
                                                        border: 0px;\
                                                        qproperty-iconSize: 25px 25px;\
                                                        background-image: url("%s");\
                                                        background-repeat: no-repeat;}\
                                                        QPushButton:hover {background-image: url("%s");\
                                                        background-repeat: no-repeat;}\
                                                        QPushButton:pressed {background-image: url("%s");
                                                        background-repeat: no-repeat;}""" % (
        selIconOff, selIconHover, selIconOn))

        if lineType == "garment":

            self.arrowToggleIconOff = "%s/icons/outlinerArrowsToggleOff.png" % folderPath
            self.arrowToggleIconHover = "%s/icons/outlinerArrowsToggleHover.png" % folderPath
            self.arrowToggleIconOn = "%s/icons/outlinerArrowsToggleOn.png" % folderPath


        elif lineType == "pattern":

            self.arrowToggleIconOff = "%s/icons/outlinerMiddleArrows.png" % folderPath
            self.arrowToggleIconHover = "%s/icons/outlinerMiddleArrows.png" % folderPath
            self.arrowToggleIconOn = "%s/icons/outlinerMiddleArrows.png" % folderPath

        elif lineType == "pattern_end":

            self.arrowToggleIconOff = "%s/icons/outlinerDownArrowsToggleOn.png" % folderPath
            self.arrowToggleIconHover = "%s/icons/outlinerDownArrowsToggleHover.png" % folderPath
            self.arrowToggleIconOn = "%s/icons/outlinerDownArrowsToggleOff.png" % folderPath

        elif lineType == "retopo":

            self.arrowToggleIconOff = "%s/icons/outlinerDownArrowsToggleOn.png" % folderPath
            self.arrowToggleIconHover = "%s/icons/outlinerDownArrowsToggleHover.png" % folderPath
            self.arrowToggleIconOn = "%s/icons/outlinerDownArrowsToggleOff.png" % folderPath

        self.buttonArrowToggle = QtWidgets.QPushButton()
        self.buttonArrowToggle.setFixedWidth(25)
        self.buttonArrowToggle.setStyleSheet("""QPushButton {qproperty-icon: url(" ");\
                                                border: 0px;\
                                                qproperty-iconSize: 25px 25px;\
                                                background-image: url("%s");\
                                                background-repeat: no-repeat;}\
                                                QPushButton:hover {background-image: url("%s");\
                                                background-repeat: no-repeat;}\
                                                QPushButton:pressed {background-image: url("%s");
                                                background-repeat: no-repeat;}""" % (
        self.arrowToggleIconOff, self.arrowToggleIconHover, self.arrowToggleIconOn))

        zoomIconOff = "%s/icons/zoomOff.png" % folderPath
        zoomIconHover = "%s/icons/zoomHover.png" % folderPath
        zoomIconOn = "%s/icons/zoomOn.png" % folderPath

        zoomButton = QtWidgets.QPushButton()
        zoomButton.setFixedWidth(25)
        zoomButton.setStyleSheet("""QPushButton {qproperty-icon: url(" ");\
                                                    border: 0px;\
                                                    qproperty-iconSize: 25px 25px;\
                                                    background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:hover {background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:pressed {background-image: url("%s");
                                                    background-repeat: no-repeat;}""" % (
        zoomIconOff, zoomIconHover, zoomIconOn))

        if lineType == "garment":
            starIconOff = "%s/icons/starOff.png" % folderPath
            starIconHover = "%s/icons/starHover.png" % folderPath
            starIconOn = "%s/icons/starOn.png" % folderPath

            starButton = QtWidgets.QPushButton()
            starButton.setFixedWidth(25)
            starButton.setStyleSheet("""QPushButton {qproperty-icon: url(" ");\
                                                            border: 0px;\
                                                            qproperty-iconSize: 25px 25px;\
                                                            background-image: url("%s");\
                                                            background-repeat: no-repeat;}\
                                                            QPushButton:hover {background-image: url("%s");\
                                                            background-repeat: no-repeat;}\
                                                            QPushButton:pressed {background-image: url("%s");
                                                            background-repeat: no-repeat;}""" % (
            starIconOff, starIconHover, starIconOn))

        itemName = QtWidgets.QLabel(item.name())
        itemFav = QtWidgets.QPushButton("FAV")

        itemQHFrame.layout().setSpacing(5)
        itemQHFrame.setContentsMargins(-8, -8, -8, -8)

        itemQHFrame.layout().addWidget(selButton)
        itemQHFrame.layout().addWidget(self.buttonArrowToggle)
        itemQHFrame.layout().addWidget(itemName)
        itemQHFrame.layout().addWidget(zoomButton)
        if lineType == "garment":
            itemQHFrame.layout().addWidget(starButton)

        selButton.clicked.connect(partial(pm.select, item.name(), tgl=True))
        zoomButton.clicked.connect(partial(self.viewFit,item.name()))
        if lineType == "garment":
            starButton.clicked.connect(partial(self.favEdit,  item.longName(), itemQVFrame))
        self.arrowButtonList[str(item.longName())] = [self.buttonArrowToggle,self.arrowToggleIconOff,self.arrowToggleIconHover,self.arrowToggleIconOn]

        self.lineNumber[str(item.longName())] = "one"
        return itemQVFrame

    def updateArrowDownLine1(self,dictUpdate) :
        for k,v in dictUpdate.items():

            try:
                self.arrowButtonList[k][0].clicked.disconnect()
            except:
                pass

            self.arrowButtonList[k][0].clicked.connect(partial(self.clickedArrowDownLine1,k,v[0],v[1],self.arrowButtonList[k][0]))


    def updateArrowDownLine2(self,dictUpdate) :

        for k,v in dictUpdate.items():

            if v[1] != "":

                try:
                    self.arrowButtonList[k][0].clicked.disconnect()
                except:
                    pass

                self.arrowButtonList[k][0].clicked.connect(partial(self.clickedArrowDownLine2,k,v[0],v[1],self.arrowButtonList[k][0]))
            else:

                pass

    def clickedArrowDownLine1(self,patternName,value1,value2,parentArrow):

        i = 0
        keys = self.orderWidget.keys()
        for key in self.orderWidget.keys():

            if key == patternName:

                line = self.outlinerLine(pm.PyNode(value1), "pattern_end")
                self.orderWidget.insert(i+1, value1, [line])
                self.arrowButtonList[keys[i]][0].setStyleSheet("""
                                            QPushButton {qproperty-icon: url(" ");\
                                                    border: 0px;\
                                                    qproperty-iconSize: 25px 25px;\
                                                    background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:hover {background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:pressed {background-image: url("%s");
                                                    background-repeat: no-repeat;}""" % (
                    self.arrowButtonList[keys[i]][3], self.arrowButtonList[keys[i]][2], self.arrowButtonList[keys[i]][1]) )
                self.drawLines()

                self.arrowButtonList[value1][0].clicked.connect(partial(self.expendOff,patternName, value1,"",parentArrow))
                parentArrow.clicked.disconnect()



                break;

            else:
                i += 1



    def clickedArrowDownLine2(self,patternName,value1,value2,parentArrow):
        i = 0
        keys = self.orderWidget.keys()
        for key in keys:
            if key == patternName:
                self.arrowButtonList[keys[i]][0].setStyleSheet("""QPushButton {qproperty-icon: url(" ");\
                                                    border: 0px;\
                                                    qproperty-iconSize: 25px 25px;\
                                                    background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:hover {background-image: url("%s");\
                                                    background-repeat: no-repeat;}\
                                                    QPushButton:pressed {background-image: url("%s");
                                                    background-repeat: no-repeat;}""" % (
                    self.arrowButtonList[keys[i]][3], self.arrowButtonList[keys[i]][2], self.arrowButtonList[keys[i]][1]))

                line1 = self.outlinerLine(pm.PyNode(value1), "pattern")
                self.orderWidget.insert(i + 1, value1, [line1])

                line2 = self.outlinerLine(pm.PyNode(value2), "retopo")
                self.orderWidget.insert(i + 2, value2, [line2])


                self.drawLines()

                self.arrowButtonList[value2][0].clicked.connect(partial(self.expendOff,patternName, value1, value2,parentArrow))
                parentArrow.clicked.disconnect()



                break;

            else:
                i += 1


    def expendOff(self,patternName,keyName,keyName2,parentArrow):

        if keyName2 == "":
            i=0
            keys = self.orderWidget.keys()
            for key in keys:

                if key == keyName:

                    self.orderWidget[key][0].deleteLater()
                    self.orderWidget.popitem(i)

                    self.arrowButtonList[keys[i-1]][0].setStyleSheet("""
                                                                                    QPushButton {qproperty-icon: url(" ");\
                                                                                            border: 0px;\
                                                                                            qproperty-iconSize: 25px 25px;\
                                                                                            background-image: url("%s");\
                                                                                            background-repeat: no-repeat;}\
                                                                                            QPushButton:hover {background-image: url("%s");\
                                                                                            background-repeat: no-repeat;}\
                                                                                            QPushButton:pressed {background-image: url("%s");
                                                                                            background-repeat: no-repeat;}""" % (
                        self.arrowButtonList[keys[i-1]][1], self.arrowButtonList[keys[i-1]][2],
                        self.arrowButtonList[keys[i-1]][3]))
                    parentArrow.clicked.connect(partial(self.clickedArrowDownLine1,patternName, keyName,keyName2,parentArrow))
                    self.drawLines()

                    break;

                else:
                    i+=1
        else:
            i = 0
            keys = self.orderWidget.keys()
            for key in keys:

                if key == keyName2:



                    self.arrowButtonList[keys[i - 2]][0].setStyleSheet("""
                                                                                                                    QPushButton {qproperty-icon: url(" ");\
                                                                                                                            border: 0px;\
                                                                                                                            qproperty-iconSize: 25px 25px;\
                                                                                                                            background-image: url("%s");\
                                                                                                                            background-repeat: no-repeat;}\
                                                                                                                            QPushButton:hover {background-image: url("%s");\
                                                                                                                            background-repeat: no-repeat;}\
                                                                                                                            QPushButton:pressed {background-image: url("%s");
                                                                                                                            background-repeat: no-repeat;}""" % (
                        self.arrowButtonList[keys[i - 2]][1], self.arrowButtonList[keys[i - 2]][2],self.arrowButtonList[keys[i - 2]][3]))

                    self.orderWidget[keyName2][0].deleteLater()


                    del self.orderWidget[keyName2]

                    self.orderWidget[keyName][0].deleteLater()

                    del self.orderWidget[keyName]

                    parentArrow.clicked.connect(partial(self.clickedArrowDownLine2,patternName, keyName,keyName2,parentArrow))


                    self.drawLines()
                    break;

                else:
                    i += 1
    def resetOutliner(self):

        for value in self.orderWidget.values():
            value[0].deleteLater()
        self.orderWidget = odict.OrderedDict()
        self.lineNumber = {}