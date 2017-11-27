# -*- coding: UTF-8 -*-
#加载分钟K 历史服务
import io
from ctypes import *
import MySQLdb

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

# //
# //历史线数据文件头
# //
# typedef struct _THisFileHeader
# {
# 	uint16_t zq_count; //股票数量
# 	uint16_t item_size; //历史数据项字节数（=sizeof(FSZSItem) 或 sizeof(SSKLineItem)）
# } THisFileHeader;
# //
# //上海深圳市场的分钟历史k线项头
# //（其它市场如果证券代码长度不一致，重新定义新类型）
# //
# typedef struct _THisItemHeader
# {
# 	uint16_t item_header_size; //本结构体大小（=sizeof(THisItemHeader) + strlen(zqdm) + 1）
# 	uint32_t item_offset; //数据项起始位置（从文件头开始的绝对位置）
# 	uint16_t item_count; //数据项数量
# 	char zqdm[0]; //证券代码，包括结尾的\0
# } THisItemHeader;

class THisFileHeader(Structure):
    _pack_ =1
    _fields_ = [
        ('zq_count', c_ushort),  #
        ('item_size', c_ushort),  #
    ]

class THisItemHeader(Structure):
    _pack_ =1
    _fields_ = [
        ('item_header_size', c_ushort),  #
        ('item_offset', c_uint),  #
        ('item_count', c_ushort),  #
    ]

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

class FSZSItem(Structure):
    _pack_ = 1
    _fields_ = [
        ('time', c_int),  #
        ('last', c_int),  #
        ('volume', c_longlong),  #
        ('amount', c_longlong),  #
        ('avg_price', c_int),  #
        ('position', c_int),  #
        ('inner_volume', c_longlong),  #
    ]

def PrintStruct(qt):
    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','
    print tmpstr

# 打开数据库连接
db = MySQLdb.connect("172.190.28.217","root","password","testdb" )
# 使用cursor()方法获取操作游标
cursor = db.cursor()


def loadfszs(filename):
    file = io.open(filename, 'rb')
    rdata = file.read()
    filelen = len(rdata)
    if filelen < sizeof(TDatFileHeader):
        print "wrong file"
        return
    print filelen, sizeof(FSZSItem), sizeof(TDatFileHeader), sizeof(THisFileHeader), sizeof(THisItemHeader)

    header = TDatFileHeader()
    memmove(addressof(header), rdata[:sizeof(TDatFileHeader)], sizeof(TDatFileHeader))
    PrintStruct(header)
    pos = sizeof(TDatFileHeader)

    hisfiledata = rdata[pos:]

    hisheader = THisFileHeader()
    memmove(addressof(hisheader),hisfiledata[:sizeof(THisFileHeader)],sizeof(THisFileHeader))
    PrintStruct(hisheader)
    pos = sizeof(THisFileHeader)

    n600000offset = 0
    n600000cnt = 0
    # item600000header = THisItemHeader()
    itemheader = THisItemHeader()
    n240cnt = 0
    for i in range(0,hisheader.zq_count):

        memmove(addressof(itemheader),hisfiledata[pos:pos+sizeof(THisItemHeader)],sizeof(THisItemHeader))

        code = hisfiledata[pos+sizeof(THisItemHeader):pos+itemheader.item_header_size-1]
        if itemheader.item_count >100:
            PrintStruct(itemheader)
            print code
            n240cnt += 1
        if code == 'SH6000000':
            PrintStruct(itemheader)
            strsql = "insert into mink(code,time,open,high,low,close,volum,value,pos,capital_in,capital_out) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            param =()
            for j in range(0, itemheader.item_count):
                item = HtKline()
                offset = itemheader.item_offset + sizeof(HtKline) * j
                memmove(addressof(item), hisfiledata[offset:offset+sizeof(HtKline)], sizeof(HtKline))
                print (item.time >> 20) & 0xFFF, (item.time >> 16) & 0xF, (item.time >> 11) & 0x1F, (item.time >> 6) & 0x1F, item.time  & 0x3F
                # PrintStruct(item)
                strsql = "insert into mink(code,time,open,high,low,close,volum,value,pos,capital_in,capital_out) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                # strsql = "insert into mink(code,time) values(%s,%s);"
                # strsql = "insert into mink(code,time,open,high,low,close,volum,value,pos,capital_in,capital_out) values('" + code + "'," + str(item.time) + ',' + str(item.open) + ',' + str(item.high) + ',' + str(item.low) + \
                #          ',' + str(item.close) + ',' + str(item.volume) + ',' + str(item.amount) + ',' + \
                #          str(item.position) + ',' + str(item.capital_in) + ',' + str(item.capital_out) + ');'

                curparam = ((code,item.time,item.open,item.high,item.low,item.close,item.volume,item.amount,item.position,item.capital_in,item.capital_out),)
                param = param+ curparam
                # param = (code,item.time)

                # 使用execute方法执行SQL语句

            if len(param):
                print param
                print cursor.executemany(strsql, param)
                # cursor.fetchone()

        pos += itemheader.item_header_size
        # print i

    # nCnt = filelen / sizeof(FSZSItem)
    # for i in range(0, nCnt):
    #     info = FSZSItem()
    #     memmove(addressof(info),
    #             rdata[i * sizeof(FSZSItem) + sizeof(TDatFileHeader):(i + 1) * sizeof(FSZSItem) + sizeof(TDatFileHeader)],
    #             sizeof(FSZSItem))
        # print (info.time >> 20) & 0xFFF, (info.time >> 16) & 0xF, (info.time >> 11) & 0x1F
        # PrintStruct(info)

    print n240cnt

# loadfszs('D:/tmp/test/SH20171109.mink')
loadfszs('D:/tmp/test/SH20171114.mink')

db.commit()
# 关闭数据库连接
db.close()
