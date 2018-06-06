# -*- coding: UTF-8 -*-
#海通转码级联
import logging
import os
import socket
import time
import sys
# array.array('','sd')
haveredis = 0



from htstruct import *
# import array
from until import getCurrentFileName, InitLog,uchar_checksum
from buffereader import buffereader

if haveredis:
    import redis
    red = redis.Redis(host='127.0.0.1', port=6379,db=2)
    pipe = red.pipeline()
    ps = red.pubsub()


class htcasclient:
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
        # yield 'test'
        # return
        # print "CamZqdmInfoReq:",camZqdmInfoReq.getstr()
        pos += camZqdmInfoReq.size
        if camZqdmInfoReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET:
            if header.length < (CaMsgHeader.size + CamZqdmInfoReq.size + CamZqdmInfoHeaderReq.size):
                print "header.length < ( CaMsgHeader.size +CamZqdmInfoReq.size +CamZqdmInfoHeaderReq.size )"
                return
            camZqdmInfoHeaderReq = CamZqdmInfoHeaderReq.frombuffer(bodyrecv[pos:])
            # print "camZqdmInfoHeaderReq:",camZqdmInfoHeaderReq.getstr()
            pos += CamZqdmInfoHeaderReq.size
        # return
        buffer = buffereader(bodyrecv[pos:])

        for i in range(0, camZqdmInfoReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            # print kztype,structsize
            if kztype == CAM_ZQDM_INFO:
                info = Struct_ZQDMInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(Struct_ZQDMInfo))
                strstruct = PrintStuct(info)

                yield  strstruct,CAM_ZQDM_INFO

                if haveredis:
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

                    pipe.execute()

            elif kztype == CAM_MB_INFO:
                # print "GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET"

                info = myMbInfo()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(myMbInfo))
                # logging.debug(PrintStuct(info) + str(time.time()))
                if  info.code[:2] =='BI':
                    logging.debug(PrintStuct(info) +str(time.time()))
                # mbinfo = MBInfo.frombuffer(structbuff)
                # print mbinfo.getstr()
            else:
                yield structsize, kztype
                structbuff = buffer.readbytes(structsize)

    def parseHQKZ_RQST(self,header,bodyrecv):
        pos = 0
        camHqkzReq = struct_CamHqkzReq()
        # camHqkzReq = CamHqkzReq.frombuffer(bodyrecv)
        # print camHqkzReq.getstr()
        memmove(addressof(camHqkzReq), bodyrecv[:sizeof(struct_CamHqkzReq)],
                sizeof(struct_CamHqkzReq))
        pos += sizeof(struct_CamHqkzReq)
        if camHqkzReq.flags & CAM_FLAGS_MARKET_FIRST_PACKET :
            if header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size ):
                print "header.length < ( CaMsgHeader.size +CamHqkzReq.size +CamHqkzHeaderReq.size )"
                return
            camHqkzHeaderReq = struct_CamZqdmInfoHeaderReq()
            # camHqkzHeaderReq = CamHqkzHeaderReq.frombuffer( bodyrecv[pos:])
            # prn_obj(camHqkzHeaderReq)
            memmove(addressof(camHqkzHeaderReq), bodyrecv[pos:(pos+sizeof(struct_CamZqdmInfoHeaderReq))], sizeof(struct_CamZqdmInfoHeaderReq) )
            # print camHqkzHeaderReq.getstr()
            pos += sizeof(struct_CamZqdmInfoHeaderReq)
            # logging.debug(PrintStuct(camHqkzHeaderReq))
        # return
        buffer = buffereader(bodyrecv[pos:])
        for i in range(0,camHqkzReq.item_count):
            kztype = buffer.readbyte()
            structsize = buffer.readint()
            # print "kztype:",kztype
            if kztype == CAM_HQKZ_SSHQ:
                structbuff = buffer.readbytes(structsize)
                info= struct_SSHQ()
                memmove(addressof(info), structbuff, sizeof(struct_SSHQ))
                # info = SSHQ.frombuffer(structbuff)
                # print prn_obj(info)
                # logging.debug(prn_obj(info))
                if haveredis:
                    pipe.multi()
                    code = str(info.code).strip('\x00')
                    pipe.hset(code, 'last', info.last)
                    pipe.hset(code, 'open', info.open)
                    pipe.hset(code, 'high', info.high)
                    pipe.hset(code, 'low', info.low)
                    pipe.hset(code, 'total_volume', info.total_volume)
                    pipe.hset(code, 'total_amount', info.total_amount)
                    pipe.hset(code, 'date', info.date)
                    pipe.hset(code, 'time', info.time)
                    pipe.execute()
                # if info.code[0:3] == 'BI9':
                #     # print info.code
                #     logging.debug(PrintStuct(info))
                if info.code[0:8] == 'SH600837':
                    # print info.code
                    yield (PrintStuct(info),1)
                if info.code[0:8] == 'SZ300059':
                    yield (PrintStuct(info),CAM_HQKZ_SSZS)
                # elif sshq.code[0:3] == 'SZ0':
                #     logging.debug(prn_obj(sshq))
                # elif sshq.code[0:3] == 'SZ3':
                #     logging.debug(prn_obj(sshq))
            elif kztype == CAM_HQKZ_SSZS:
                info = SSZS()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(SSZS))
                # print structsize,sizeof(SSZS)
                if info.code[0:8] == 'SH000001':
                    strstruct = PrintStuct(info) +str(time.time())
                    # print strstruct
                    yield (strstruct,CAM_HQKZ_SSZS)
                if info.code[0:3] == 'BI9':
                    strstruct = PrintStuct(info) +str(time.time())
                    yield (strstruct,CAM_HQKZ_SSZS)

            elif kztype == CAM_HQKZ_BLOCKHQ:
                info = BLOCKHQ()
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(info), structbuff, sizeof(BLOCKHQ))
                strstruct= PrintStuct(info)
                # logging.debug(strstruct)
                if haveredis:
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
            elif kztype == CAM_HQKZ_FunFlow:
                info = FunFlow()
                structbuff = buffer.readbytes(structsize)

                memmove(addressof(info), structbuff, sizeof(FunFlow))
                if info.code[:8] == 'SZ300431':
                    yield info,CAM_HQKZ_FunFlow
                    # yield (PrintStuct(info),CAM_HQKZ_FunFlow)
            elif kztype == CAM_HQKZ_SSHQEXT:
                buffer.readbytes(structsize)
                pass
            else:
                print "kztype:",kztype
                structbuff = buffer.readbytes(structsize)

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
            # print "CAM_ZQDMINFO_RQST"
            for str in self.parseZQDMINFO_RQST(header, bodyrecv):
                if callback:
                    callback(str,0)
                else:
                    print str
                # print str
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
print os.getcwd()
curpath = os.path.dirname(sys.argv[0])
print curpath
curpath = os.getcwd()
print curpath
curfilename = getCurrentFileName()

# logging.debug('test')
print  time.asctime()
client = htcasclient()
# client.connect('10.10.13.26',8030)
# client.connect('10.10.13.26',13120)
# client.connect('127.0.0.1',8020)
# client.connect('115.159.95.177',13120)
# client.connect('115.159.95.177',13130)
# client.connect('115.159.204.185',8020)
# client.connect('182.254.155.190',8020)
port = 8030
port = 8020
port = 13130
ip = '188.190.12.88'
# ip = '172.190.28.217'
# ip='10.10.13.26'
# ip='127.0.0.1'

if len(sys.argv) >2:
    ip = sys.argv[1]
    port = int(sys.argv[2])

filename = 'htcasclientbk'
# +str(os.getpid())
InitLog(curpath,filename)

client.connect( ip,port )
client.login()
# client.reqmarkets(['MB','SZ','SH','HT'])
# client.reqmarkets(['MB','HZ'])
# client.reqmarkets(['SZ'])
# client.reqmarkets(['HT'])
# client.reqmarkets(['SH','SZ'])
client.reqmarkets(['SH'])
# client.reqmarkets(['BI'])
# client.reqmarkets(['BK'])
# client.reqmarkets(['MB'])
def mycallback(str,type):
    if type == CAM_HQKZ_SSHQ:
        if str.code == 'SH600837':
            print str
        # print str,type
        pass
    else:
        pass
        # print str

client.work(mycallback)
