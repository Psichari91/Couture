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
    def __init__(self, folderPath, coutureCore):

        QtWidgets.QDialog.__init__(self)

        self.coutureCore = coutureCore

        self.setStyleSheet("background-color: rgb(42, 54, 59)")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("About Couture")
        self.setFixedHeight(750)
        self.setFixedWidth(600)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(10, 15, 10, 15)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.verticalLayout = QtWidgets.QVBoxLayout()

        about_widget = QtWidgets.QWidget()
        about_widget.setLayout(self.verticalLayout)

        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setAlignment(qc.Qt.AlignCenter)
        self.logo_pix = qg.QPixmap("%s/icons/coutureLogo.png" % folderPath)
        self.logo_label.setPixmap(self.logo_pix)

        self.version_label = QtWidgets.QLabel("Version: Couture 1.01")
        self.version_label.setAlignment(qc.Qt.AlignCenter)

        self.verticalLayout.addWidget(self.logo_label)
        self.verticalLayout.addWidget(self.version_label)

        self.introFrame = QtWidgets.QFrame()
        self.introFrame.setLayout(QtWidgets.QHBoxLayout())

        self.photo_label = QtWidgets.QLabel()
        self.photo_label.setAlignment(qc.Qt.AlignCenter)
        self.photo_pix = qg.QPixmap("%s/icons/photo.png" % folderPath)
        self.photo_label.setPixmap(self.photo_pix)

        self.intro_label = QtWidgets.QLabel("Hi, I'm Florian Croquet, creator of Couture.\n I would like to thank you for downloading and\n using this tool.\n Feel free to contact me if you encountered a \n bug, if you have an idea about Couture or if\nyou are happy to use Couture ! \n florian_croquet@hotmail.com \n \nYou can also follow me on several social networks. ")
        self.intro_label.setAlignment(qc.Qt.AlignAbsolute)

        self.introFrame.layout().addWidget(self.photo_label)
        self.introFrame.layout().addWidget(self.intro_label)
        self.verticalLayout.addWidget(self.introFrame)

        self.webLogoFrame = QtWidgets.QFrame()
        self.webLogoFrame.setLayout(QtWidgets.QHBoxLayout())

        self.twitterIcon = qg.QPixmap("%s/icons/twitter.png" % folderPath)
        self.twitterButton = QtWidgets.QPushButton()
        self.twitterButton.setIcon(self.twitterIcon)
        self.twitterButton.setIconSize(qc.QSize(103, 103))
        self.twitterButton.setMinimumHeight(100)
        self.twitterButton.setStyleSheet("border: none;")

        self.linkedinIcon = qg.QPixmap("%s/icons/linkedin.png" % folderPath)
        self.linkedinButton = QtWidgets.QPushButton()
        self.linkedinButton.setIcon(self.linkedinIcon)
        self.linkedinButton.setIconSize(qc.QSize(103, 103))
        self.linkedinButton.setMinimumHeight(100)
        self.linkedinButton.setStyleSheet("border: none;")


        self.artstationIcon = qg.QPixmap("%s/icons/artstation.png" % folderPath)
        self.artstationButton = QtWidgets.QPushButton()
        self.artstationButton.setIcon(self.artstationIcon)
        self.artstationButton.setIconSize(qc.QSize(103, 103))
        self.artstationButton.setMinimumHeight(100)
        self.artstationButton.setStyleSheet("border: none;")


        self.instagramIcon = qg.QPixmap("%s/icons/instagram.png" % folderPath)
        self.instagramButton = QtWidgets.QPushButton()
        self.instagramButton.setIcon(self.instagramIcon)
        self.instagramButton.setIconSize(qc.QSize(103, 103))
        self.instagramButton.setMinimumHeight(100)
        self.instagramButton.setStyleSheet("border: none;")


        self.vimeoIcon = qg.QPixmap("%s/icons/vimeo.png" % folderPath)
        self.vimeoButton = QtWidgets.QPushButton()
        self.vimeoButton.setIcon(self.vimeoIcon)
        self.vimeoButton.setIconSize(qc.QSize(103, 103))
        self.vimeoButton.setMinimumHeight(100)
        self.vimeoButton.setStyleSheet("border: none;")


        self.webLogoFrame.layout().addWidget(self.artstationButton)
        self.webLogoFrame.layout().addWidget(self.twitterButton)
        self.webLogoFrame.layout().addWidget(self.instagramButton)
        self.webLogoFrame.layout().addWidget(self.linkedinButton)
        self.webLogoFrame.layout().addWidget(self.vimeoButton)
        self.artstationButton.clicked.connect(partial(data.goToWeb,'https://www.artstation.com/psichari',None))
        self.twitterButton.clicked.connect(partial(data.goToWeb,'https://twitter.com/floriancroquet',None))
        self.instagramButton.clicked.connect(partial(data.goToWeb,'https://www.instagram.com/psichari/',None))
        self.linkedinButton.clicked.connect(partial(data.goToWeb,'https://www.linkedin.com/in/floriancroquet/',None))
        self.vimeoButton.clicked.connect(partial(data.goToWeb,'https://vimeo.com/abitbol',None))
        self.verticalLayout.addWidget(self.webLogoFrame)

        self.licence_label = QtWidgets.QLabel("Couture is distributed under Creative Commons licence:\n Attribution-ShareAlike 4.0 International\n (CC BY-SA 4.0)")
        self.licence_label.setAlignment(qc.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.licence_label)

        self.CC_pix = qg.QPixmap("%s/icons/CC.png" % folderPath)
        self.CCButton = QtWidgets.QPushButton()
        self.CCButton.setIcon(self.CC_pix)
        self.CCButton.setIconSize(qc.QSize(400, 141))
        self.CCButton.setMinimumHeight(141)
        self.CCButton.setStyleSheet("border: none;")

        self.CCButton.clicked.connect(partial(data.goToWeb,'https://creativecommons.org/licenses/by-sa/4.0/',None))
        self.verticalLayout.addWidget(self.CCButton)


        self.layout().addWidget(about_widget)



    def closeEvent(self, event):
        delete()

    def killWindow(self):
        delete()


def create(folderPath, coutureCore):
    global dialog
    if dialog is None:
        dialog = manualPairingWindow(folderPath, coutureCore)
    dialog.show()
    return dialog


def delete():
    global dialog
    if dialog is None:
        return

    dialog.deleteLater()
    dialog = None
