# -*- coding: GBK -*-
__author__ = 'gao'
#!/usr/bin/python


import socket
import struct
import traceback
import io
import datetime
import time
import zlib
from ctypes import *

STOCK_NAME_LEN = 32
STOCK_CODE_LEN = 16
MARKET_CODE_LEN = 16
STOCK_ID_LEN = 32

class SStdQt(Structure):
    _pack_ = 1
    _fields_ = [
        ('Date' , c_uint), #交易日YYYYMMDD
        ('Time' , c_uint), #交易时间hhmmss
        ('Name' , c_char * STOCK_NAME_LEN), #股票名称
        ('Code' , c_char * STOCK_CODE_LEN), #股票代码
        ('Market' , c_char * MARKET_CODE_LEN), #市场代码
        ('Open' , c_double), #开盘价
        ('High' , c_double), #最高价
        ('Low' , c_double), #最低价
        ('Price' , c_double), #最新价
        ('Close' , c_double), #前日收盘价
        ('Volume' , c_ulonglong), #成交量
        ('Amount' , c_double), #成交额
        ('TradeNum' , c_ulonglong), #成交笔数
        ('MMP' , c_double * 10), #买卖盘价格 卖五、卖四。。。买一。。。买五
        ('MMPVol' , c_ulonglong * 10), #买卖盘量
        ('AvgPrice' , c_double), #均价
        ('OpenInterest' , c_ulonglong), #持仓量
        ('SettlementPrice' , c_double), #今结算价
        ('PreOpenInterest' , c_ulonglong), #昨持仓量
        ('PreSettlementPrice' , c_double), #昨结算价
        ('PriceZT' , c_double), #涨停价，美股为52周最高价
        ('PriceDT' , c_double), #跌停价，美股为52周最低价
        ]

def prn_obj(obj):
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])

class DrsClient:
    __sock =''
    __packno = 200
    def connect(self,ip,port):
        # print dir(SStdQt)
        # print dir(DrsClient)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect((ip,port))

    def Register(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3344,1000,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterBroke(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3344,1002,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterRawData(self):
        data = struct.pack('!IIHH',12,self.__packno,0x3344,1100)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterMMP(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1001,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterNMX(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1004,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterCAS(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1006,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterQtEx(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1005,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterVCM(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1007,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def RegisterJsonQt(self,MarketName):
        data = struct.pack('!IIHH16s',28,self.__packno,0x3345,1009,MarketName)
        self.__sock.send(data)
        self.__packno+=1

    def __SafeRecv(self,leng):
        dat = ''
        while leng:
            data = self.__sock.recv(leng)
            if len(data) ==0:
                return data
            leng -= len(data)
            dat += data
        return dat

    def ParseData(self,data,output):
        #print data
        now = datetime.datetime.now()
        print now.strftime('%Y-%m-%d %H:%M:%S')
        print 'recv:'
        unpackeddata = struct.unpack_from('!IIHH',data,0)
        if unpackeddata[3] == 1000:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            for i in range(0, unpackeddata[2]):
                j = 33 +sizeof(SStdQt)*i
                # unpackeddata2 = struct.unpack_from('<II32s16s16s5dQdQ10d10QdQdQ3d',data,j)

                qt = SStdQt()
                memmove(addressof(qt),data[j:j+sizeof(SStdQt)],sizeof(SStdQt))
                output(qt)

        elif unpackeddata[3] == 76:
            print 'heart beat'
            self.__sock.send(data)
        elif unpackeddata[3] == 72:
            unpackeddata3 = struct.unpack_from('!I',data,14)
            dataCompressed = data[26:]
            totallen = unpackeddata3[0]
            dataUnCompress = zlib.decompress(dataCompressed)
            self.ParseData(data[14:26]+dataUnCompress,output)
        elif unpackeddata[3] == 1001:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            for i in range(0, unpackeddata[2]):
                j = 33 +352*i
                unpackeddata2 = struct.unpack_from('<16s16s20d20Q',data,j)
                # output(unpackeddata2)
        elif unpackeddata[3] == 1004:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            for i in range(0, unpackeddata[2]):
                j = 33 +59*i
                unpackeddata2 = struct.unpack_from('<16s16s2I2sIQIc',data,j)
                # output(unpackeddata2)

        elif unpackeddata[3] == 1005:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            for i in range(0, unpackeddata[2]):
                j = 33 +115*i
                unpackeddata2 = struct.unpack_from('<16s16sc3sI2s6c2I4sc3Ic3I16scIQ',data,j)
                # output(unpackeddata2)
        elif unpackeddata[3] == 1006:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            for i in range(0, unpackeddata[2]):
                j = 33 +53*i
                unpackeddata2 = struct.unpack_from('<16s16scQ3I',data,j)
                # output(unpackeddata2)
        elif unpackeddata[3] == 1007:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            for i in range(0, unpackeddata[2]):
                j = 33 +56*i
                unpackeddata2 = struct.unpack_from('<16s16s6I',data,j)
                # output(unpackeddata2)
        elif unpackeddata[3] == 1009:
            unpackeddata = struct.unpack_from('<16scI',data,12)
            print unpackeddata
            print data

            # for i in range(0, unpackeddata[2]):
            #     j = 33 +56*i
            #     unpackeddata2 = struct.unpack_from('<16s16s6I',data,j)
                # output(unpackeddata2)
        else:
            print "unknown Protocol:",unpackeddata[3]
            print data


        #print 'End'

    def RecordRawData(self,data):
        unpackeddata = struct.unpack_from('!IIHH',data,0)
        if unpackeddata[3] == 76:
            #print 'heart beat'
            self.__sock.send(data)
        else:
            sockname = self.__sock.getpeername()
            filew = io.open(sockname[0]+'_'+str(sockname[1]),'ab')

            filew.write(data[12:])
        #print data
        #sock.send(data)
    def RecvAndHandleData(self,handle,output):
        now = datetime.datetime.now()
        print now.strftime('%Y-%m-%d %H:%M:%S')

        while True:
            try:
                dat = self.__SafeRecv(4)
                if len(dat) == 0:
                    self.__sock.close()
                    print '\r\nthe End1\r\n'
                    break
                unpackeddata = struct.unpack_from('!I',dat,0)
                body = self.__SafeRecv(unpackeddata[0]-4)
                if len(body) == 0:
                    self.__sock.close()
                    print '\r\nthe End2\r\n'
                    break
                dat += body
                handle(dat,output)
            except Exception,ex:
                traceback.print_exc()
                print Exception,":",ex
                break

    def RecvSnapShotAndHandleData(self,handle,output):
        now = datetime.datetime.now()
        print now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            dat = self.__SafeRecv(4)
            if len(dat) == 0:
                self.__sock.close()
                print '\r\nthe End1\r\n'
            unpackeddata = struct.unpack_from('!I',dat,0)
            body = self.__SafeRecv(unpackeddata[0]-4)
            if len(body) == 0:
                self.__sock.close()
                print '\r\nthe End2\r\n'
            dat += body
            handle(dat,output)
        except Exception,ex:
            traceback.print_exc()
            print Exception,":",ex

    def Close(self):
        self.__sock.close()