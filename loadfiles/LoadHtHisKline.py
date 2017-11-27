# -*- coding: UTF-8 -*-
#加载下载服务(主站)落地的K线  his目录
import io
import codecs
import sys
from ctypes import *

# CSafedDatFile

# class SSKLineItem
# {
# public:
#     int time; //用行情客户端日期时间格式：year(12bits)|month(4)|day(5)|hour(5)|minute(6)
#     int open; //开盘价
#     int high; //最高价
#     int low; //最低价
#     int close; //收盘价
#     int64_t volume; //成交量
#     int64_t amount; //成交额
#     int position; //持仓量 总的持仓量，tag为0没有该字段
#     int capital_in; //ADD 资金流入
#     int capital_out; //ADD 资金流出
# };

# struct TDatFileHeader
# {
# 	uint16_t	HeadSize; //文件头大小。当前版本=sizeof(TDatFileHeader).
# 	uint32_t	Type; //文件类型码。当前版本='DATF'.
# 	uint16_t	Version; //文件版本。当前版本=0x100.
# 	int32_t		CreateTime; //文件创建时间。dates from midnight(00:00:00), January 1, 1970 to January 18, 2038. UTC time.
# 	uint8_t		Lock1; //文件锁1。1表示锁住，0表示未锁。写数据时交替锁住Lock1、Lock2，写后解锁，防止数据写中断不一致。
# 	uint32_t    FileSize1; //锁1的文件大小。
# 	int32_t		TimeStamp1; //锁1的时间戳。对于K线，为最后一条K线的时间，K线时间格式：year(12bits)|month(4)|day(5)|hour(5)|minute(6)
# 	int32_t		UpdateTime1; //锁1更新时间。同文件创建时间格式.
# 	uint8_t		Lock2; //锁2。
# 	uint32_t	FileSize2; //锁2的文件大小。
# 	int32_t		TimeStamp2; //锁2的时间戳。
# 	int32_t		UpdateTime2; //锁2更新时间。
# };

class TDatFileHeader(Structure):
    _pack_ =1
    _fields_ = [
        ('HeadSize', c_short),  #
        ('Type', c_char*4),  #
        ('Version', c_short),  #
        ('CreateTime', c_int),  #
        ('Lock1', c_byte),  #
        ('FileSize1', c_int),  #
        ('TimeStamp1', c_int),  #
        ('UpdateTime1', c_int),  #
        ('Lock2', c_byte),  #
        ('FileSize2', c_int),  #
        ('TimeStamp2', c_int),  #
        ('UpdateTime2', c_int),  #
    ]

class HtKline(Structure):
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
    if filelen <sizeof(TDatFileHeader):
        print "wrong file"
        return
    header = TDatFileHeader()
    memmove(addressof(header),rdata[:sizeof(TDatFileHeader)],sizeof(TDatFileHeader))
    PrintStruct(header)
    print filelen,sizeof(HtKline),filelen/sizeof(HtKline),sizeof(TDatFileHeader),filelen%sizeof(HtKline)
    nCnt = filelen/sizeof(HtKline)
    for i in range(0,nCnt):
        info = HtKline()
        memmove(addressof(info), rdata[i*sizeof(HtKline)+sizeof(TDatFileHeader):(i+1)*sizeof(HtKline)+sizeof(TDatFileHeader)], sizeof(HtKline))
        print (info.time>>20)&0xFFF,(info.time>>16)&0xF,(info.time>>11)&0x1F
        PrintStruct(info)


testkline( 'D:/tmp/test/81049.day')
# testkline( 'D:/tmp/test/81059.day')
# testkline( 'D:/tmp/test/600000.day')
# testkline( 'D:/tmp/test/300642.day')