# -*- coding: UTF-8 -*-
#加载下载服务器落地分时走势

import io
from ctypes import *
import MySQLdb

#==============================================================================
#分时走势数据 --- 实时数据
# class FSZSItem:
# {
# public:
#     int time; //用行情客户端日期时间格式：year(12bits)|month(4)|day(5)|hour(5)|minute(6)
#     int	last; //最新价
#     int64_t volume; //成交量
#     int64_t amount; //成交额
#     int avg_price; //均价
#     int position; //持仓量
#     union
#     {
#         int64_t inner_volume; //内盘成交量（股票）
#         char zdj_ratio; //涨跌家数据（指数）
#     };
#
#     void Init();
#     bool Serialize(CMemStream* pStream) const;
#     bool Deserialize(CMemStream* pStream);
#     void Set(const FSZSItem* pValue);
# };

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
    for i in range(0,hisheader.zq_count):

        memmove(addressof(itemheader),hisfiledata[pos:pos+sizeof(THisItemHeader)],sizeof(THisItemHeader))

        code = hisfiledata[pos+sizeof(THisItemHeader):pos+itemheader.item_header_size-1]

        # print code
        if code == 'SH600000':
            PrintStruct(itemheader)
            for j in range(0, itemheader.item_count):
                item = FSZSItem()
                offset = itemheader.item_offset + sizeof(FSZSItem) * j
                memmove(addressof(item), hisfiledata[offset:offset+sizeof(FSZSItem)], sizeof(FSZSItem))
                print (item.time >> 20) & 0xFFF, (item.time >> 16) & 0xF, (item.time >> 11) & 0x1F, (item.time >> 6) & 0x1F, item.time  & 0x3F
                PrintStruct(item)

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

loadfszs('D:/tmp/test/SH20171109.fszs')

