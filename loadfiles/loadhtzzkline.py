# -*- coding: UTF-8 -*-
#加载海通主站落地日K线  cache目录

import io
import codecs
import sys
from ctypes import *
import struct

class TCacheFileHeader(Structure):
    _pack_ =1
    _fields_ = [
        ('HeadSize', c_short),  #
        ('Type', c_char*4),  #
        ('Version', c_short),  #
        ('CreateTime', c_int),  #
        ('Lock1', c_byte),  #
        ('FileSize1', c_int),  #
        ('RecordCount1', c_int),  #
        ('TimeStamp1', c_int),  #
        ('UpdateTime1', c_int),  #
        ('Lock2', c_byte),  #
        ('FileSize2', c_int),  #
        ('RecordCount2', c_int),  #
        ('TimeStamp2', c_int),  #
        ('UpdateTime2', c_int),  #
    ]

class Kline(Structure):
    _pack_ =1
    _fields_ = [
        ('time', c_int),  #
        ('open', c_int),  #
        ('high', c_int),  #
        ('low', c_int),  #
        ('close', c_int),  #
        # ('preclose', c_int),  #
        ('volume', c_longlong),  #
        ('amount', c_longlong),  #
        ('position', c_int),  #
        ('capital_in', c_int),  #
        ('capital_out', c_int),  #
    ]

def PrintStruct(qt):
    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','
    print tmpstr

def testkline(filename = 'D:/BK/BK2011040000'):
    file = io.open(filename,'rb')
    rdata = file.read()
    filelen = len(rdata)
    print filelen
    if filelen <sizeof(TCacheFileHeader):
        print "wrong file"
        return
    header = TCacheFileHeader()
    memmove(addressof(header),rdata[:sizeof(TCacheFileHeader)],sizeof(TCacheFileHeader))
    PrintStruct(header)

    pos = sizeof(TCacheFileHeader)

    for i in range(0,10000000):
        bfil = 0
        unpackdata =struct.unpack('B', rdata[pos:pos+1])
        codesize = unpackdata[0]
        code = rdata[pos+1:pos+codesize+1]
        # if code =='SH600837':
        if code =='SH600000':
            bfil = 1
            print code
        pos += 1+codesize

        info = Kline()
        memmove(addressof(info), rdata[pos:pos+sizeof(Kline)], sizeof(Kline))
        # if 2115064768 == info.time:
        #     bfil = 1
        #     print code
        if bfil:
            print (info.time>>20)&0xFFF,(info.time>>16)&0xF,(info.time>>11)&0x1F,(info.time>>6)&0x1F,(info.time)&0x3F
            PrintStruct(info)
        pos += sizeof(Kline)

        if pos < filelen:
            continue
        else:
            print "end",pos,filelen
            break

# testkline('D:/tmp/test/TX_SH_kine_day/SH_kine_day.2')
testkline('D:/tmp/test/SH_kine_day.1')