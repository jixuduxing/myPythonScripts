# -*- coding: UTF-8 -*-
#海通主站接入转码
import os
import socket
import threading
import time

# array.array('','sd')
import redis

from htstruct import *
from httcstruct import *
# import array
from util.until import getCurrentFileName, InitLog,uchar_checksum
from util.buffereader import buffereader

red = redis.Redis(host='127.0.0.1', port=6379,db=1)
pipe = red.pipeline()
ps = red.pubsub()


class httcclient:
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

    def handle(self):
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
        self.parsebody(header,bodyrecv)
        return True



    def parsebody(self,header,bodyrecv):
        # if header.cmd == CAM_LOGIN_RPLY:
        #     reader = buffereader(bodyrecv)
        #     print "CAM_LOGIN_RPLY:0x%x" %reader.readint()
        # elif header.cmd == CAM_MARKET_RPLY:
        #     print "CAM_MARKET_RPLY:"
        if header.cmd == TCM_IDLE_RPLY:
            pass
            # print "TCM_IDLE_RPLY"
        elif header.cmd == CAM_HQKZ_RQST:
            # print "TCM_HQKZ_RQST"
            self.parseHQKZ_RQST(header,bodyrecv)
        elif header.cmd == TCM_ZQDMINFO_RQST:
            # print "TCM_ZQDMINFO_RQST"
            self.parseZQDMINFO_RQST(header, bodyrecv)
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
            if kztype == CAM_ZQDM_INFO:
                info = Struct_ZQDMInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(Struct_ZQDMInfo))
                strstruct = PrintStuct(info)
                # print strstruct
                pipe.multi()
                pipe.set( 'zqdminfo_'+info.code, strstruct)
                pipe.sadd( 'zqdmset',info.code)

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

                pipe.execute()

                # logging.debug(PrintQt(info))
            elif kztype == CAM_MB_INFO:
                info = myMbInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(myMbInfo))
                strstruct = PrintStuct(info)
                # print strstruct
                pipe.multi()
                pipe.set('mbinfo_' + info.code, strstruct)
                pipe.sadd('mbset', info.code)
                pipe.hset(info.code, 'name_now', info.name_now)
                pipe.hset(info.code, 'pinyin_name_now', info.pinyin_name_now)
                pipe.hset(info.code, 'name_old', info.name_old)
                pipe.hset(info.code, 'pinyin_name_old', info.pinyin_name_old)
                pipe.hset(info.code, 'type', info.type)
                # logging.debug(PrintQt( info))
                pipe.execute()

                # mbinfo = MBInfo.frombuffer(structbuff)
                # print mbinfo.getstr()
            else:
                # print "kztype 2:", kztype, i, structsize
                structbuff = buffer.readbytes(structsize)

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
            if kztype == CAM_HQKZ_SSHQ:
                structbuff = buffer.readbytes(structsize)
                sshq = SSHQ.frombuffer(structbuff)
                strstruct = sshq.getstr()
                strcode = str(sshq.code).strip('\x00')
                pipe.multi()
                pipe.set('sshq_' + strcode, strstruct)
                red.publish('sshq',strstruct)
                pipe.hset(strcode,'last',sshq.last)
                pipe.hset(strcode,'open',sshq.open)
                pipe.hset(strcode,'high',sshq.high)
                pipe.hset(strcode,'low',sshq.low)
                pipe.hset(strcode,'total_volume',sshq.total_volume)
                pipe.hset(strcode,'total_amount',sshq.total_amount)
                pipe.hset(strcode,'total_trade_count',sshq.total_trade_count)
                pipe.hset(strcode,'date',sshq.date)
                pipe.hset(strcode,'time',sshq.time)
                # pipe.set('sshq_' + str(sshq.code).strip('\x00') + '_' + str(sshq.date * 10000 + sshq.time / 100000), strstruct)
                pipe.execute()

            elif kztype == TCM_HQKZ_BLOCKHQ:
                info = BLOCKHQ()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(BLOCKHQ))
                strstruct = PrintStuct(info)
                print strstruct
                pipe.multi()
                pipe.set('blockhq_'+info.code,strstruct)
                red.publish('blockhq',strstruct)

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
                # pipe.set('blockhq_'+info.code+'_'+str(info.date*1000000000+info.time), strstruct)
                # pipe.set('blockhq_'+info.code+'_'+str(info.date*10000+info.time/100000), strstruct)

                pipe.execute()
                # logging.debug(strstruct)
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
                strstruct = PrintStuct(info)
                red.set('xgsg_' + info.code, strstruct)
                # red.set('blockhq_' + info.code + '_' + str(info.date * 1000000000 + info.time), strstruct)
                # red.set('blockhq_' + info.code + '_' + str(info.date * 10000 + info.time / 100000), strstruct)
                # logging.debug(PrintQt(info))
            else:
                # print "kztype:", kztype
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

InitLog(curpath,'httcclient')

client = httcclient()
# client.connect('10.10.13.26',8031)
# client.connect('127.0.0.1',9080)
client.connect('115.159.95.177',13141)

client.login()
# client.reqmarkets(['MB','SZ','SH'])
# client.reqmarkets(['MB'])
# client.reqmarkets(['SH'])
t =threading.Thread(target=httcclient.keepconn,args=(client,))
# t.start()
client.work()
