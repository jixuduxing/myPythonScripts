import socket
from httranscode.htstruct import *
import time

from httranscode.htstruct import *


class testobject(Structure):
    _pack_ = 1
    _fields_ = [
        ('test1', c_ushort),  #
    ]

class teststruct(testobject):
    _pack_ = 1
    _fields_ = testobject._fields_+[
        ('boot_code', c_ushort),  #
        ('checksum', c_ushort),  #
        ('length', c_ushort),  #
        ('cmd', c_ushort),  #
        ('seq_id', c_uint),  #
    ]

    def __new__(name):
        cls = Structure.__new__(name)
        cls.test = lambda x: type(x)
        return cls

def prn_obj(obj):
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])

tts = teststruct()
print sizeof(teststruct)
# prn_obj(teststruct)
print tts.test(tts)
for item in teststruct._fields_:
    # name = item[0]
    print item[0],':',getattr(tts,item[0])
# getattr(tts,'te')

class test:
    def __init__(self):
        self.ad= 0


def printit(test1):
    print test1.__class__

tt = test()
printit(tt)

ip = '127.0.0.1'
port = 8020


def testCasServer():
    # sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print 'ret:',sock_.connect(('10.10.13.26', 13120))
    pos = 0
    while 1:
        for i in range(1,100):
            try:
                sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_.connect((ip, port))
                header = CaMsgHeader()
                loginreq = CamLoginReq()
                body = loginreq.tobuffer()

                header.length = CaMsgHeader.size + CamLoginReq.size

                req = header.tobuffer() + body
                header.checksum = uchar_checksum(req)

                req = header.tobuffer() + body
                sock_.send(req)
                time.sleep(1)
                sock_.close()
                pos +=1
            except Exception, ex:
                print Exception, ":", ex,pos
