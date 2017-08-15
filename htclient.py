import socket
import struct
from buffereader import buffereader

class quotelistitem:
    def __init__(self):
        # self.code_        # self.name_        # self.decimal_        # self.type_        # self.preclose_        # self.open_
        # self.new_        # self.high_        # self.low_        # self.amount_
        pass

    def setcodename(self,code,name):
        self.code_ = code
        self.name_ = name

    def settuple(self,tuple):
        self.decimal_ = tuple[0]
        self.type_ = tuple[1]
        self.preclose_ = tuple[2]
        self.open_ = tuple[3]
        self.new_ = tuple[4]
        self.high_ = tuple[5]
        self.low_ = tuple[6]
        self.amount_ = tuple[7]

    def printcodes(self):
        print str(self.code_)+","+str(self.name_)
    def printself(self):
        print str(self.code_),str(self.name_), (self.decimal_, self.type_, self.preclose_, self.open_, self.new_, self.high_, self.low_, self.amount_)

class htclient:
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    def connect(self,ip,port):
        return self.sock_.connect( (ip,port) )

    def reqest2984(self,rankingfield = 1,rankingway = 0,reqbegin =0,reqnum = 50):
        print "reqest2984:",(rankingfield, rankingway,rankingway, reqbegin,reqnum)
        body = struct.pack('<3B2h',  rankingfield, rankingway,rankingway, reqbegin,reqnum)
        tail = '}'
        head = struct.pack('<c3h','{',2984,0,struct.calcsize('<3b2h') )
        data = head +body +tail
        self.sock_.send(data)

    def reqest2955(self,market = 102, filedattri = 0,rankingfield = 9,rankingway = 0,reqbegin =0,reqnum = 50):
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

    def recvhead(self):
        datarecv = self.sock_.recv(7)
        # print 'recvhead',datarecv
        if (len(datarecv) < 7):
            print 'wrong datarecv',len(datarecv)
            return datarecv,0
        unpackdata = struct.unpack('<c3h', datarecv[:7])
        print unpackdata
        return datarecv,unpackdata[3]

    def recvbody(self,bodylen):
        datarecv = self.sock_.recv(bodylen+1)
        # print 'recvbody',datarecv
        if (len(datarecv) < ( bodylen + 1) ):
            print 'wrong bodyrecv',len(datarecv)
            return datarecv
        return datarecv

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

                tuples = reader.readtuple('<2b6i')
                quoteitem.settuple(tuples)
                quoteitem.printcodes()
                # quoteitem.printself()
                if bodyhead[0] ==105:
                    reader.readshort()
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

            return itemlist,bodyhead[0]


def Getlist( market,rankingway = 0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2955(market = market,rankingway = rankingway)
    index = 0

    datarecv,datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist,totalsize = client.parsebody( 2955,bodyrecv )
        # print 'totallist:', len(totallist), ',totalsize:', totalsize
        index += len(itemlist)
        totallist = totallist + itemlist
        while index <totalsize:
            client.reqest2955(reqbegin = index,market =market,rankingway = rankingway)
            datarecv, datalen = client.recvhead()
            if not datalen:
                print "recv head error"
                break
            bodyrecv = client.recvbody(datalen)
            itemlist, totalsize = client.parsebody(2955, bodyrecv)
            index += len(itemlist)
            totallist = totallist + itemlist
        print 'totallist:',len(totallist),',totalsize:',totalsize

def Getlist2984( rankingway = 0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2984(rankingway = rankingway,reqnum= 50)
    index = 0

    datarecv,datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)
    totallist = []
    if datalen:

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist,totalsize = client.parsebody( 2984,bodyrecv )
        # print 'totallist:', len(totallist), ',totalsize:', totalsize
        index += len(itemlist)
        totallist = totallist + itemlist
        while index <totalsize:
            client.reqest2984(reqbegin = index,rankingway = rankingway,reqnum= 50)
            datarecv, datalen = client.recvhead()
            if not datalen:
                print "recv head error"
                break
            bodyrecv = client.recvbody(datalen)
            itemlist, totalsize = client.parsebody(2984, bodyrecv)
            index += len(itemlist)
            totallist = totallist + itemlist
        print 'totallist:',len(totallist),',totalsize:',totalsize


def Getlist2938(market, rankingway=0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2938(market=market, rankingway=rankingway)
    index = 0

    datarecv, datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist, totalsize = client.parsebody(2938, bodyrecv)