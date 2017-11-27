# -*- coding: UTF-8 -*-

from ctypes import *

def Struct2Str(qt):

    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','

    return tmpstr

class msgHeader(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MsgType', c_int),  #消息类型
        ('BodyLength', c_int),  #消息体长度
    ]

def checksum(data):
    idx = 0
    cks = 0
    for i in data:
        cks += ord(i)
    return cks%256

class msgTail(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('Checksum', c_int),  #
    ]

msgtype_login = 1
#msgtype = 1
class msgLogin(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('SenderCompID', c_char*20 ),  #
        ('TargetCompID', c_char*20 ),  #
        ('HeartBtInt', c_int ),  #
        ('Password', c_char*16 ),  #
        ('DefaultApplVerID', c_char*32),  #
    ]

msgtype_logout = 2
#msgtype = 2
class msgLoginOut(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('SessionStatus', c_int),  #
        ('Text', c_char*200),  #
    ]

msgtype_heartbeat = 3
#bodylenlength =0

msgtype_channel_heartbeat = 390095

class msgChanHeartBeat(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ChannelNo', c_int16),  #
        ('ApplLastSeqNum', c_int64),  #
        ('EndOfChannel', c_int16),  #
    ]

msgtype_zhubi_resend = 390094
#VSS ->MDGW
class msgzhubiresend(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ResendType', c_int8),  #
        ('ChannelNo', c_int16),  #
        ('ApplBegSeqNum', c_int64),  #
        ('ApplEndSeqNum', c_int64),  #
        ('NewsID', c_char*8),  #
        ('ResendStatus', c_int8),  #
        ('RejectText', c_char*16 ),  #
    ]

msgtype_userinfo_report = 390093
#VSS ->MDGW
class msguserinforeport(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('VersionCode', c_char*16),  #
        ('UserNum', c_int16),  #
    ]

msgtype_quote_count = 390090

class quotecountitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MDStreamID', c_char*3),  #
        ('StockNum', c_int),  #
        ('TradingPhaseCode', c_char*8),  #
    ]
#MDGW ->VSS
class msgquotecount(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('ChannelNo', c_int16),  #
        ('NoMDStreamID', c_int),  #
    ]
    def __init__(self):
        self.itemvec = []

msgtype_reject = 8
#MDGW ->VSS
class msgreject(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('RefSeqNum', c_int64),  #
        ('RefMsgType', c_int),  #
        ('BusinessRejectRefID', c_char*10),  #
        ('BusinessRejectReason', c_int16),  #
        ('BusinessRejectText', c_char*50),  #
    ]

#市场实时状态 额度数据
msgtype_market_status = 390019
class msgmarketstatus(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('ChannelNo', c_int16),  #
        ('MarketID', c_char*8),  #
        ('MarketSegmentID', c_char*8),  #
        ('TradingSessionID',c_char*4 ),  #
        ('TradingSessionSubID', c_char*4),  #
        ('TradSesStatus', c_int16),  #
        ('TradSesStartTime', c_int64),  #
        ('TradSesEndTime', c_int64),  #
        ('ThresholdAmount', c_int64),  #
        ('PosAmt', c_int64),  #
        ('AmountStatus', c_char),  #
    ]

msgtype_stock_status = 390013

class SecuritySwitch(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('Type', c_int16),  #
        ('Status', c_int16),  #
    ]

class msgstockstatus(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('ChannelNo', c_int16),  #
        ('SecurityID', c_char*8),  #
        ('SecurityIDSource', c_char*4),  #
        ('FinancialStatus', c_char*8),  #
        ('NoSwitch', c_int),  #
    ]
    def __init__(self):
        self.switchvec = []

msgtype_gonggao = 390012

class msggonggao(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('ChannelNo', c_int16),  #
        ('SecurityID', c_char * 8),  #
        ('NewsID', c_char * 4),  #
        ('Headline', c_char * 8),  #
        ('RawDataFormat', c_char*8),
        ('RawDataLength', c_int),  #
        # ('RawData', c_char),  #
    ]
    def __init__(self):
        self.RawData = []

# 3xxx11
class msghqkz(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrigTime', c_int64),  #
        ('ChannelNo', c_int16),  #
        ('MDStreamID', c_char * 3),  #
        ('SecurityID', c_char * 8),  #
        ('SecurityIDSource', c_char * 4),  #
        ('TradingPhaseCode', c_char * 8),  #
        ('PrevClosePx', c_int64),  #
        ('NumTrades', c_int64),  #
        ('TotalVolumeTrade', c_int64),  #
        ('TotalValueTrade', c_int64),  #
    ]

msgtype_panhou = 300611
#盘后定价交易业务行情快照
class msgpanhouitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MDEntryType', c_char*2),  #
        ('MDEntryPx', c_int64),  #
        ('MDEntrySize', c_int64),  #
    ]

# class msgpanhou(msghqkz):
class msgpanhou(BigEndianStructure):
    _pack_ = 1
    _fields_ = msghqkz._fields_+[
        ('NoMDEntries', c_int),  #
    ]
    def __init__(self):
        self.itemvec = []

# print sizeof(msggonggao)
msgtype_volume_tj_ex = 309111
#成交量统计指标行情快照
class msgvolume_tj_ex(BigEndianStructure):
    _pack_ = 1
    _fields_ = msghqkz._fields_+[
        ('StockNum', c_int),  #
    ]
    def __init__(self):
        self.itemvec = []

msgtype_hqkz_ex = 300111
#集中竞价交易业务行情快照
class orderitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('OrderQty', c_int64),  #
    ]

class msghqkzexitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MDEntryType', c_char*2),  #
        ('MDEntryPx', c_int64),  #
        ('MDEntrySize', c_int64),  #
        ('MDPriceLevel', c_int16),  #
        ('NumberOfOrders', c_int64),  #
        ('NoOrders', c_int),  #
    ]
    def __init__(self):
        self.itemlist = []

class msghqkz_ex(BigEndianStructure):
    _pack_ = 1
    _fields_ = msghqkz._fields_+[
        ('NoMDEntries', c_int),  #
    ]
    def __init__(self):
        self.itemlist = []


msgtype_index_ex = 309011
#指数行情快照
class msgindexexitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MDEntryType', c_char*2),  #
        ('MDEntryPx', c_int64),  #
        # ('MDEntrySize', c_int64),  #
        # ('MDPriceLevel', c_int16),  #
    ]

class msg_index_ex(BigEndianStructure):
    _pack_ = 1
    _fields_ = msghqkz._fields_+[
        ('NoMDEntries', c_int),  #
    ]
    def __init__(self):
        self.itemlist = []


msgtype_hkhq_ex = 306311
#港股实时行情快照
class msghkhqexitem(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('MDEntryType', c_char*2),  #
        ('MDEntryPx', c_int64),  #
        ('MDEntrySize', c_int64),  #
        ('MDPriceLevel', c_int16),  #
    ]

class msghkvcm(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ComplexEventStartTime', c_int64),  #
        ('ComplexEventEndTime', c_int64),  #
    ]


class msg_hkhq_ex(BigEndianStructure):
    _pack_ = 1
    _fields_ = msghqkz._fields_+[
        ('NoMDEntries', c_int),  #
    ]
    def __init__(self):
        self.NoComplexEventTimes = 0#int
        self.itemlist = []
        self.vcm = []

#逐笔委托
class msg_zubiwt(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ChannelNo', c_int16),  #
        ('ApplSeqNum', c_int64),  #
        ('MDStreamID', c_char * 3),  #
        ('SecurityID', c_char * 8),  #
        ('SecurityIDSource', c_char * 4),  #
        ('Price', c_int64),  #
        ('OrderQty', c_int64),  #
        ('Side', c_char),  #
        ('TransactTime', c_int64),  #
    ]

#逐笔成交
class msg_zubi(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ChannelNo', c_int16),  #
        ('ApplSeqNum', c_int64),  #
        ('MDStreamID', c_char * 3),  #
        ('BidApplSeqNum', c_int64),  #
        ('OfferApplSeqNum', c_int64),  #
        ('SecurityID', c_char * 8),  #
        ('SecurityIDSource', c_char * 4),  #
        ('LastPx', c_int64),  #
        ('LastQty', c_int64),  #
        ('ExecType', c_char),  #
        ('TransactTime', c_int64),  #
    ]

msgtype_jzjj_zubiwt = 300192
#集中竞价逐笔
msgtype_xxjy_zubiwt = 300592
#协议交易逐笔
msgtype_zrt_zubiwt = 300792
#转融通证券出借逐笔

msgtype_jzjj_zubi = 300191
#集中竞价逐笔
msgtype_xxjy_zubi = 300591
#协议交易逐笔
msgtype_zrt_zubi = 300791
#转融通证券出借逐笔

class msg_jzjj_zubiwt(BigEndianStructure):
    _pack_ = 1
    _fields_ = msg_zubiwt._fields_+[
        ('OrdType', c_char),  #
    ]


class msg_xxjy_zubiwt(BigEndianStructure):
    _pack_ = 1
    _fields_ = msg_zubiwt._fields_+[
        ('ConfirmID', c_char*8),  #
        ('Contactor', c_char*12),  #
        ('ContactInfo', c_char*30),  #
    ]

class msg_zrt_zubiwt(BigEndianStructure):
    _pack_ = 1
    _fields_ = msg_zubiwt._fields_+[
        ('ExpirationDays', c_int16),  #
        ('ExpirationType', c_int8),  #
    ]

