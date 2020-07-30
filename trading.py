# python system trading program using PyQt
# Reference : https://cafe.naver.com/autotradestudy, https://wikidocs.net/book/110
# author : youngpark-POS

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
import sqlite3

ui_form = uic.loadUiType("main_window.ui")[0]


class MyWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.pushButton.clicked.connect(self.login)
        self.pushButton2.clicked.connect(self.check_status)
        self.items = {}

    def setupUI(self):
        self.setupUi(self)

        columns = ["00: 지정가", "03: 시장가", "05: 조건부지정가", "06: 최유리지정가", "07: 최우선지정가",
                   "10: 지정가IOC", "13: 시장가IOC", "16: 최유리IOC", "17: 최우선IOC", "20: 지정가FOK",
                   "23: 시장가FOK", "26: 최유리FOK", "61: 장전시간외종가", "62: 시간외단일기매매", "81: 장후시간외종가"]
        self.typeBox.addItems(columns)
        columns = ["매수", "매도", "매수정정", "매도정정"]
        self.tradeType.addItems(columns)

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
            self.get_login_info()
            self.pushButton.hide()
            self.pushButton2.hide()
            self.get_items(0, 10)
        elif errcode == -100:
            self.statusBar().showMessage("User information exchange failed")
        elif errcode == -101:
            self.statusBar().showMessage("Server access failed")
        elif errcode == -102:
            self.statusBar().showMessage("Version progress failed")

    def get_login_info(self):
        accCnt = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCOUNT_CNT")
        accList = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCLIST").split(';')
        del accList[-1]
        userid = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "USER_ID")
        userName = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        ketSec = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "KEY_BSECGB")
        firewall = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "FIREW_SECGB")
        servertype = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "GetSurverGubun")

        if servertype == "1":
            servertype = "Practice"
        else:
            servertype = "Real"
        self.statusBar().showMessage(servertype)
        self.accListcomboBox.addItems(accList)

    def get_items(self, *market_list):
        for market in market_list:
            codeList = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(';')
            del codeList[-1]
            for code in codeList:
                name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)

                self.items[code] = name


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
