# -*- coding: UTF-8 -*-
#深圳binary客户端类
import socket
import time

# import array
from util.buffereader import buffereader

from binaryStruct import *


class szbinclient:
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.running = True

    def connect(self,ip,port):
        print "connect",(ip,port)
        return self.sock_.connect( (ip,port) )

    def login(self):
        print "login"
        header = msgHeader()
        loginreq = msgLogin()
        tail = msgTail()

        header.MsgType = msgtype_login
        header.BodyLength = sizeof( loginreq)

        loginreq.SenderCompID = 'zork'
        loginreq.TargetCompID = 'VDE'
        loginreq.HeartBtInt = 10
        loginreq.Password = ''
        loginreq.DefaultApplVerID = '1.00'

        tail.Checksum = checksum(string_at(addressof(loginreq), sizeof(loginreq)))
        req = string_at(addressof(header),sizeof(header)) + string_at(addressof(loginreq),sizeof(loginreq))+ string_at(addressof(tail),sizeof(tail))
        self.sock_.send(req)

    def heartbeat(self):
        header = msgHeader()
        tail = msgTail()
        header.MsgType = msgtype_heartbeat
        header.BodyLength = 0
        req = string_at(addressof(header), sizeof(header)) + string_at(addressof(tail),sizeof(tail))
        self.sock_.send(req)

    def recvhead(self):
        datarecv = self.saferecv(sizeof(msgHeader) )

        if (len(datarecv) < sizeof(msgHeader) ):
            print 'wrong datarecv',len(datarecv)
            return datarecv,msgHeader(),-1
        header = msgHeader()
        memmove(addressof(header), datarecv, sizeof(msgHeader))
        # header = CaMsgHeader.frombuffer(datarecv)
        # print 'recvhead',datarecv

        return datarecv,header,header.BodyLength

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
        # yield 'handle'
        datarecv,header, bodylen = self.recvhead()
        if bodylen <0:
            raise Exception('wrong head')

        # yield Struct2Str(header)
        # print "pack:0x%x" % header.cmd
        bodyrecv = []
        # if bodylen >0:
        bodyrecv = self.recvbody(bodylen+sizeof(msgTail))
        if (len(bodyrecv) < (bodylen + sizeof(msgTail)) ):
            print 'wrong bodyrecv',len(bodyrecv),bodylen
            raise Exception('wrong bodyrecv')
        self.parsebody(header,bodyrecv)

    def parse_hqkz_ex(self,header, bodyrecv):

        pos = 0
        hqkz_ex = msghqkz_ex()  # .frombuffer(bodyrecv)
        memmove(addressof(hqkz_ex), bodyrecv, sizeof(msghqkz_ex))
        pos += sizeof(hqkz_ex)
        flag = 0
        if str(hqkz_ex.SecurityID).strip() == "300059":
            yield 'msgtype_hqkz_ex'
            flag = 1
            yield Struct2Str(hqkz_ex)
        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, hqkz_ex.NoMDEntries):
            info = msghqkzexitem()
            structsize = sizeof(msghqkzexitem)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            if flag :
                yield Struct2Str(info)
            for j in range(0,info.NoOrders):
                item = orderitem()
                structsize = sizeof(orderitem)
                structbuff = buffer.readbytes(structsize)
                memmove(addressof(item), structbuff, structsize)
                if flag:
                    yield Struct2Str(item)
                info.itemlist.append(item)
            hqkz_ex.itemlist.append(info)

    def parse_index_ex(self, header, bodyrecv):
        yield 'msgtype_index_ex'
        pos = 0
        index_ex = msg_index_ex()  # .frombuffer(bodyrecv)
        memmove(addressof(index_ex), bodyrecv, sizeof(msg_index_ex))
        pos += sizeof(msg_index_ex)

        yield Struct2Str(index_ex)
        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, index_ex.NoMDEntries):
            info = msgindexexitem()
            structsize = sizeof(msgindexexitem)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            index_ex.itemlist.append(info)
        pass

    def parse_hkhq_ex(self, header, bodyrecv):
        yield 'msgtype_hkhq_ex'
        pos = 0
        hkhq_ex = msg_hkhq_ex()  # .frombuffer(bodyrecv)
        memmove(addressof(hkhq_ex), bodyrecv, sizeof(msg_hkhq_ex))
        pos += sizeof(msg_hkhq_ex)

        yield Struct2Str(hkhq_ex)
        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, hkhq_ex.NoMDEntries):
            info = msghkhqexitem()
            structsize = sizeof(msghkhqexitem)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            hkhq_ex.itemlist.append(info)
        hkhq_ex.NoComplexEventTimes = buffer.readint()
        # yield hkhq_ex.NoComplexEventTimes
        for i in range(0, hkhq_ex.NoComplexEventTimes):
            info = msghkvcm()
            structsize = sizeof(msghkvcm)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            hkhq_ex.vcm.append(info)
        pass
    def parse_market_status(self, header, bodyrecv):
        yield 'msgtype_market_status'
        pos = 0
        marketstatus = msgmarketstatus()  # .frombuffer(bodyrecv)
        memmove(addressof(marketstatus), bodyrecv, sizeof(msgmarketstatus))
        pos += sizeof(msgmarketstatus)

        yield Struct2Str(marketstatus)
        pass

    def parse_stock_status(self, header, bodyrecv):
        yield 'msgtype_stock_status'
        pos = 0
        stockstatus = msgstockstatus()  # .frombuffer(bodyrecv)
        memmove(addressof(stockstatus), bodyrecv, sizeof(msgstockstatus))
        pos += sizeof(msgstockstatus)

        yield Struct2Str(stockstatus)
        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, stockstatus.NoSwitch):
            info = SecuritySwitch()
            structsize = sizeof(SecuritySwitch)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            stockstatus.switchvec.append(info)
        pass
    # def parse_quote_count(self, header, bodyrecv):
    #     yield 'msgtype_quote_count'
    #     pos = 0
    #     quotecount = msgquotecount()  # .frombuffer(bodyrecv)
    #     memmove(addressof(quotecount), bodyrecv, sizeof(msgquotecount))
    #     pos += sizeof(msgquotecount)
    #
    #     yield Struct2Str(quotecount)
    #
    #     buffer = buffereader(bodyrecv[pos:])
    #     for i in range(0, quotecount.NoMDStreamID):
    #         info = quotecountitem()
    #         structsize = sizeof(quotecountitem)
    #         structbuff = buffer.readbytes(structsize)
    #         memmove(addressof(info), structbuff, structsize)
    #         yield Struct2Str(info)
    #
    #         quotecount.itemvec.append(info)
    #     pass
    def parse_quote_count(self, header, bodyrecv):
        yield 'msgtype_quote_count'
        pos = 0
        quotecount = msgquotecount()  # .frombuffer(bodyrecv)
        memmove(addressof(quotecount), bodyrecv, sizeof(msgquotecount))
        pos += sizeof(msgquotecount)

        yield Struct2Str(quotecount)

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, quotecount.NoMDStreamID):
            info = quotecountitem()
            structsize = sizeof(quotecountitem)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            quotecount.itemvec.append(info)
        pass

    def parse_channel_heartbeat(self, header, bodyrecv):
        yield 'msgtype_channel_heartbeat'
        pos = 0
        ChanHeartBeat = msgChanHeartBeat()  # .frombuffer(bodyrecv)
        memmove(addressof(ChanHeartBeat), bodyrecv, sizeof(msgChanHeartBeat))
        pos += sizeof(msgChanHeartBeat)

        yield Struct2Str(ChanHeartBeat)

    def parse_login(self, header, bodyrecv):
        yield 'msgtype_login'
        pos = 0
        Login = msgLogin()  # .frombuffer(bodyrecv)
        memmove(addressof(Login), bodyrecv, sizeof(msgLogin))
        pos += sizeof(msgLogin)

        yield Struct2Str(Login)

    def parse_gonggao(self, header, bodyrecv):
        yield 'msgtype_gonggao'
        pos = 0
        gonggao = msggonggao()  # .frombuffer(bodyrecv)
        memmove(addressof(gonggao), bodyrecv, sizeof(msggonggao))
        pos += sizeof(msggonggao)

        yield Struct2Str(gonggao)

        buffer = buffereader(bodyrecv[pos:])
        structbuff = buffer.readbytes(gonggao.RawDataLength)
        yield structbuff
        pass
    def parse_panhou(self, header, bodyrecv):
        yield 'msgtype_panhou'
        pos = 0
        panhou = msgpanhou()  # .frombuffer(bodyrecv)
        memmove(addressof(panhou), bodyrecv, sizeof(msgpanhou))
        pos += sizeof(msgpanhou)

        yield Struct2Str(panhou)

        buffer = buffereader(bodyrecv[pos:])
        for i in range(0, panhou.NoMDEntries):
            info = msgpanhouitem()
            structsize = sizeof(msgpanhouitem)
            structbuff = buffer.readbytes(structsize)
            memmove(addressof(info), structbuff, structsize)
            yield Struct2Str(info)

            panhou.itemvec.append(info)
        pass
    def parse_volume_tj_ex(self, header, bodyrecv):
        yield 'msgtype_volume_tj_ex'
        pos = 0
        volume_tj_ex = msgvolume_tj_ex()  # .frombuffer(bodyrecv)
        memmove(addressof(volume_tj_ex), bodyrecv, sizeof(msgvolume_tj_ex))
        pos += sizeof(msgvolume_tj_ex)

        yield Struct2Str(volume_tj_ex)
        pass

    def parse_zubi(self, header, bodyrecv):
        yield 'msgtype_zubis'
        pos = 0
        zubi = msg_zubi()  # .frombuffer(bodyrecv)
        memmove(addressof(zubi), bodyrecv, sizeof(msg_zubi))
        pos += sizeof(msg_zubi)

        yield Struct2Str(zubi)

    def parse_zrt_zubiwt(self, header, bodyrecv):
        yield 'msgtype_zrt_zubiwt'
        pos = 0
        zubiwt = msg_zrt_zubiwt()  # .frombuffer(bodyrecv)
        memmove(addressof(zubiwt), bodyrecv, sizeof(msg_zrt_zubiwt))
        pos += sizeof(msg_zrt_zubiwt)

        yield Struct2Str(zubiwt)

    def parse_xxjy_zubiwt(self, header, bodyrecv):
        yield 'msgtype_xxjy_zubiwt'
        pos = 0
        zubiwt = msg_xxjy_zubiwt()  # .frombuffer(bodyrecv)
        memmove(addressof(zubiwt), bodyrecv, sizeof(msg_xxjy_zubiwt))
        pos += sizeof(msg_xxjy_zubiwt)

        yield Struct2Str(zubiwt)

    def parse_jzjj_zubiwt(self, header, bodyrecv):
        yield 'msgtype_jzjj_zubiwt'
        pos = 0
        zubiwt = msg_jzjj_zubiwt()  # .frombuffer(bodyrecv)
        memmove(addressof(zubiwt), bodyrecv, sizeof(msg_jzjj_zubiwt))
        pos += sizeof(msg_jzjj_zubiwt)

        yield Struct2Str(zubiwt)

    def parsebody(self, header, bodyrecv):
        print 'header.MsgType',header.MsgType
        pass

    def keepconn(args):
        while args.running:
            args.heartbeat()
            time.sleep(1)
            print "keepconn running"

    def work(self):
        print 'work'
        ncycle = 0
        while 1:
            # print 'hh'
            self.handle()
            # for out in self.handle():
            #     print out
            ncycle += 1



