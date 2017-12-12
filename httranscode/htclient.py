# -*- coding: UTF-8 -*-

import socket
import struct
from buffereader import buffereader
from ctypes import *
import time

class quotelistitem:
    def __init__(self):
        # self.code_        # self.name_        # self.decimal_        # self.type_        # self.preclose_        # self.open_
        # self.new_        # self.high_        # self.low_        # self.amount_
        pass

    def setcodename(self,code,name):
        self.code_ = code
        self.name_ = name

    def settuple(self,tuple):
        print tuple
        self.decimal_ = tuple[0]
        self.type_ = tuple[1]
        self.preclose_ = tuple[2]
        self.open_ = tuple[3]
        self.new_ = tuple[4]
        self.high_ = tuple[5]
        self.low_ = tuple[6]
        self.amount_ = tuple[7]
        self.volumn_ = tuple[10]


    def printcodes(self):
        print str(self.code_)+","+str(self.name_)
    def printself(self):
        print str(self.code_),str(self.name_), (self.decimal_, self.type_, self.preclose_, self.open_, self.new_, self.high_, self.low_, self.amount_)

class pushhead(Structure):
    _pack_ = 1
    _fields_ = [
        ('errcode', c_int),  #
        ('seq', c_int),  #
        ('listrange', c_short),  #
        ('listatt', c_short),  #
        ('totalnum', c_short),  #
        ('curnum', c_short),  #
        ('zh1', c_int),  #
        ('zh2', c_int),  #
        ('zh3', c_int),  #
    ]

def Stuct2Str(qt):

    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','

    # print tmpstr
    return tmpstr

class htclient:
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.running = True
        self.seq = 1

    def connect(self,ip,port):
        return self.sock_.connect( (ip,port) )

    def heartbeat(self):
        body = struct.pack('<I', self.seq)
        seq = self.seq +1
        tail = '}'
        head = struct.pack('<c3h', '{', 10009, 0, struct.calcsize('<I'))
        data = head + body + tail
        self.sock_.send(data)

    def reqest2984(self,rankingfield = 0,rankingway = 0,reqbegin =0,reqnum = 50):
        print "reqest2984:",(rankingfield, rankingway,rankingway, reqbegin,reqnum)
        body = struct.pack('<3B2h',  rankingfield, rankingway,rankingway, reqbegin,reqnum)
        tail = '}'
        head = struct.pack('<c3h','{',2984,0,struct.calcsize('<3b2h') )
        data = head +body +tail
        self.sock_.send(data)

    def reqest2955(self,market = 102, filedattri = 1,rankingfield = 9,rankingway = 0,reqbegin =0,reqnum = 50):
        body = struct.pack('<2h2B3h',market, filedattri, rankingfield, rankingway, reqbegin,reqnum,0)
        tail = '}'
        head = struct.pack('<c3h','{',2955,0,struct.calcsize('<2h2B3h') )
        data = head +body +tail
        self.sock_.send(data)

    def reqest2938(self,market = 102, rankingfield = 7,rankingway = 0,reqbegin =0,reqnum = 50):
        body = struct.pack('<H2B2hB',market,  rankingway,rankingfield, reqbegin,reqnum,1)
        tail = '}'
        head = struct.pack('<c3h','{',2938,0,struct.calcsize('<h2B2hB') )
        data = head +body +tail
        self.sock_.send(data)

    def reqest2331(self,id = 0, rankingfield = 1,rankingway = 0,reqbegin =0,reqnum = 50):
        body = struct.pack('<3H3B',0, reqbegin,reqnum,rankingfield, rankingway,id )
        tail = '}'
        head = struct.pack('<c3h','{',2331,0,struct.calcsize('<3H3B') )
        data = head +body +tail
        self.sock_.send(data)

    # int    流水号    转发即可
    # short    列表范围    其实就是自选股列表，可以是1个股票，可以多个
    # short    操作类型    1    取消（即完全删除），2    删除（删除部分），3    增加（增加股票），4    替换（删除原有，使用新的）
    # short    请求条数    2
    # String[]    代码列表 8    SH6000018SZ000001
    # int    字段组合类型一    组合操作符、筛选证券代码的字段
    # int    字段组合类型二    备用
    # int    字段组合类型三    备用(总共96个位，应该够用了）  zh1 = 1 code  zh2 =1 行情时间
    #request10000(10000,1,3,1,1,0,['SZ300059','SH600837'])
    def request10000(self,seq,listrange,optype,zh1,zh2,zh3,codes):
        body = struct.pack('<I3H', seq,listrange, optype, len(codes))
        for code in codes:
            codeencode = struct.pack('<H8s',len(code),code)
            # print codeencode
            body = body +codeencode
        bodytail = struct.pack('<3I',zh1,zh2,zh3)
        body = body +bodytail
        tail = '}'
        head = struct.pack('<c3h', '{', 10000, 0, len(body))
        data = head + body + tail
        self.sock_.send(data)

    def recvhead(self):
        datarecv = self.sock_.recv(7)
        # print 'recvhead',datarecv
        if (len(datarecv) < 7):
            print 'wrong datarecv',len(datarecv)
            return datarecv,0,0
        unpackdata = struct.unpack('<c3h', datarecv[:7])
        print unpackdata
        return datarecv,unpackdata[3],unpackdata[1]

    def recvbody(self,bodylen):
        datarecv = self.sock_.recv(bodylen+1)
        # print 'recvbody',datarecv
        if (len(datarecv) < ( bodylen + 1) ):
            print 'wrong bodyrecv',len(datarecv)
            return datarecv
        return datarecv

    def keepconn(args):
        while args.running:
            args.heartbeat()
            time.sleep(15)
            print "keepconn running"

    def parsebody(self,type,data):
        itemlist = []
        if type == 2955:
            reader = buffereader(data)
            bodyhead = reader.readtuple('<4h')
                # struct.unpack('<hhhh',data[:8])
            print 'bodyhead',bodyhead
            for i in range(0,bodyhead[3]):
                quoteitem = quotelistitem()
                code = reader.readstring()
                # print "code=",code,",test"
                name = reader.readstring()
                quoteitem.setcodename(code,name)

                # quoteitem.printself()
                if bodyhead[0] ==105:
                    tuples = reader.readtuple('<2b6i2hi')
                    quoteitem.settuple(tuples)
                    quoteitem.printcodes()
                else:
                    tuples = reader.readtuple('<2b6i')
                    quoteitem.settuple(tuples)
                    quoteitem.printcodes()
                    # reader.readshort()
                itemlist.append(quoteitem)

            return itemlist, bodyhead[2]
        elif type == 2938:
            reader = buffereader(data)
            bodyhead = reader.readtuple('<2h')
                # struct.unpack('<hhhh',data[:8])
            print 'bodyhead',bodyhead
            return itemlist,bodyhead[0]
        elif type == 2984:
            reader = buffereader(data)
            bodyhead = reader.readtuple('<2h')
                # struct.unpack('<hhhh',data[:8])
            print 'bodyhead',bodyhead

            for i in range(0,bodyhead[1]):
                quoteitem = quotelistitem()
                code = reader.readstring()
                # print "code=",code,",test"
                name = reader.readstring()
                quoteitem.setcodename(code,name)

                tuples = reader.readtuple('<b2ih')
                code = reader.readstring()
                name = reader.readstring()
                tuples = reader.readtuple('<b2i')
                # quoteitem.settuple(tuples)
                quoteitem.printcodes()
                # if bodyhead[0] ==105:
                #     reader.readshort()
                itemlist.append(quoteitem)

        elif type == 2331:
            reader = buffereader(data)
            bodyhead = reader.readtuple('<B2h')
            # struct.unpack('<hhhh',data[:8])
            print 'bodyhead', bodyhead

            for i in range(0, bodyhead[2]):
                quoteitem = quotelistitem()
                code = reader.readstring()
                # print "code=",code,",test"
                name = reader.readstring()
                quoteitem.setcodename(code, name)
                if bodyhead[0] == 5:
                    reader.readtuple('<6i')
                else:
                    reader.readtuple('<10i')
                quoteitem.printcodes()
                itemlist.append(quoteitem)
            return itemlist, bodyhead[1]
        elif type == 10000:
            print "type == 10000"
            return itemlist,type
        elif type == 10001:
            reader = buffereader(data[sizeof(pushhead):])
            bodyhead = pushhead()
            memmove(addressof(bodyhead),data,sizeof(pushhead))
            # print Stuct2Str(bodyhead)
            for i in range(0,bodyhead.curnum):
                if bodyhead.zh1&1:
                    # codelen = reader.readbyte(1)
                    code = reader.readstring()
                    print 'code =', code
                if bodyhead.zh2&1:
                    timecur = reader.readint()
                    print 'timecur=',timecur
            return itemlist,type
        elif type == 10009:
            print 'recv heartbeat'
            return itemlist,10009
        return itemlist,bodyhead[0]





