# -*- coding: UTF-8 -*-
#加载李旭飞落地的筹码数据
from ctypes import *
import io

def Struct2Str(qt):

    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','

    return tmpstr

#分价数据
class chipdata(Structure):
    _pack_ = 1
    _fields_ = [
        ('price', c_int),  #价格
        ('buyratio', c_int),  #成交占比
        ('sealratio', c_int),  # 成交占比
    ]

#股票分价数据
class stockchipinfo(Structure):
    _pack_ = 1
    _fields_ = [
        ('stockcode', c_char*22),  #股票代码
        ('chipdatacnt', c_int),  #分价个数
    ]

#文件格式
class fileinfo(Structure):
    _pack_ = 1
    _fields_ = [
        ('stockcnt', c_int),  #股票个数
        ('chipcnt',c_int),    #筹码个数
    ]

def loaddiv(filename):
    file = io.open(filename, 'rb')
    rdata = file.read()
    filelen = len(rdata)
    print filelen
    pos = 0
    nreminder = filelen
    if filelen < sizeof(fileinfo):
        print 'wrong file 1'
        return

    info  = fileinfo()
    memmove(addressof(info), rdata[0:sizeof(fileinfo)], sizeof(fileinfo))
    pos += sizeof(fileinfo)
    print Struct2Str(info)

    if filelen != sizeof(fileinfo) + sizeof(stockchipinfo)*info.stockcnt+ sizeof(chipdata)*info.chipcnt:
        print sizeof(stockchipinfo),sizeof(chipdata)
        print 'wrong file 2'
        return
    ncnt = 0
    n300171pos = 0
    n300171cnt = 0
    for i in range(0,info.stockcnt):
        stockchipinfoins = stockchipinfo()
        memmove(addressof(stockchipinfoins), rdata[pos:sizeof(stockchipinfo)+pos], sizeof(stockchipinfo))
        pos += sizeof(stockchipinfo)
        if stockchipinfoins.stockcode == 'SZ300171':
            print Struct2Str(stockchipinfoins)
            n300171pos = ncnt
            n300171cnt = stockchipinfoins.chipdatacnt
        ncnt += stockchipinfoins.chipdatacnt
    if ncnt != info.chipcnt:
        print ncnt,info.chipcnt
        print 'wrong file 3'
        return
    print n300171cnt,n300171pos
    pos += n300171pos*sizeof(chipdata)
    for j in range(n300171pos,n300171pos +n300171cnt):
        chipdatainstance = chipdata()
        memmove(addressof(chipdatainstance), rdata[pos:sizeof(chipdata) + pos],sizeof(chipdata))
        pos += sizeof(chipdata)
        print Struct2Str(chipdatainstance)
    print pos

loaddiv('E:/tmp/20171024.chip')