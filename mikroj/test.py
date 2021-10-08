from abc import abstractmethod
import abc
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QRect, Qt, pyqtSignal
import imagej
import os
import logging
import pydantic

from pydantic.main import BaseModel
from arkitekt.messages.base import T
from herre.utils import wait_for_post, wait_for_redirect
from koil.loop import koil
from konfik.grants.qtbeacon import QtSelectableBeaconGrant
from konfik.grants.yaml import YamlGrant
from konfik.konfik import Konfik
from mikro import Representation
import scyjava
import numpy as np
from mikroj.helper import ImageJHelper
import xarray as xr
import typing
from herre import Herre
from arkitekt.agents.qt import QtAgent
from mikro.widgets import MY_TOP_REPRESENTATIONS
from mikroj.ui.provisions import ProvisionsWidget
packaged = False
import asyncio
import aiohttp
import json
from urllib.parse import quote

from socket import socket, AF_INET, SOCK_DGRAM

if packaged:
    os.environ['JAVA_HOME'] = os.path.join(os.getcwd(), 'share\\jdk8')
    os.environ['PATH'] = os.path.join(os.getcwd(), 'share\\mvn\\bin') + os.pathsep + os.environ['PATH']


class ImageJRunner(QObject):
    init_signal = QtCore.pyqtSignal(str)


    def __init__(self, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)
        self.helper = None

    def run_it(self):
        # I'm guessing this is an infinite while loop that monitors files
        self.helper = ImageJHelper()
        self.init_signal.emit('yes')



class ArkitektPopup(QtWidgets.QWidget):
    def __init__(self, arWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arWidget = arWidget

        self.layout = QtWidgets.QVBoxLayout()

        self.delete_konfig = QtWidgets.QPushButton("Delete Konfig")
        self.delete_konfig.clicked.connect(self.konfig_delete)

        self.logout_button = QtWidgets.QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout_pressed)

        self.layout.addWidget(self.delete_konfig)
        self.layout.addWidget(self.logout_button)
        self.setLayout(self.layout)

    def konfig_delete(self):
        self.arWidget.konfik.delete()


    def logout_pressed(self):
        self.arWidget.herre.logout()




class ArkitektWidget(QtWidgets.QWidget):

    def __init__(self, helper, *args, config_path=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.file_grant = YamlGrant("querk.yaml")
        self.beacon_grant = QtSelectableBeaconGrant()

        self.konfik = Konfik(grants=[self.file_grant, self.beacon_grant], save_conf="querk.yaml")

        self.herre = Herre()
        self.agent = QtAgent(self)

        self.layout = QtWidgets.QVBoxLayout()

        self.button_layout = QtWidgets.QHBoxLayout()
        self.buttons = QtWidgets.QWidget()
        self.buttons.setLayout(self.button_layout)

        self.gear_button = QtWidgets.QToolButton()
        self.gear_button.setIcon(QtGui.QIcon("gear.png"))
        self.gear_button.clicked.connect(self.gear_button_clicked)


        self.magic_button = QtWidgets.QPushButton("Connect")
        self.magic_button.clicked.connect(self.magic_button_clicked)

        
        self.button_layout.addWidget(self.magic_button)
        self.button_layout.addWidget(self.gear_button)


        self.gear_button_popup = ArkitektPopup(self)

        self.magic_button.setIcon(QtGui.QIcon())
        self.start_button_movie = QtGui.QMovie("pink pulse.gif")
        self.start_button_movie.frameChanged.connect(self.update_start_button_movie)
        self.start_button_movie.start()
        self.agent_task = None
        self.load_konfig_task = None

        self.provisision_widget = ProvisionsWidget(self.agent)
        self.layout.addWidget(self.provisision_widget)

        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)


    def gear_button_clicked(self):
        self.gear_button_popup.show()
        

    def logout(self):
        assert self.herre.logged_in, "This error should not happen"
        if self.agent_task: self.agent_task.cancel()
        self.herre.logout()
        
        self.magic_button.setText("Reconnect")
        self.magic_button.setIcon(QtGui.QIcon())
        self.start_button_movie = QtGui.QMovie("pink pulse.gif")
        self.start_button_movie.frameChanged.connect(self.update_start_button_movie)
        self.start_button_movie.start()



    def magic_button_clicked(self):
        if not self.konfik.loaded:
            print("Loading Konfig")
            if self.load_konfig_task: return None
            self.load_konfig_task = self.konfik.load(as_task=True)
            return 

        if not self.herre.logged_in:
            self.herre.login()
            self.start_button_movie = QtGui.QMovie("green pulse.gif")
            self.magic_button.setIcon(QtGui.QIcon(self.start_button_movie.currentPixmap()))
            self.magic_button.setText("Connected!")

        if not self.agent_task:
            self.agent_task = self.agent.provide(as_task=True)
            self.start_button_movie = QtGui.QMovie("green pulse.gif")
            self.magic_button.setIcon(QtGui.QIcon(self.start_button_movie.currentPixmap()))
            self.magic_button.setText("Providing...")
            self.start_button_movie.frameChanged.connect(self.update_start_button_movie)
            self.start_button_movie.start()
        
        else:
            self.agent_task.cancel()
            self.agent_task = None
            self.magic_button.setText("Halted")
            self.magic_button.setIcon(QtGui.QIcon())
            self.start_button_movie = QtGui.QMovie("pink pulse.gif")
            self.start_button_movie.frameChanged.connect(self.update_start_button_movie)
            self.start_button_movie.start()


        





    def update_start_button_movie(self):
        self.magic_button.setIcon(QtGui.QIcon(self.start_button_movie.currentPixmap()))


def show_image(rep: Representation):
    """Shows an Image

    Shows a Representation on Imagej

    Args:
        rep (Representation): [description]
    """




class MikroJ(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        #self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))


        self.runner = ImageJRunner()
        self.arkitektWidget = ArkitektWidget(self.runner.helper, **kwargs)

        self.agent = self.arkitektWidget.agent

        self.showActor = self.agent.register(show_image, widgets={"rep": MY_TOP_REPRESENTATIONS})
        self.showActor.signals.assigns.connect(self.show_image_assign)

        self.thread = QtCore.QThread(self)
        self.runner.init_signal.connect(self.imagej_done)
        self.layout = QtWidgets.QHBoxLayout()
        self.runner.moveToThread(self.thread)
        self.thread.started.connect(self.runner.run_it)
        self.thread.start()
        self.arkitektWidget.magic_button.setDisabled(True)
        self.setCentralWidget(self.arkitektWidget)
        self.init_ui() 

    def show_image_assign(self, res, rep):
        self.runner.helper.displayRep(rep)
        self.showActor.signals.returns.emit(res, None)
        
    def imagej_done(self, str):
        #self.arkitektWidget.start_button.setDisabled(False)
        #self.arkitektWidget.start_button.setText("Assign")
        self.arkitektWidget.magic_button.setDisabled(False)

    def init_ui(self):
        self.setWindowTitle('MikroJ')
        self.show()

def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    #app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()