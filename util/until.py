# -*- coding: UTF-8 -*-

import logging
import os


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

def getCurrentFileName( ):
    filename = os.path.basename(__file__)
    return os.path.splitext(filename)[0]

def InitLog(curpath,curfilename):
    # curpath = os.path.dirname(__file__)
    # curfilename = getCurrentFileName()
    # print curpath, curfilename
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        # datefmt='%a, %d %b %Y %H:%M:%S.%f',
                        filename=curpath + '/../log/' + curfilename + '.txt',
                        filemode='w')
    # print curpath + '/../log/' + curfilename + '.txt'
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

