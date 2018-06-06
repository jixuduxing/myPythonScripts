# -*- coding: UTF-8 -*-

from template import *
from streamdecoder import *

class fastdecoder:
    def __init__(self,curtemplate):
        self.pmap = 0
        self.thiscurtemplate = curtemplate
        pass
    #生成bits数组
    def generatepmapbits(self):
        temppmap = self.pmap
        tempmap2 = 0
        self.mapbits = []
        for i in range(0, 100):
            self.mapbits.append(temppmap & 1)
            tempmap2 = temppmap >>1
            if tempmap2 ==0:
                break
            temppmap = tempmap2
            # if temppmap & 2
        self.mapbits.reverse()
        print self.mapbits

    def decoderdata(self,data):
        decod = streamdecoder(data)
        while decod.datanoprocess() >0:
            self.pmap = decod.readpmap()
            self.generatepmapbits()
            print 'pmap',self.pmap
            msgid,i = decod.readint()
            print 'msgid',msgid
            bfind,curmessage = self.thiscurtemplate.getmessage(msgid)
            if bfind == False:
                print "data can not parse,unknown msgid",msgid
                return
            # if len(curmessage.Fields) > len(self.mapbits):
            #     raise "pmap not match"
            #     return
            seq = 0
            for field in curmessage.Fields:
                # print field.id,field.needplace(),field.seq
                if field.needplace():
                    if field.type == itemtype.type_else:
                        print "decoderdata fail for field:1",'test',field.id,field.seq
                        return
                    seq += 1
                    if not self.ispresent(seq):
                        # print 'no',seq,field.id
                        continue
                    dataret,flag = decod.read(field.type,field.option)
                    if field.option:
                        if not flag :#means null
                            if field.type ==optype.op_constant:#constant can not be null
                                raise Exception("this type can not be null",field.type,field.option) #,field.id
                            else:
                                print "data is null",field.id
                                continue
                    print "data: ",field.id,dataret,seq
                elif field.op in (optype.op_no,optype.op_delta):#不占位  数据存在
                    if field.type == itemtype.type_else:
                        print "decoderdata fail for field2:",field.id,field.seq
                        return
                    dataret, flag = decod.read(field.type, False)
                    if field.option:
                        if not flag :#means null
                                print "data is null",field.id
                                continue
                    print "data2: ",field.id,dataret


    def ispresent(self,seq):
        if seq >= len(self.mapbits):
            print "seq wrong",seq
            return
            # raise "seq wrong"
        if self.mapbits[seq] !=0:
            return True
        return False

RAWDATA_ID = '96'
BODY_LENGTH_ID = '9'
RAWDATALENGTH_ID = '95'
SOH = '\x01'
class stepdecoder:
    def __init__(self,curtemplete):
        self.templete = curtemplete
        pass

    def decodedata(self,data):
        if len( data) <10:
            return -1
        if data[:2] != "8=":
            print data[:2]
            raise "wrong header"
        pos = 2
        for i in range(pos, len(data)):
            if data[i] == SOH:
                break
        if i == len(data) - 1:
            return -1
        value = data[pos:i]
        # print '8=', value
        pos = i+1
        while 1:
            for i in range(pos,len(data)):
                if data[i] == '=':
                    break
            if i == len(data) - 1:
                return -1
            id = data[pos:i]
            pos = i+1
            for i in range(pos, len(data)):
                if data[i] == SOH:
                    break
            if i == len(data) - 1:
                return -1
            value = data[pos: i]
            # print id, '=', value
            pos = i +1
            if id == BODY_LENGTH_ID:
                bodylen = int(value)
                print id, '=', value
                self.decodebody(data[pos: pos + bodylen])
                pos += bodylen
            elif id == '10':
                return pos

    def decodebody(self,data):
        if len( data) <10:
            return -1
        pos = 0
        rawdatasize = 0
        while 1:
            for i in range(pos,len(data)):
                if data[i] == '=':
                    break
            id = data[pos:i]
            pos = i+1

            if id != RAWDATA_ID:
                for i in range(pos,len(data)):
                    if data[i] == SOH:
                        break
                if i == len(data)-1:
                    return -1
                value = data[pos: i]
                pos = i+1
                # print id,'=', value
                if id == RAWDATALENGTH_ID:
                    rawdatasize = int(value)
            else:
                if rawdatasize >0:
                    print 'fast fast fast fast fast fast fast fast '
                    fastvalue = data[pos:pos+rawdatasize]
                    if fastvalue[:2] == "8=":
                        self.decodedata(fastvalue)
                        break
                    fastdecode = fastdecoder( self.templete)
                    fastdecode.decoderdata(fastvalue)
                    break
                else:
                    for i in range(pos, len(data)):
                        if data[i] == SOH:
                            break
                    if i == len(data) - 1:
                        return -1
                    value = data[pos: i]
                    # print id, '=', value

                            # decode = fastdecoder()

import io

if __name__ == '__main__':
    tem = template()
    tem.load('C:\Users\gao\PycharmProjects/test\shstep/template.xml')

    datafile = io.open('E:/tmp/shrecord_2018-05-2293845','rb')
    data = datafile.read()
    print "filedatalen: ",len(data)
    pos =0
    cnt = 0
    dec = stepdecoder(tem)
    while 1:
        iret = dec.decodedata(data[pos:])
        if iret <0:
            print "end"
            break
        cnt += 1
        print 'parsed len=',iret,pos,cnt
        pos += iret
