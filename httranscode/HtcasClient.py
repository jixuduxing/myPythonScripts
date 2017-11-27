# -*- coding: UTF-8 -*-
#海通转码级联

import logging
import os
import socket
import time

# array.array('','sd')
import redis

from htstruct import *
# import array
from util.until import getCurrentFileName, InitLog,uchar_checksum
from util.buffereader import buffereader

red = redis.Redis(host='127.0.0.1', port=6379,db=1)
pipe = red.pipeline()
ps = red.pubsub()

class htcasclient:
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.running = True

    def connect(self,ip,port):
        print "connect",(ip,port)
        return self.sock_.connect( (ip,port) )

    def login(self):
        print "login"
        header = CaMsgHeader()
        loginreq = CamLoginReq()
        body = loginreq.tobuffer()

        header.length = CaMsgHeader.size + CamLoginReq.size

        req = header.tobuffer() + body
        header.checksum = uchar_checksum(req)

        req = header.tobuffer() + body
        self.sock_.send(req)

        # header2 = CaMsgHeader.frombuffer(req[:CaMsgHeader.size])
        # print header2.getstr()

    def heartbeat(self):
        header = CaMsgHeader()
        header.cmd = CAM_IDLE_RQST
        header.length = CaMsgHeader.size
        hbpack = header.tobuffer()
        header.checksum = uchar_checksum(hbpack)
        hbpack = header.tobuffer()
        self.sock_.send(hbpack)

    def reqmarkets(self,markets):#['MB','SZ','SH']
        print "reqmarkets",markets
        header = CaMsgHeader()
        marketreq = CamMarketReq( markets)
        body = marketreq.tobuffer()
        header.length = CaMsgHeader.size + len(body)
        header.cmd = CAM_MARKET_RQST

        req = header.tobuffer() + body
        header.checksum = uchar_checksum(req)

        req = header.tobuffer() + body
        self.sock_.send(req)

    def recvhead(self):
        datarecv = self.saferecv(CaMsgHeader.size)

        if (len(datarecv) < CaMsgHeader.size):
            print 'wrong datarecv',len(datarecv)
            return datarecv,CaMsgHeader(),-1
        header = CaMsgHeader.frombuffer(datarecv)
        # print 'recvhead',datarecv

        return datarecv,header,header.length - header.size

    def saferecv(self,size):
        nrecv = 0
        datatotal = []
        datarecv = self.sock_.recv(size)
        if 0 ==len(datarecv):
            print "saferecv error 1"
            return datatotal
        datatotal = datarecv
        # nrecv += len(datarecv)
        size -= len(datarecv)
        while size:
            datarecv = self.sock_.recv(size)
            if 0 == len(datarecv):
                print "saferecv error 2"
                return datatotal
            datatotal += datarecv
            # nrecv += len(datarecv)
            size -= len(datarecv)
        return datatotal
    def recvbody(self,bodylen):
        datarecv = self.saferecv(bodylen)
        # print 'recvbody',datarecv

        return datarecv

    def handle(self):
        # print "handle"
        datarecv,header, bodylen = self.recvhead()
        if bodylen <0:
            return False
        # print "header:",header.getstr()
        # print "pack:0x%x" % header.cmd
        bodyrecv = []
        if bodylen >0:
            bodyrecv = self.recvbody(bodylen)
            if (len(bodyrecv) < bodylen  ):
                print 'wrong bodyrecv',len(bodyrecv),bodylen
                return False
        self.parsebody(header,bodyrecv)
        return True



    def parsebody(self,header,bodyrecv):
        if header.cmd == CAM_LOGIN_RPLY:
            reader = buffereader(bodyrecv)
            print "CAM_LOGIN_RPLY:0x%x" %reader.readint()
        elif header.cmd == CAM_MARKET_RPLY:
            print "CAM_MARKET_RPLY:"
        elif header.cmd == CAM_IDLE_RPLY:
            print "CAM_IDLE_RPLY"
        elif header.cmd == CAM_HQKZ_RQST:
            print "CAM_HQKZ_RQST"
            self.parseHQKZ_RQST(header,bodyrecv)
        elif header.cmd == CAM_ZQDMINFO_RQST:
            # print "CAM_ZQDMINFO_RQST"
            self.parseZQDMINFO_RQST(header, bodyrecv)
        else:
            print "unknown pack:0x%x" % header.cmd

    def parseZQDMINFO_RQST(self,header,bodyrecv):
        pos = 0
        camZqdmInfoReq = CamZqdmInfoReq.frombuffer(bodyrecv)
        # print "CamZqdmInfoReq:",camZqdmInfoReq.getstr()
        pos += camZqdmInfoReq.size
        if camZqdmInfoReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET:
            if header.length < (CaMsgHeader.size + CamZqdmInfoReq.size + CamZqdmInfoHeaderReq.size):
                print "header.length < ( CaMsgHeader.size +CamZqdmInfoReq.size +CamZqdmInfoHeaderReq.size )"
                return
            camZqdmInfoHeaderReq = CamZqdmInfoHeaderReq.frombuffer(bodyrecv[pos:])
            # print "camZqdmInfoHeaderReq:",camZqdmInfoHeaderReq.getstr()
            pos += CamZqdmInfoHeaderReq.size

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, camZqdmInfoReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            if kztype == CAM_ZQDM_INFO:
                info = Struct_ZQDMInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(Struct_ZQDMInfo))
                # if info.code[0:3] == 'SH6':
                strstruct = PrintStuct(info)
                #     logging.debug(strstruct)
                # elif info.code[0:3] == 'SZ0':
                #     strstruct = PrintStuct(info)
                #     logging.debug(strstruct)
                # elif info.code[0:3] == 'SZ3':
                #     strstruct = PrintStuct(info)
                #     logging.debug(strstruct)
                if info.type == 15:
                    print strstruct

                pipe.multi()
                pipe.set('zqdminfo_' + info.code, strstruct)
                pipe.sadd('zqdmset', info.code)

                pipe.hset(info.code, 'code', info.code)
                pipe.hset(info.code, 'name', info.name)
                pipe.hset(info.code, 'pinyin_name', info.pinyin_name)
                pipe.hset(info.code, 'type', info.type)
                pipe.hset(info.code, 'volume_unit', info.volume_unit)
                pipe.hset(info.code, 'pre_close', info.pre_close)
                pipe.hset(info.code, 'high_limit', info.high_limit)
                pipe.hset(info.code, 'low_limit', info.low_limit)
                pipe.hset(info.code, 'price_digit', info.price_digit)
                pipe.hset(info.code, 'price_divide', info.price_divide)
                pipe.hset(info.code, 'intrest', info.intrest)
                pipe.hset(info.code, 'crd_flag', info.crd_flag)
                pipe.hset(info.code, 'pre_position', info.pre_position)
                pipe.hset(info.code, 'pre_settle_price', info.pre_settle_price)
                pipe.hset(info.code, 'ext_type', info.ext_type)
            #
                pipe.execute()
            elif kztype == CAM_MB_INFO:
                # print "GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET"

                info = myMbInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(myMbInfo))
                logging.debug(PrintStuct(info))
                # mbinfo = MBInfo.frombuffer(structbuff)
                # print mbinfo.getstr()
            else:
                print "kztype 2:", kztype, i, structsize
                structbuff = buffer.readbytes(structsize)

    def parseHQKZ_RQST(self,header,bodyrecv):
        pos = 0
        camHqkzReq = CamHqkzReq.frombuffer(bodyrecv)
        print camHqkzReq.getstr()
        pos += camHqkzReq.size
        if camHqkzReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET :
            if header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size ):
                print "header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size )"
                return
            camHqkzHeaderReq = CamHqkzHeaderReq.frombuffer( bodyrecv[pos:])
            prn_obj(camHqkzHeaderReq)
            print camHqkzHeaderReq.getstr()
            pos += CamHqkzHeaderReq.size

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0,camHqkzReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            # print "kztype:",kztype
            if kztype == CAM_HQKZ_SSHQ:
                structbuff = buffer.readbytes(structsize)
                sshq = SSHQ.frombuffer(structbuff)
                if sshq.code[0:3] == 'SH6':
                    logging.debug(prn_obj(sshq))
                elif sshq.code[0:3] == 'SZ0':
                    logging.debug(prn_obj(sshq))
                elif sshq.code[0:3] == 'SZ3':
                    logging.debug(prn_obj(sshq))
            elif kztype == CAM_HQKZ_BLOCKHQ:
                info = BLOCKHQ()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(BLOCKHQ))
                strstruct= PrintStuct(info)
                logging.debug(strstruct)
                pipe.multi()
                pipe.set('hq_' + info.code, strstruct)
                pipe.hset(info.code, 'last', info.last)
                pipe.hset(info.code, 'open', info.open)
                pipe.hset(info.code, 'high', info.high)
                pipe.hset(info.code, 'low', info.low)
                pipe.hset(info.code, 'total_volume', info.total_volume)
                pipe.hset(info.code, 'total_amount', info.total_amount)
                pipe.hset(info.code, 'pchTopStockCode', info.pchTopStockCode)
                pipe.hset(info.code, 'StockNum', info.StockNum)
                pipe.hset(info.code, 'UpNum', info.UpNum)
                pipe.hset(info.code, 'DownNum', info.DownNum)
                pipe.hset(info.code, 'StrongNum', info.StrongNum)
                pipe.hset(info.code, 'WeakNum', info.WeakNum)
                pipe.hset(info.code, 'ZGB', info.ZGB)
                pipe.hset(info.code, 'LTG', info.LTG)
                pipe.hset(info.code, 'LTSZ', info.LTSZ)
                pipe.hset(info.code, 'ZSZ', info.ZSZ)
                pipe.hset(info.code, 'date', info.date)
                pipe.hset(info.code, 'time', info.time)
                pipe.execute()
                # print sshq.getstr()
            # elif kztype == CAM_HQKZ_SSZS:
            # elif kztype == CAM_HQKZ_ORDER_QUEUE:
            # elif kztype == CAM_HQKZ_STEP_TRADE:
            # elif kztype == CAM_HQKZ_SSHQHZEXT:
            # elif kztype == CAM_HQKZ_HZZXJC:
            # elif kztype == CAM_HQKZ_MARKET_STATUS:
            # elif kztype == CAM_HQKZ_MARKET_STATIC_INFO:
            # elif kztype == CAM_HQKZ_SSHQ_OTC:
            # elif kztype == CAM_HQKZ_SSHQ_OTCZH:
            # elif kztype == CAM_HQKZ_SSHQ_SOZH:
            # elif kztype == CAM_HQKZ_SSHQ_SG:
            # elif kztype == CAM_HQKZ_SSHQEXT:
            elif kztype == CAM_HQKZ_XGSG:
                info = struct_xgsg()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(struct_xgsg))
                # logging.debug(PrintStuct(info))
            else:
                # print "kztype:",kztype
                structbuff = buffer.readbytes(structsize)

    def keepconn(args):
        while args.running:
            args.heartbeat()
            time.sleep(5)
            print "keepconn running"

    def work(self):
        ncycle = 0;
        while 1:
            if self.handle() :
                ncycle += 1
                continue;
            else:
                break;

            # if ncycle % 60 ==0:
            #     self.heartbeat()
            #     ncycle = 0

# def keepconn(args):
#     while args.running:
#         args.heartbeat()
#         time.sleep(5)

# header = CaMsgHeader()
# buffer = header.tobuffer()
# print buffer,len(buffer)
# inds  = 100
# print "16jinzhi  %x" %inds

curpath = os.path.dirname(__file__)
curfilename = getCurrentFileName()

InitLog(curpath,'htcasclient')

client = htcasclient()
# client.connect('10.10.13.26',8030)
# client.connect('127.0.0.1',8020)
# client.connect('115.159.95.177',13140)
# client.connect('115.159.95.177',13130)
client.connect('115.159.95.177',13140)
client.login()
# client.reqmarkets(['MB','SZ','SH'])
# client.reqmarkets(['MB','HZ'])
# client.reqmarkets(['SZ'])
# client.reqmarkets(['HT'])
client.reqmarkets(['SH','SZ'])
# client.reqmarkets(['BI'])
# client.reqmarkets(['BK'])
# client.reqmarkets(['US'])
client.work()
