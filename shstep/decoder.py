# -*- coding: UTF-8 -*-

from template import *
from streamdecoder import *

class fastdecoder:
    def __init__(self,curtemplate):
        # self.pmap
        self.thiscurtemplate =curtemplate
        self.curmsgid = 0
        pass

    #生成bits数组
    @staticmethod
    def generatepmapbits(pmap):
        temppmap = pmap
        tempmap2 = 0
        mapbits = []
        for ch in pmap:
            i = ord(ch)
            mapbits.append( "{:b}".format(i))
        print mapbits

    def decodermsg(self,decod):
        print 'msgid', self.curmsgid
        bfind, curmessage = self.thiscurtemplate.getmessage(self.curmsgid)
        if bfind == False:
            print "data can not parse,unknown msgid", self.curmsgid
            return
        # if len(curmessage.Fields) > len(self.mapbits):
        #     raise "pmap not match"
        #     return
        self.seq = 1
        for field in curmessage.Fields[1:]:
            # print field.id,field.needplace(),field.seq
            if field.needplace():
                if field.type == itemtype.type_else:
                    print "decoderdata fail for field:1", 'test', field.id, field.seq
                    return
                if not streamdecoder.ispresent(self.seq, self.pmap):
                    print 'no', self.seq, field.id
                    self.seq += 1
                    continue
                self.seq += 1
                print field.id, self.seq
                dataret, flag = self.read(field,decod, field.option)
                if field.option:
                    if not flag:  # means null
                        if field.op == optype.op_constant:  # constant can not be null
                            raise Exception("this type can not be null", field.type, field.option)  # ,field.id
                        else:
                            print "data is null", field.id
                            continue
                print "data: ", field.id,'=', dataret, self.seq
            elif field.op in (optype.op_no, optype.op_delta):  # 不占位  数据存在
                if field.type == itemtype.type_else:
                    print "decoderdata fail for field2:", field.id, field.seq
                    return
                dataret, flag = self.read(field,decod, field.option)
                if field.option:
                    if not flag:  # means null
                        print "data is null", field.id
                        continue
                print "data2: ", field.id,'=', dataret
        pass

    def decoderdata(self,data):
        decod = streamdecoder(data)
        msgid = 0
        while decod.datanoprocess() >0:
            self.pmap = decod.readpmap()
            fastdecoder.generatepmapbits(self.pmap)
            # print 'pmap',pmap
            if streamdecoder.ispresent(0, self.pmap):
                msgid,i = decod.readint()
                self.curmsgid = msgid
            else:
                print "no msgid"
            self.decodermsg(decod)

    def read(self,field,decod,isoption):
        if field.type ==itemtype.type_int32:
            if isoption:
                return decod.readint_optional()
            return decod.readint()
        elif field.type ==itemtype.type_uint32:
            if isoption:
                return decod.readuint_optional()
            return decod.readuint()
        elif field.type ==itemtype.type_length:
            if isoption:
                return decod.readuint_optional()
            return decod.readuint()
        elif field.type ==itemtype.type_uint64:
            if isoption:
                return decod.readuint64_optional()
            return decod.readuint64()
        elif field.type ==itemtype.type_int64:
            if isoption:
                return decod.readint64_optional()
            return decod.readint64()
        elif field.type == itemtype.type_acsii:
            if isoption:
                return decod.read_string_acii_optional()
            return decod.read_string_acii()
        elif field.type == itemtype.type_decimal:
            if isoption:
                exponent, mantissa,flag = decod.readdecimal_optional()
                return (exponent,mantissa),flag
            exponent, mantissa, i = decod.readdecimal()
            return (exponent,mantissa) * mantissa, i
        elif field.type == itemtype.type_byteVector:
            if isoption:
                return decod.readbyteVector_optional()
            return decod.readbyteVector()
        elif field.type == itemtype.type_sequence:
            return self.readsequence(field,decod)

    def readsequence(self,fieldseq,decod):
        if len(fieldseq.items ) == 0:
            return fieldseq.name +" wrong",0
        sequencelen = 0
        if fieldseq.needplace():#占位
            if not streamdecoder.ispresent(self.seq, self.pmap): #不存在
                if fieldseq.op == optype.op_copy:
                    sequencelen = fieldseq.items[0].prevalue
                else:
                    raise "error readsequence  no length!!!!"
            else:
                sequencelen, flag = self.read(fieldseq.items[0],decod, fieldseq.option)
                self.seq += 1
        else:
            sequencelen, flag = self.read(fieldseq.items[0],decod, fieldseq.option)
        sequncedecod = sequencedecoder()

        fieldseq.items[0].prevalue = sequencelen
        # sequencelen,i = self.readint()
        print "enter sequence", fieldseq.name,sequencelen
        return sequncedecod.decode(decod,sequencelen,fieldseq)

class sequencedecoder:
    def __init__(self):
        pass
    def read(self,field,decod,isoption):
        if field.type ==itemtype.type_int32:
            if isoption:
                return decod.readint_optional()
            return decod.readint()
        elif field.type ==itemtype.type_uint32:
            if isoption:
                return decod.readuint_optional()
            return decod.readuint()
        elif field.type ==itemtype.type_length:
            if isoption:
                return decod.readuint_optional()
            return decod.readuint()
        elif field.type ==itemtype.type_uint64:
            if isoption:
                return decod.readuint64_optional()
            return decod.readuint64()
        elif field.type ==itemtype.type_int64:
            if isoption:
                return decod.readint64_optional()
            return decod.readint64()
        elif field.type == itemtype.type_acsii:
            if isoption:
                return decod.read_string_acii_optional()
            return decod.read_string_acii()
        elif field.type == itemtype.type_decimal:
            if isoption:
                exponent, mantissa,flag = decod.readdecimal_optional()
                return (exponent,mantissa),flag
            exponent, mantissa, i = decod.readdecimal()
            return (exponent,mantissa) * mantissa, i
        elif field.type == itemtype.type_byteVector:
            if isoption:
                return decod.readbyteVector_optional()
            return decod.readbyteVector()
        elif field.type == itemtype.type_sequence:
            return self.readsequence(field,decod)

    def readsequence(self,fieldseq,decod):
        if len(fieldseq.items ) == 0:
            return fieldseq.name +" wrong",0
        sequencelen = 0
        if fieldseq.needplace():#占位
            if not streamdecoder.ispresent(self.seq, self.pmap): #不存在
                if fieldseq.op == optype.op_copy:
                    sequencelen = fieldseq.items[0].prevalue
                else:
                    raise "error readsequence  no length!!!!"
            else:
                sequencelen, flag = self.read(fieldseq.items[0],decod, fieldseq.option)
                self.seq += 1
        else:
            sequencelen, flag = self.read(fieldseq.items[0],decod, fieldseq.option)
        sequncedecod = sequencedecoder()

        fieldseq.items[0].prevalue = sequencelen
        # sequencelen,i = self.readint()
        print "enter sequence", fieldseq.name,sequencelen
        return sequncedecod.decode(decod,sequencelen,fieldseq)

    def decode(self,decoder,sequencelen,fieldseq):
        for i in range(0,sequencelen):
            self.pmap = decoder.readpmap()
            generatepmapbits(self.pmap)
            # print 'pmap', pmap
            self.seq = 0
            for field in fieldseq.items[0:]:
                print field.id,field.needplace(),field.seq
                if field.needplace():
                    if field.type == itemtype.type_else:
                        print "decoderdata fail for field:1", 'test', field.id, field.seq
                        return fieldseq.name +" wrong", 0

                    if not streamdecoder.ispresent(self.seq,self.pmap):
                        # print 'no',seq,field.id
                        self.seq += 1
                        continue
                    self.seq += 1
                    dataret, flag = self.read(field,decoder, field.option)
                    if field.option:
                        if not flag:  # means null
                            if field.op == optype.op_constant:  # constant can not be null
                                raise Exception("this type can not be null", field.type, field.option)  # ,field.id
                            else:
                                print "data is null", field.id
                                continue
                    print "data3: ", field.id,'=', dataret, self.seq
                elif field.op in (optype.op_no, optype.op_delta):  # 不占位  数据存在
                    if field.type == itemtype.type_else:
                        print "decoderdata fail for field2:", field.id, field.seq
                        return fieldseq.name +" wrong",0
                    dataret, flag = self.read(field,decoder, field.option)
                    # if field.option:
                    #     if not flag:  # means null
                    #         print "data is null", field.id
                    #         continue
                    print "data4: ", field.id,'=', dataret
        return "leave sequence"+ fieldseq.name, 0

        # print "leave sequence", fieldseq.name, sequencelen

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
    # datafile = io.open('E:/tmp/shrecord_2018-06-07151852_bak','rb')
    data = datafile.read()
    # print type(data)
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
