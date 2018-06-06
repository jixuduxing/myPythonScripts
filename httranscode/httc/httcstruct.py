# -*- coding: UTF-8 -*-
#海通数据结构
import struct

from ctypes import *

TCM_MSG_BOOT_CODE= 0x8668

TCR_HQKZ_RQST = 0x0001
TCM_ZQDMINFO_RQST = 0x0003
TCM_FLAGS_FIRST_PACKET = 0x01
TCM_FLAGS_MARKET_FIRST_PACKET = 0x02
TCM_IDLE_RQST = 0x00ff
TCM_IDLE_RPLY = 0x80ff
TCM_LOGIN_RQST = 0x0080
TCM_LOGIN_RPLY = 0x8080

TCM_ZQDM_INFO	=1
TCM_ZQDM_OTC	=2
TCM_ZQDM_SG		=3
TCM_ZQDM_XGSG	=4

HT_TC_VERSION = 0x020200

TCM_HQKZ_SSHQ = 1
TCM_HQKZ_SSZS = 2
TCM_HQKZ_ORDER_QUEUE = 3
TCM_HQKZ_STEP_TRADE = 4
TCM_HQKZ_SSHQHZEXT = 5
TCM_HQKZ_HZZXJC = 6
TCM_HQKZ_MARKET_STATUS = 7
TCM_HQKZ_MARKET_STATIC_INFO = 8
TCM_HQKZ_SSHQ_OTC =9
TCM_HQKZ_SSHQ_OTCZH =10
TCM_HQKZ_SSHQ_SOZH = 11
TCM_HQKZ_SSHQ_SG =12
TCM_HQKZ_SSQDHQ	=13 #千档行情
TCM_HQKZ_SSHQEXT =	14 #拓展动态行情
TCM_HQKZ_XGSG =	17	#申购信息
TCM_HQKZ_FunFlow = 18 #资金流
TCM_HQKZ_BLOCKHQ = 15

class TcMsgHeader(Structure):
    _pack_ =1
    _fields_ = [
        ('boot_code', c_ushort),  #
        ('checksum', c_ushort),  #
        ('length', c_ushort),  #
        ('cmd', c_ushort),  #
        ('seq_id', c_uint),  #
    ]

class TcLoginReq(Structure):
    _pack_ = 1
    _fields_ = [
        ('version', c_uint),  #
    ]



class TcmZqdmInfoReq(Structure):
    _pack_ =1
    _fields_ = [
        ('flags', c_ubyte),  #
        ('item_count', c_ubyte),  #
    ]

class TcmHqkzReq(Structure):
    _pack_ =1
    _fields_ = [
        ('flags', c_ubyte),  #
        ('item_count', c_ubyte),  #
    ]

class TcmZqdmInfoHeaderReq(Structure):
    _pack_ =1
    _fields_ = [
        ('market_code', c_char*3),  #
        ('zqdminfo_date', c_uint),  #
        ('zqdminfo_time', c_uint),  #
    ]
class TcmHqkzHeaderReq(Structure):
    _pack_ =1
    _fields_ = [
        ('market_code', c_char*3),  #
        ('zqdminfo_date', c_uint),  #
        ('zqdminfo_time', c_uint),  #
    ]