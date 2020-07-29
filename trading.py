# python system trading program using PyQt
# author : youngpark-POS

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic

ui_form = uic.loadUiType("main_window.ui")[0]


class MyWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.pushButton.clicked.connect(self.login)
        self.pushButton2.clicked.connect(self.check_status)
        '''
        when I click pushButton(login button), 
        the program finishes with exit code 0xC0000409.
        why this happens?
        '''

    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.event_connect)

    def check_status(self):
        if self.kiwoom.dynamicCall("GetConnectedState()") == 0:
            self.statusBar().showMessage("Not Connected")
        else:
            self.statusBar().showMessage("Connected")

    def event_connect(self, errcode):
        if errcode == 0:
            self.statusBar().showMessage("OK")
        elif errcode == -100:
            self.statusBar().showMessage("User information exchange failed")
        elif errcode == -101:
            self.statusBar().showMessage("Server access failed")
        elif errcode == -102:
            self.statusBar().showMessage("Version progress failed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
