# -*- coding: UTF-8 -*-
#海通转码数据接口

import struct
# import array
from ctypes import *

CAM_MSG_BOOT_CODE = 0x7f7f
HT_TC_VERSION = 0x020200


CAM_LOGIN_RQST = 0x80
CAM_LOGIN_RPLY = 0x8080
CAM_MARKET_RQST = 0x00f0
CAM_MARKET_RPLY = 0x80f0#
CAM_IDLE_RQST = 0x00ff
CAM_IDLE_RPLY = 0x80ff

CAM_HQKZ_RQST = 0x0001
CAM_ZQDMINFO_RQST = 0x0003

CAM_FLAGS_FIRST_PACKET = 0x01
CAM_FLAGS_MARKET_FIRST_PACKET=0x02
CAM_FLAGS_MARKET_LAST_PACKET=0x04
CAM_FLAGS_LAST_PACKET		=0x08

CAM_ZQDM_INFO=1
CAM_ZQDM_OTC=2
CAM_ZQDM_SG=	3
CAM_MB_INFO=	4

CAM_HQKZ_SSHQ = 1
CAM_HQKZ_SSZS = 2
CAM_HQKZ_ORDER_QUEUE = 3
CAM_HQKZ_STEP_TRADE = 4
CAM_HQKZ_SSHQHZEXT = 5
CAM_HQKZ_HZZXJC = 6
CAM_HQKZ_MARKET_STATUS = 7
CAM_HQKZ_MARKET_STATIC_INFO = 8
CAM_HQKZ_SSHQ_OTC =9
CAM_HQKZ_SSHQ_OTCZH =10
CAM_HQKZ_SSHQ_SOZH = 11
CAM_HQKZ_SSHQ_SG =12
CAM_HQKZ_SSQDHQ	=13 #千档行情
CAM_HQKZ_SSHQEXT =	14 #拓展动态行情
CAM_HQKZ_XGSG =	15	#申购信息
CAM_HQKZ_BLOCKHQ = 16	#板块行情
CAM_HQKZ_FunFlow = 18 #资金流

print "CaMsgHeader(boot_code,checksum,length,cmd,seq_id,compress)"

class CaMsgHeader:
    fmt = '<4HIB'
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
    def frombuffer(buff):
        header = CaMsgHeader()
        unpacked = struct.unpack(CaMsgHeader.fmt,buff[:CaMsgHeader.size])
        header.init(unpacked)
        return header

class CamLoginReq:
    size = struct.calcsize('<i')
    def __init__(self):
        self.version = HT_TC_VERSION

    def tobuffer(self):
        return struct.pack('<I',self.version)

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

class struct_CamHqkzReq(Structure):
    _pack_ =1
    _fields_ = [
        ('flags', c_byte),  #
        ('item_count', c_byte),  #
    ]

class CamHqkzReq:
    fmt = '<2B'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.flags = 0
        self.item_count = 0

    def init(self,tuple):
        self.flags = tuple[0]
        self.item_count = tuple[1]

    @staticmethod
    def frombuffer(buff):
        header = CamHqkzReq()
        unpacked = struct.unpack(CamHqkzReq.fmt, buff[:CamHqkzReq.size])
        header.init(unpacked)
        return header
    def getstr(self):
        return (CamHqkzReq.fmt,self.flags, self.item_count )

class CamZqdmInfoReq:
    fmt = '<2B'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.flags = 0
        self.item_count = 0

    def init(self,tuple):
        self.flags = tuple[0]
        self.item_count = tuple[1]

    @staticmethod
    def frombuffer(buff):
        header = CamZqdmInfoReq()
        unpacked = struct.unpack(CamZqdmInfoReq.fmt, buff[:CamZqdmInfoReq.size])
        header.init(unpacked)
        return header

    def getstr(self):
        return (CamZqdmInfoReq.fmt,self.flags, self.item_count )

class CamHqkzHeaderReq:
    fmt = '<3s2i'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.market_code = ''
        self.hqkz_date = 0
        self.hqkz_time = 0

    def init(self,tuple):
        self.market_code = tuple[0]
        self.hqkz_date = tuple[1]
        self.hqkz_time = tuple[2]

    @staticmethod
    def frombuffer(buff):
        header = CamHqkzHeaderReq()
        unpacked = struct.unpack(CamHqkzHeaderReq.fmt, buff[:CamHqkzHeaderReq.size])
        header.init(unpacked)
        return header

    def getstr(self):
        return (CamHqkzHeaderReq.fmt,self.market_code, self.hqkz_date ,self.hqkz_time)

class CamZqdmInfoHeaderReq:
    fmt = '<3s2i'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.market_code = ''
        self.hqkz_date = 0
        self.hqkz_time = 0

    def init(self,tuple):
        self.market_code = tuple[0]
        self.hqkz_date = tuple[1]
        self.hqkz_time = tuple[2]

    @staticmethod
    def frombuffer(buff):
        header = CamZqdmInfoHeaderReq()
        unpacked = struct.unpack(CamZqdmInfoHeaderReq.fmt, buff[:CamZqdmInfoHeaderReq.size])
        header.init(unpacked)
        return header

    def getstr(self):
        return (CamZqdmInfoHeaderReq.fmt,self.market_code, self.hqkz_date ,self.hqkz_time)

class struct_CamZqdmInfoHeaderReq(Structure):
    _pack_ =1
    _fields_ = [
        ('market_code', c_char*3),  #
        ('hqkz_date', c_int),  #
        ('hqkz_time', c_int),  #
    ]

class SSHQ:
    fmt = '<22s4i2q44i'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.code = ''
        self.last = 0
        self.open = 0
        self.high = 0
        self.low = 0
        self.total_volume = 0
        self.total_amount = 0
        self.total_trade_count = 0
        self.position = 0
        self.buy_price = []
        self.buy_volume = []
        self.sell_price = []
        self.sell_volume = []
        self.date = 0
        self.time = 0

    def init(self, tuple):
        self.code = tuple[0]
        self.last = tuple[1]
        self.open = tuple[2]
        self.high = tuple[3]
        self.low = tuple[4]
        self.total_volume = tuple[5]
        self.total_amount = tuple[6]
        self.total_trade_count = tuple[7]
        self.position = tuple[8]
        self.buy_price = []
        self.buy_volume = []
        self.sell_price = []
        self.sell_volume = []
        self.date = tuple[49]
        self.time = tuple[50]

    @staticmethod
    def frombuffer(buff):
        header = SSHQ()
        unpacked = struct.unpack(SSHQ.fmt, buff[:SSHQ.size])
        header.init(unpacked)
        return header

    def getstr(self):
        return (SSHQ.fmt, str(self.code).strip('\x00'), self.last, self.open, self.high, self.low
                , self.total_volume, self.total_amount, self.total_trade_count, self.position,
                self.date,self.time)

class struct_SSHQ(Structure):
    _pack_ =1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('last', c_int),  #
        ('open', c_int),  #
        ('high', c_int),  #
        ('low', c_int),  #
        ('total_volume', c_longlong),  # type
        ('total_amount', c_longlong),  #
        ('total_trade_count', c_int),  #
        ('position', c_int),  #
        ('buy_price', c_int*10),  #
        ('buy_volume', c_int*10),  #
        ('sell_price', c_int*10),  #
        ('sell_volume', c_int*10),  #
        ('date', c_int),  #
        ('time', c_int),  #
    ]

class ZQDMInfo:
    fmt = '<22s60s16sBH4iBiB2iB'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.code = ''
        self.name = ''
        self.pinyin_name = ''
        self.type = 0
        self.volume_unit = 0
        self.pre_close = 0
        self.high_limit = 0
        self.low_limit = 0
        self.price_digit = 0
        self.price_divide = 0
        self.intrest = 0
        self.crd_flag = 0
        self.pre_position = 0
        self.pre_settle_price = 0
        self.ext_type = 0

    def init(self, tuple):
        self.code = tuple[0]
        self.name = tuple[1]
        self.pinyin_name = tuple[2]
        self.type = tuple[3]
        self.volume_unit = tuple[4]
        self.pre_close = tuple[5]
        self.high_limit = tuple[6]
        self.low_limit = tuple[7]
        self.price_digit = tuple[8]
        self.price_divide =tuple[9]
        self.intrest = tuple[10]
        self.crd_flag = tuple[11]
        self.pre_position =tuple[12]
        self.pre_settle_price = tuple[13]
        self.ext_type = tuple[14]

    @staticmethod
    def frombuffer(buff):
        header = ZQDMInfo()
        unpacked = struct.unpack(ZQDMInfo.fmt, buff[:ZQDMInfo.size])
        header.init(unpacked)
        return header

    def getstr(self):
        # print str(self.code).strip('\x00'), str(self.name).strip('\x00')
        return (ZQDMInfo.fmt, str(self.code).strip('\x00'), str(self.name).strip('\x00'), str(self.pinyin_name).strip('\x00'), self.type, self.volume_unit
                , self.pre_close, self.high_limit, self.low_limit, self.price_digit,
                self.price_divide,self.intrest,self.crd_flag,self.pre_position,self.pre_settle_price,self.ext_type)

class MBInfo:
    fmt = '<22s60s24s60s24sB'
    size = struct.calcsize(fmt)

    def __init__(self):
        self.code = ''
        self.name_now = ''
        self.pinyin_name_now = ''
        self.name_old = ''
        self.pinyin_name_old = ''
        self.type = 0

    def init(self, tuple):
        self.code = tuple[0]
        self.name_now = tuple[1]
        self.pinyin_name_now = tuple[2]
        self.name_old = tuple[3]
        self.pinyin_name_old = tuple[4]
        self.type = tuple[5]

    @staticmethod
    def frombuffer(buff):
        header = MBInfo()
        unpacked = struct.unpack(MBInfo.fmt, buff[:MBInfo.size])
        header.init(unpacked)
        return header

    # .decode('UTF-8').encode('UTF-8'),
    def getstr(self):
        # import array
        arr = self.name_now.strip('\x00')
        print arr
        return [MBInfo.fmt, str(self.code).strip('\x00'), arr,
                str(self.pinyin_name_now).strip('\x00'),
                str(self.name_old).strip('\x00'), str(self.pinyin_name_old).strip('\x00'),str(self.type)]

def prn_obj(obj):
    return ','.join(['%s:%s' % item for item in obj.__dict__.items()])

def PrintStuct(qt):

    tmpstr = str(qt.__class__)
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+ str(qt.__getattribute__(name))+','

    # print tmpstr
    return tmpstr

class myMbInfo(Structure):
    _pack_ =1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('name_now', c_char * 60),  # 股票名称
        ('pinyin_name_now', c_char * 24),  # pin yin
        ('name_old', c_char * 60),  # 股票old名称
        ('pinyin_name_old', c_char * 24),  # old pin yin
        ('type', c_ubyte),  # type
        ('blockid', c_int),  # type
    ]

class BLOCKHQ(Structure):
    _pack_ =1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('last', c_int),  #
        ('open', c_int),  #
        ('high', c_int),  #
        ('low', c_int),  #
        ('total_volume', c_longlong),  # type

        ('total_amount', c_longlong),  #
        ('pchTopStockCode', c_char * 22),  #
        ('StockNum', c_ushort),  #
        ('UpNum', c_ushort),  #
        ('DownNum', c_ushort),  #
        ('StrongNum', c_ushort),  #
        ('WeakNum', c_ushort),  #
        ('ZGB', c_longlong),  #
        ('LTG', c_longlong),  #
        ('LTSZ', c_longlong),  #
        ('ZSZ', c_longlong),  #
        ('date', c_int),  #
        ('time', c_int),  #
    ]

class struct_xgsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('name', c_char * 60),  # 股票代码
        ('market_type', c_int8),  #
        ('issue_price', c_int),  #
        ('apply_share', c_int),  #
        ('price_digit', c_int8),  #
        ('price_divide', c_int8),  # type

        ('date', c_int),  #
        ('id', c_char * 15),  #
        ('issue_type', c_int8),  #
    ]

class Struct_ZQDMInfo(Structure):
    fmt = '<22s60s16sBH4iBiB2iB'
    size = struct.calcsize(fmt)
    _pack_ = 1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('name', c_char * 60),  #
        ('pinyin_name', c_char * 16),  #
        ('type', c_byte),  #
        ('volume_unit', c_short),  #
        ('pre_close', c_int),  # type
        ('high_limit', c_int),  #
        ('low_limit', c_int),  #
        ('price_digit', c_int),  #
        ('price_divide', c_byte),  #
        ('intrest', c_int),  #
        ('crd_flag', c_byte),  #
        ('pre_position', c_int),  #
        ('pre_settle_price', c_int),  #
        ('ext_type', c_byte),  #
    ]

class SSZS(Structure):
    _pack_ = 1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('last', c_int),  #
        ('open', c_int),  #
        ('high', c_int),  #
        ('low', c_int),  #
        ('total_volume', c_longlong),  # type

        ('total_amount', c_longlong),  #
        ('date', c_int),  #
        ('time', c_int),  #
    ]

class FunFlow(Structure):
    _pack_ =1
    _fields_ = [
        ('code', c_char * 22),  # 股票代码
        ('trade_cnt_buy', c_int*4),  #
        ('trade_cnt_sell', c_int*4),  #
        ('volume_buy1', c_longlong),  #
        ('volume_buy2', c_longlong),  #
        ('volume_buy3', c_longlong),  #
        ('volume_buy4', c_longlong),  #
        ('volume_sell1', c_longlong),  #
        ('volume_sell2', c_longlong),  #
        ('volume_sell3', c_longlong),  #
        ('volume_sell4', c_longlong),  #
        ('amount_buy1', c_longlong),  #
        ('amount_buy2', c_longlong),  #
        ('amount_buy3', c_longlong),  #
        ('amount_buy4', c_longlong),  #
        ('amount_sell1', c_longlong),  #
        ('amount_sell2', c_longlong),  #
        ('amount_sell3', c_longlong),  #
        ('amount_sell4', c_longlong),  #
        ('date', c_int),  #
        ('time', c_int),  #
    ]