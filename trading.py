# python system trading program using PyQt
# Reference : https://cafe.naver.com/autotradestudy, https://wikidocs.net/book/110
# author : youngpark-POS

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
import sqlite3

ui_form = uic.loadUiType("new_main_window.ui")[0]


class MyWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.textEdit.setEnabled(False)
        self.searchButton.clicked.connect(self.search_item)
        self.kiwoom.OnReceiveTrData.connect(self.receive_Trdata)

    def setupUI(self):
        self.setupUi(self)

    def event_connect(self, errcode):
        if errcode == 0:
            self.statusBar().showMessage("OK")
            self.textEdit.append("Login Success")
            self.get_logininfo()
            self.get_codelist(0)
        elif errcode == -100:
            self.statusBar().showMessage("User information exchange failed")
        elif errcode == -101:
            self.statusBar().showMessage("Server access failed")
        elif errcode == -102:
            self.statusBar().showMessage("Version progress failed")

    def search_item(self):
        code = self.lineEdit.text()
        self.textEdit.append("Item Code : " + code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                "coingo", "opt10001", 0, "0101")

    def receive_Trdata(self, *args):
        if args[1] == "coingo":  # args[1] is sRQName, args[2] is sTrcode
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",
                                           args[2], "", args[1], 0, "종목명")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",
                                             args[2], "", args[1], 0, "PER")

            self.textEdit.append("Item name : " + name.strip())
            self.textEdit.append("Volume : " + volume.strip())

    def get_logininfo(self):
        account_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        self.textEdit.append("Account number : " + ','.join(account_num.rstrip(';').split(';')))

    def get_codelist(self, *args):
        code_name_list = []
        for arg in args:
            code_list = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", str(arg)).split(';')
            del code_list[-1]
            for code in code_list:
                name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)
                code_name_list.append(code + " : " + name)
        for code_name in code_name_list:
            self.textEdit.append(code_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

