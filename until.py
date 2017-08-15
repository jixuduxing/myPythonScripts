# -*- coding: UTF-8 -*-
from buffereader import buffereader

def uchar_checksum(data, byteorder='little'):
    '''''
    char_checksum 按字节计算校验和。每个字节被翻译为无符号整数
    @param data: 字节串
    @param byteorder: 大/小端
    '''
    length = len(data)
    checksum = 0
    datalen = len(data)
    pos = 0
    reader = buffereader( data)
    while datalen >1:
        intshort = reader.readshort()
        # int.from_bytes(data[pos:pos + 2], byteorder, signed=False)
        checksum += intshort
        checksum &= 0xFFFFFFFF  # 强制截断
        datalen = datalen -2

    if datalen == 1:
        intchar = reader.readbyte()
        # intchar = int.from_bytes(data[0:1], byteorder, signed=False)
        checksum += intchar
        checksum &= 0xFFFFFFFF  # 强制截断

    checksum = (checksum>>16 ) + (checksum &0xffff)
    checksum += (checksum>>16)
    checksum &= 0xFFFFFFFF  # 强制截断
    checksum = ~checksum
    checksum &= 0xffff
    # print 'checksum',checksum
    return checksum