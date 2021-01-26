# python system trading program using PyQt
# Reference : https://cafe.naver.com/autotradestudy, https://wikidocs.net/book/110
# author : youngpark-POS, slayerzeroa
# 키움증권 Open Api+ Entity Class Generator

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from pandas import Series, DataFrame
import pandas as pd
import sqlite3
import time
import os, subprocess    # 프로세스 관련 모듈인데 혹시 몰라서 넣어놈

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_instance()
        self._set_signals_slots()

    def _create_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signals_slots(self):
        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveTrData.connect(self.receive_Trdata)


    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def event_connect(self, errcode):
        if errcode == 0:
            print("Connected")
            # self.get_logininfo()
        else:
            print("Disconnected")
        self.login_event_loop.exit()

    def market_search(self):
        code = self.lineEdit.text()
        self.dynamicCall("SetInputValue(QString, QString)", "업종코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "coingo", "opt20003", 0, "0211")

    def get_logininfo(self):
        account_num = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def receive_Trdata(self, *args):
        if args[4] == '2':  # args[4] is "next"
            self.remained_data = True
        else:
            self.remained_data = False

        if args[1] == "coingo":  # args[1] is sRQName, args[2] is sTrcode
            self._opt20006(args[1], args[2])

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_get_data(self, code, realtype, fieldname, index, itemname):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)",
                               code, realtype, fieldname, index, itemname)
        return ret.strip()

    def _opt20006(self, rqname, trcode):
        data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

        features = ["일자", "현재가"]
        features_en = ["date", "nwprice"]
        for i in range(data_cnt):
            data_list = []
            for feature in features:
                data_list.append(self._comm_get_data(trcode, "", rqname, i, feature))
            for j, feature_en in enumerate(features_en):
                self.ohlcv[feature_en].append(data_list[j])


class Condition(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_instance()
        self._set_signals_slots()

    def _create_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signals_slots(self):
        self.OnReceiveConditionVer.connect(self.condition_search)
        self.OnReceiveTrCondition.connect(self.condition_serach)
        self.OnReceiveRealCondition.connect(self.result_condition)

    def condition_search(self):
        self.dynamicCall("GetConditionLoad()")
        self.search_event_loop = QEventLoop()
        self.search_event_loop.exec_()
        self.dynamicCall("GetConditionNameList()")

    def result_condition(self, screen_no, condition_name, nIndex, nSearch):
        self.dynamicCall("SendCondition(QString, QString, int, int)", screen_no, condition_name, nIndex, nSearch)

        ## 조건검색 결과 가공


if __name__ == "__main__":

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.ohlcv = {'date': [], 'nwprice': []}
    kiwoom.comm_connect()
    kiwoom.set_input_value("업종코드", "001")
    kiwoom.set_input_value("기준일자", "")
    kiwoom.set_input_value("수정주가구분", "1")
    kiwoom.comm_rq_data("coingo", "opt20006", 0, "0211")

    while kiwoom.remained_data is True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("업종코드", "001")
        kiwoom.set_input_value("기준일자", "")
        kiwoom.set_input_value("수정주가구분", "1")
        kiwoom.comm_rq_data("coingo", "opt20006", 2, "0211")

    con_M = sqlite3.connect("marketINDEX.db")
    df_M = DataFrame(kiwoom.ohlcv, columns=["nwprice"], index=kiwoom.ohlcv["date"])
    df_M.to_sql("table_001", con_M, if_exists="replace")

    cursor = con_M.cursor()
    result1 = cursor.execute("SELECT * FROM table_001")    # 개별종목코드를 전체 시장코드로 변환
    row = result1.fetchmany(20)
    bf = row[19][1]    # 20일 전 종가
    nw = row[0][1]    # 현재 일봉 중 종가
    bh = int(bf)  # 숫자열 변환
    nl = int(nw)
    if nl > bh:
        print("1번 알고리즘을 실행합니다.")

        app = QApplication(sys.argv)   # 조건검색 알고리즘 1
        condition = Condition()
        condition.condition_searh()
        condition.result_condition("0150", "알고리즘 1", 0, 1)

        con_C = sqlite3.connect("ConditionList.db")
        df_C = DataFrame(condition.result_condition, columns=["code"], index=["1", "2", "3", "4", "5"])
        df_C.to_sql("table_condition_result", con_C, if_exists="replace")

        cursors = con_C.cursor()
        result2 = cursors.execute("SELECT * FROM table_condition_result")
        row = result2.fetchall()
        first = row[0][0]
        print(first)
    else:
        print("시장상황이 1번 알고리즘 실행조건을 만족하지 못했습니다.")