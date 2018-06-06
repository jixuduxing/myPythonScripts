# -*- coding: UTF-8 -*-
#海通主站接入转码
import os
import socket
import threading
import time

# array.array('','sd')
import redis

from httranscode.htstruct import *
from httcstruct import *
# import array
from util.until import getCurrentFileName, InitLog,uchar_checksum
from util.buffereader import buffereader


class httcclient:
    zqdmmap = {CAM_ZQDM_INFO: Struct_ZQDMInfo, CAM_MB_INFO: myMbInfo}
    hqkzmap = {TCM_HQKZ_SSHQ: struct_SSHQ, TCM_HQKZ_SSZS: SSZS, TCM_HQKZ_BLOCKHQ: BLOCKHQ, TCM_HQKZ_XGSG: struct_xgsg,
               TCM_HQKZ_FunFlow: FunFlow}
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.running = True

    def connect(self,ip,port):
        print "connect",(ip,port)
        return self.sock_.connect( (ip,port) )

    def login(self):
        print "login"
        header = TcMsgHeader()
        loginreq = TcLoginReq()
        header.checksum = 0
        header.boot_code = TCM_MSG_BOOT_CODE
        header.seq_id = 2
        header.cmd = TCM_LOGIN_RQST
        loginreq.version = HT_TC_VERSION
        header.length = sizeof(TcMsgHeader) + sizeof(TcLoginReq )

        req = string_at(addressof(header),sizeof(header)) + string_at(addressof(loginreq),sizeof(loginreq))
        header.checksum = uchar_checksum(req)

        req = string_at(addressof(header),sizeof(header)) + string_at(addressof(loginreq),sizeof(loginreq))
        self.sock_.send(req)

    def heartbeat(self):
        header = TcMsgHeader()
        header.boot_code = TCM_MSG_BOOT_CODE
        header.cmd = TCM_IDLE_RQST
        header.length = sizeof(TcMsgHeader)
        # hbpack = header.tobuffer()
        hbpack = string_at(addressof(header),sizeof(header))
        header.checksum = uchar_checksum(hbpack)
        hbpack = string_at(addressof(header),sizeof(header))
        self.sock_.send(hbpack)

    def recvhead(self):
        datarecv = self.saferecv(sizeof(TcMsgHeader) )

        if (len(datarecv) < sizeof(TcMsgHeader) ):
            print 'wrong datarecv',len(datarecv)
            return datarecv,CaMsgHeader(),-1
        header = TcMsgHeader()
        memmove(addressof(header), datarecv, sizeof(TcMsgHeader))
        # header = CaMsgHeader.frombuffer(datarecv)
        # print 'recvhead',datarecv

        return datarecv,header,header.length - sizeof(header)

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
        # print PrintStuct(header)
        # print "pack:0x%x" % header.cmd
        bodyrecv = []
        if bodylen >0:
            bodyrecv = self.recvbody(bodylen)
            if (len(bodyrecv) < bodylen  ):
                print 'wrong bodyrecv',len(bodyrecv),bodylen
                return False
        self.parsebody(header,bodyrecv,callback)
        return True



    def parsebody(self,header,bodyrecv,callback = None):

        if header.cmd == TCM_IDLE_RPLY:
            pass
            print "TCM_IDLE_RPLY"
        elif header.cmd == CAM_HQKZ_RQST:
            # print "TCM_HQKZ_RQST"
            for (str,type) in self.parseHQKZ_RQST(header,bodyrecv):
                if callback:
                    callback(str,type)
                else:
                    print str,type
        elif header.cmd == TCM_ZQDMINFO_RQST:
            for (str,type) in self.parseZQDMINFO_RQST(header, bodyrecv):
                if callback:
                    callback(str,0)
                else:
                    print str
                pass
        else:
            print "unknown pack:0x%x" % header.cmd

    def parseZQDMINFO_RQST(self,header,bodyrecv):
        pos = 0
        tcmZqdmInfoReq = TcmZqdmInfoReq()#.frombuffer(bodyrecv)
        memmove( addressof(tcmZqdmInfoReq),bodyrecv,sizeof(TcmZqdmInfoReq))
        # print PrintStuct(tcmZqdmInfoReq)
        # print "CamZqdmInfoReq:",camZqdmInfoReq.getstr()
        pos += sizeof(tcmZqdmInfoReq)
        if tcmZqdmInfoReq.flags & TCM_FLAGS_MARKET_FIRST_PACKET:
            if header.length < (sizeof(TcMsgHeader) + sizeof(TcmZqdmInfoReq) + sizeof(TcmZqdmInfoHeaderReq)):
                # print "header.length < sizeof(TcMsgHeader) + sizeof(TcmZqdmInfoReq) + sizeof(TcmZqdmInfoHeaderReq)"
                return
            tcmZqdmInfoHeaderReq = TcmZqdmInfoHeaderReq()
            memmove(addressof(tcmZqdmInfoHeaderReq), bodyrecv[pos:], sizeof(TcmZqdmInfoHeaderReq))
            # print PrintStuct(tcmZqdmInfoHeaderReq)
            pos += sizeof(TcmZqdmInfoHeaderReq)

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, tcmZqdmInfoReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            info = None
            structbuff = buffer.readbytes(structsize)
            if self.zqdmmap.has_key(kztype):
                classtype = self.zqdmmap[kztype]
                # print classtype
                info = classtype()
                memmove(addressof(info), structbuff, min(sizeof(classtype), structsize))
                yield info, kztype

    def parseHQKZ_RQST(self,header,bodyrecv):
        pos = 0
        tcmHqkzReq = TcmHqkzReq()  # .frombuffer(bodyrecv)
        memmove(addressof(tcmHqkzReq), bodyrecv, sizeof(TcmHqkzReq))
        # PrintQt(tcmHqkzReq)
        pos += sizeof(tcmHqkzReq)
        if tcmHqkzReq.flags & TCM_FLAGS_MARKET_FIRST_PACKET:
            if header.length < (sizeof(TcMsgHeader) + sizeof(TcmHqkzReq) + sizeof(TcmHqkzHeaderReq)):
                print "header.length < sizeof(TcMsgHeader) + sizeof(TcmHqkzReq) + sizeof(TcmHqkzHeaderReq)"
                return
            tcmHqkzHeaderReq = TcmHqkzHeaderReq()
            memmove(addressof(tcmHqkzHeaderReq), bodyrecv[pos:], sizeof(TcmHqkzHeaderReq))
            # print PrintStuct(tcmHqkzHeaderReq)
            pos += sizeof(TcmHqkzHeaderReq)

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0,tcmHqkzReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            info = None
            structbuff = buffer.readbytes(structsize)

            if self.hqkzmap.has_key(kztype):
                classtype = self.hqkzmap[kztype]
                info = classtype()
                memmove(addressof(info), structbuff, min(sizeof(classtype), structsize))
                yield info, kztype

    def keepconn(args):
        while args.running:
            args.heartbeat()
            time.sleep(5)
            print "keepconn running"

    def work(self,callback = None):
        ncycle = 0;
        while 1:
            if self.handle(callback) :
                ncycle += 1
                continue;
            else:
                break;


