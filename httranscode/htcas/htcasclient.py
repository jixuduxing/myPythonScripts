# -*- coding: UTF-8 -*-
#海通转码级联
import logging
import socket
import sys
import time

# array.array('','sd')
haveredis = 0

sys.path.append('..')

from htstruct import *
# import array
from until import uchar_checksum
from buffereader import buffereader



class htcasclient:
    zqdmmap = {CAM_ZQDM_INFO: Struct_ZQDMInfo, CAM_MB_INFO: myMbInfo}
    hqkzmap = {CAM_HQKZ_SSHQ: struct_SSHQ, CAM_HQKZ_SSZS: SSZS, CAM_HQKZ_BLOCKHQ: BLOCKHQ, CAM_HQKZ_XGSG: struct_xgsg,
               CAM_HQKZ_FunFlow: FunFlow}

    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.running = True
        self.totalpack = 0

    def connect(self,ip,port):
        print "connect",(ip,port)
        return self.sock_.connect( (ip,port) )

    def login(self):
        print "login"
        header = CaMsgHeader()
        loginreq = CamLoginReq()
        loginreq.version = HT_TC_VERSION+1
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

    def handle(self,callback = None):
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
        self.parsebody(header,bodyrecv,callback)
        return True

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
            # print 'i:', i
            kztype = buffer.readbyte()
            # print 'kztype:',kztype
            structsize = buffer.readint()
            info = None
            structbuff = buffer.readbytes(structsize)
            if self.zqdmmap.has_key(kztype):
                classtype = self.zqdmmap[kztype]
                # print classtype
                info = classtype()
                memmove(addressof(info),structbuff , min(sizeof(classtype),structsize))
                yield info, kztype

    def parseHQKZ_RQST(self,header,bodyrecv):
        pos = 0
        camHqkzReq = struct_CamHqkzReq()
        # camHqkzReq = CamHqkzReq.frombuffer(bodyrecv)

        memmove(addressof(camHqkzReq), bodyrecv[:sizeof(struct_CamHqkzReq)],
                sizeof(struct_CamHqkzReq))
        # print PrintStuct(camHqkzReq)
        pos += sizeof(struct_CamHqkzReq)
        if camHqkzReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET :
            if header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size ):
                print "header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size )"
                return
            camHqkzHeaderReq = struct_CamZqdmInfoHeaderReq()

            memmove(addressof(camHqkzHeaderReq), bodyrecv[pos:(pos+sizeof(struct_CamZqdmInfoHeaderReq))], sizeof(struct_CamZqdmInfoHeaderReq) )
            pos += sizeof(struct_CamZqdmInfoHeaderReq)
        # return
        buffer = buffereader(bodyrecv[pos:])

        for i in range(0,camHqkzReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            info =None
            structbuff = buffer.readbytes(structsize)

            if self.hqkzmap.has_key(kztype):
                classtype = self.hqkzmap[kztype]
                info = classtype()
                memmove(addressof(info), structbuff, min(sizeof(classtype),structsize))
                yield info, kztype


    def keepconn(args):
        while args.running:
            args.heartbeat()
            time.sleep(5)
            print "keepconn running"

    def parsebody(self,header,bodyrecv,callback = None):
        self.totalpack = self.totalpack +1
        # print  time.asctime(),self.totalpack
        # print  time.time(),self.totalpack
        if header.cmd == CAM_LOGIN_RPLY:
            reader = buffereader(bodyrecv)
            print "CAM_LOGIN_RPLY:0x%x" %reader.readint()
        elif header.cmd == CAM_MARKET_RPLY:
            print "CAM_MARKET_RPLY:"
        elif header.cmd == CAM_IDLE_RPLY:
            print "CAM_IDLE_RPLY"
        elif header.cmd == CAM_HQKZ_RQST:
            # print "CAM_HQKZ_RQST"
            for (str,type) in self.parseHQKZ_RQST(header,bodyrecv):
                if callback:
                    callback(str,type)
                else:
                    print str,type

        elif header.cmd == CAM_ZQDMINFO_RQST:
            for (str,type) in self.parseZQDMINFO_RQST(header, bodyrecv):
                if callback:
                    callback(str,0)
                else:
                    print str
                pass
        else:
            print "unknown pack:0x%x" % header.cmd

    def work(self,callback = None):
        ncycle = 0;
        while 1:
            if self.handle(callback) :
                ncycle += 1
                continue;
            else:
                break;


# client = htcasclient()
# client.connect( ip,port )
# client.login()
# client.reqmarkets(['SH','SZ'])
#
# def mycallback(info,type):
#     pass
#
# client.work(mycallback)