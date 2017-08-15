import socket
import struct
# import array

from buffereader import buffereader
# array.array('','sd')

CAM_MSG_BOOT_CODE = 0x7f7f
HT_TC_VERSION = 0x020200


CAM_LOGIN_RQST = 0x80
CAM_LOGIN_RPLY = 0x8080
CAM_MARKET_RQST = 0x00f0
CAM_MARKET_RPLY = 0x80f0
CAM_IDLE_RQST = 0x00ff
CAM_IDLE_RPLY = 0x80ff

print CAM_MSG_BOOT_CODE

def print_all(module_):
  modulelist = dir(module_)
  length = len(modulelist)
  for i in range(0,length,1):
    print getattr(module_,modulelist[i])

class CaMsgHeader:
    fmt = '<4HiB'
    size = struct.calcsize(fmt)
    seqid = 1
    def __init__(self):
        self.boot_code = CAM_MSG_BOOT_CODE
        self.checksum = 0
        self.length = CaMsgHeader.size
        self.cmd = CAM_LOGIN_RQST
        CaMsgHeader.seqid = CaMsgHeader.seqid +1
        self.seq_id = CaMsgHeader.seqid
        self.compress = 0

    def init(self,tuple):
        self.boot_code = tuple[0]
        self.checksum = tuple[1]
        self.length = tuple[2]
        self.cmd = tuple[3]
        self.seq_id = tuple[4]
        self.compress = tuple[5]

    def tobuffer(self):
        return struct.pack( CaMsgHeader.fmt,self.boot_code,self.checksum,self.length,self.cmd,self.seq_id,self.compress )

    def getstr(self):
        return ( CaMsgHeader.fmt,self.boot_code,self.checksum,self.length,self.cmd,self.seq_id,self.compress )

    @staticmethod
    def fromtuple(buff):
        header = CaMsgHeader()
        unpacked = struct.unpack(CaMsgHeader.fmt,buff)
        header.init(unpacked)
        return header

class CamLoginReq:
    size = struct.calcsize('<i')
    def __init__(self):
        self.version = HT_TC_VERSION

    def tobuffer(self):
        return struct.pack('<i',self.version)

class CamMarketReq:
    def __init__(self,markets = []):
        self.compress = 0
        self.market_count = len(markets)
        self.markets = markets

    def tobuffer(self):
        data  = struct.pack('<2B',self.compress,self.market_count )
        for market in self.markets:
            data += struct.pack('<3s',market )
        return data

class httcclient:
    def __init__(self):
        self.sock_ = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    def connect(self,ip,port):
        return self.sock_.connect( (ip,port) )

    def login(self):
        header = CaMsgHeader()
        loginreq = CamLoginReq()
        header.length = CaMsgHeader.size + CamLoginReq.size
        loginpack = header.tobuffer() + loginreq.tobuffer()
        self.sock_.send(loginpack)

    def heartbeat(self):
        header = CaMsgHeader()
        header.cmd = CAM_IDLE_RQST
        header.length = CaMsgHeader.size
        hbpack = header.tobuffer()
        self.sock_.send(hbpack)

    def reqmarkets(self,markets):#['MB','SZ','SH']
        header = CaMsgHeader()
        marketreq = CamMarketReq( markets)
        body = marketreq.tobuffer()
        header.length = CaMsgHeader.size + len(body)
        header.cmd = CAM_MARKET_RQST
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
        datarecv = self.sock_.recv(CaMsgHeader.size)

        if (len(datarecv) < CaMsgHeader.size):
            print 'wrong datarecv',len(datarecv)
            return datarecv,CaMsgHeader(),-1
        header = CaMsgHeader.fromtuple(datarecv)
        # print 'recvhead',datarecv

        return datarecv,header,header.length - header.size

    def recvbody(self,bodylen):
        datarecv = self.sock_.recv(bodylen)
        # print 'recvbody',datarecv

        return datarecv

    def handle(self):
        datarecv,header, bodylen = self.recvhead()
        if bodylen <0:
            return False
        print header.getstr()
        # print "pack:0x%x" % header.cmd
        bodyrecv = []
        if bodyrecv >0:
            bodyrecv = self.recvbody(bodylen)
            if (len(bodyrecv) < bodylen  ):
                print 'wrong bodyrecv',len(bodyrecv),bodylen
                return
        if header.cmd == CAM_LOGIN_RPLY:
            reader = buffereader(bodyrecv)
            print "CAM_LOGIN_RPLY:",reader.readint()
        elif header.cmd == CAM_MARKET_RPLY:
            print "CAM_MARKET_RPLY:"
        elif header.cmd == CAM_IDLE_RPLY:
            print "CAM_IDLE_RPLY"
        else:
            print "unknown pack:0x%x" % header.cmd
        return True

    def work(self):
        ncycle = 0;
        while 1:
            if self.handle() :
                ncycle += 1
                continue;
            else:
                break;

            if ncycle % 60 ==0:
                self.heartbeat()
                ncycle = 0

# header = CaMsgHeader()
# buffer = header.tobuffer()
# print buffer,len(buffer)
# inds  = 100
# print "16jinzhi  %x" %inds
client = httcclient()
client.connect('10.10.13.26',13121)
# client.connect('127.0.0.1',8020)

client.login()
client.reqmarkets(['MB','SZ','SH'])
client.work()
