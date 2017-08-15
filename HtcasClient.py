# -*- coding: UTF-8 -*-
import socket
import time
import struct
# import array
import random
from buffereader import buffereader
from until import uchar_checksum
from htstruct import *
import threading
# array.array('','sd')

print CAM_MSG_BOOT_CODE

print uchar_checksum( '12345')

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

    def reqest2984(self,rankingfield = 1,rankingway = 0,reqbegin =0,reqnum = 50):
        print "reqest2984:",(rankingfield, rankingway,rankingway, reqbegin,reqnum)
        body = struct.pack('<3B2h',  rankingfield, rankingway,rankingway, reqbegin,reqnum)
        tail = '}'
        head = struct.pack('<c3h','{',2984,0,struct.calcsize('<3b2h') )
        data = head +body +tail
        self.sock_.send(data)

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
        print "header:",header.getstr()
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
            print "CAM_ZQDMINFO_RQST"
            self.parseZQDMINFO_RQST(header, bodyrecv)
        else:
            print "unknown pack:0x%x" % header.cmd

    def parseZQDMINFO_RQST(self,header,bodyrecv):
        pos = 0
        camZqdmInfoReq = CamZqdmInfoReq.frombuffer(bodyrecv)
        print "CamZqdmInfoReq:",camZqdmInfoReq.getstr()
        pos += camZqdmInfoReq.size
        if camZqdmInfoReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET:
            if header.length < (CaMsgHeader.size + CamZqdmInfoReq.size + CamZqdmInfoHeaderReq.size):
                print "header.length < ( CaMsgHeader.size +CamZqdmInfoReq.size +CamZqdmInfoHeaderReq.size )"
                return
            camZqdmInfoHeaderReq = CamZqdmInfoHeaderReq.frombuffer(bodyrecv[pos:])
            print "camZqdmInfoHeaderReq:",camZqdmInfoHeaderReq.getstr()
            pos += CamZqdmInfoHeaderReq.size

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, camZqdmInfoReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            print "kztype 2:", kztype,i,structsize
            if kztype == CAM_ZQDM_INFO:
                structbuff = buffer.readbytes(structsize)
                sshq = ZQDMInfo.frombuffer(structbuff)
                print sshq.getstr()
            elif kztype == CAM_MB_INFO:
                # print "GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET"

                info = myMbInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(myMbInfo))
                PrintQt( info)
                # mbinfo = MBInfo.frombuffer(structbuff)
                # print mbinfo.getstr()
            else:
                structbuff = buffer.readbytes(structsize)

    def parseHQKZ_RQST(self,header,bodyrecv):
        pos = 0
        camHqkzReq = CamHqkzReq.frombuffer(bodyrecv)
        # print camHqkzReq.getstr()
        pos += camHqkzReq.size
        if camHqkzReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET :
            if header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size ):
                print "header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size )"
                return
            camHqkzHeaderReq = CamHqkzHeaderReq.frombuffer( bodyrecv[pos:])
            # print camHqkzHeaderReq.getstr()
            pos += CamHqkzHeaderReq.size

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0,camHqkzReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            # print "kztype:",kztype
            if kztype == CAM_HQKZ_SSHQ:
                structbuff = buffer.readbytes(structsize)
                sshq = SSHQ.frombuffer(structbuff)
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
            # elif kztype == CAM_HQKZ_XGSG:
            else:
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
client = htcasclient()
# client.connect('10.10.13.26',13120)
client.connect('127.0.0.1',8020)

client.login()
# client.reqmarkets(['MB','SZ','SH'])
client.reqmarkets(['MB'])
# client.reqmarkets(['SH'])
t =threading.Thread(target=htcasclient.keepconn,args=(client,))
t.start()
client.work()
