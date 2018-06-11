# -*- coding: UTF-8 -*-

from template import *
import decoder

#生成bits数组
def generatepmapbits(pmap):
    temppmap = pmap
    tempmap2 = 0
    mapbits = []
    for ch in pmap:
        i = ord(ch)
        mapbits.append( "{:b}".format(i))
    print mapbits

#字符串解析
class streamdecoder:
    stopbit = 0x80
    databits = 0x7F
    signbit =  0x40

    def __init__(self,data):
        self.data = data
        self.pos = 0
        self.datalen = len(data)

    def datanoprocess(self):
        return self.datalen - self.pos

    def readint8(self):
        rint = int()
        firstch = 0
        for i in range(0, 2):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if (ch & streamdecoder.signbit):
                        rint = -1
                elif i == 1:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 1:
                            raise "readint8  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint8  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readint8 buffer end"
                break
            raise "readint8 no stop bit"
    def readdecimal(self):
        exponent,i1 = self.readint()
        mantissa,i2 = self.readint64()
        return exponent,mantissa,i1+i2

    def readdecimal_optional(self):
        exponent, flag1 = self.readint_optional()
        if flag1 == False:
            return 0,0,False
        mantissa, i2 = self.readint64()
        # exponent, mantissa,i = self.readdecimal()
        # if exponent >0:
        #     exponent -= 1
        return exponent, mantissa,True

    # return int,notempty?
    def readuint_optional(self):
        if self.pos < self.datalen:
            ch = ord(self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos +=1
                return 0,False # False means NULL
        else:
            raise "readuint_optional buffer end"
        rint,i = self.readuint()
        if rint >0:
            rint -= 1
        return rint,True

    # return int,notempty?
    def readuint64_optional(self):
        if self.pos < self.datalen:
            ch = ord(self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos +=1
                return 0, False
        else:
            raise "readuint64_optional buffer end"
        rint,i = self.readuint64()
        if rint >0:
            rint -= 1
        return rint,True

    # return int,notempty?
    def readint_optional(self):
        if self.pos < self.datalen:
            ch = ord(self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos +=1
                return 0, False
        else:
            raise "readint_optional buffer end"
        rint,i = self.readint()
        if rint >0:
            rint -= 1
        return rint,True

    # return int,notempty?
    def readint64_optional(self):
        if self.pos < self.datalen:
            ch = ord(self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos +=1
                return 0, False
        else:
            raise "readint64_optional buffer end"
        rint,i = self.readint64()

        if rint >0:
            rint -= 1
        return rint,True

    # return int,bytecnt
    def readuint(self):
        rint = 0
        firstch = 0
        for i in range(0,5):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                if i == 0:
                    firstch = ch
                elif i == 4:
                    if (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readuint  over flow"
                rint <<= 7
                rint |=(ch& streamdecoder.databits)

                self.pos += 1

                if ch & streamdecoder.stopbit >0:
                    return rint,i
            else:
                raise "readuint buffer end"

        raise "readuint no stop bit"

    # return int,bytecnt
    def readuint64(self):
        rint = 0
        firstch = 0
        for i in range(0,10):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                if i == 0:
                    firstch = ch
                elif i == 9:
                    if (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readuint64  over flow"
                rint <<= 7
                rint |=(ch& streamdecoder.databits)

                self.pos += 1
                if ch & streamdecoder.stopbit >0:
                    return rint,i
            else:
                raise "readuint64 buffer end"

        raise "readuint64 no stop bit"

    # return int,bytecnt
    def readint(self):
        rint = 0
        firstch = 0
        for i in range(0,5):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if( ch &streamdecoder.signbit):
                        rint = -1
                elif i == 4:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 7:
                            raise "readint  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint,i
            else:
                raise "readint buffer end"
                break
        raise "readint no stop bit"

    # return int,bytecnt
    def readint64(self):
        rint = 0
        firstch = 0
        for i in range(0,10):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if( ch &streamdecoder.signbit):
                        rint = -1
                elif i == 9:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 7:
                            raise "readint64  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint64  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)

                self.pos += 1
                if ch & streamdecoder.stopbit > 0:
                    return rint,i
            else:
                raise "readint64 buffer end"
                break
        raise "readint64 no stop bit"
    #return str,bytecnt
    def read_string_acii(self):
        retstr = []
        i = 0
        while 1:
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    retstr.append(chr(ch&streamdecoder.databits))
                    return str(retstr),i
                retstr.append(chr(ch))
                i += 1
            else:
                raise "read_string_acii buffer end"
    #return str,notempty?
    def read_string_acii_optional(self):
        if self.pos < self.datalen:
            ch = ord(self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos +=1
                return "",False #FC_NULL_VALUE
            elif ch == 0:
                self.pos +=1
                if self.pos < self.datalen:
                    ch = self.data[self.pos]
                    if ch == streamdecoder.stopbit:
                        self.pos += 1
                        return "", True #FC_EMPTY_VALUE
                    else:
                        self.pos -= 1
                else:
                    raise "read_string_acii_optional buffer end"

        else:
            raise "read_string_acii_optional buffer end"
        retstr,i =  self.read_string_acii()
        return retstr,True

    def readpmap(self):
        rint = 0
        firstch = 0
        i = 0
        beginpos = self.pos
        for i in range(0, 100):
            if self.pos < self.datalen:
                ch = ord(self.data[self.pos])
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return self.data[beginpos:self.pos]
            else:
                raise Exception("readpmap buffer end")

        print self.data[beginpos:(self.pos+1)]
        raise Exception("readpmap no stop bit ",i)

    def readbyteVector_optional(self):
        rlen,flag = self.readuint64_optional()
        if not flag:
            return "",flag
        rdata = self.data[self.pos:self.pos+rlen]
        self.pos += rlen
        return (rlen,rdata),True
        pass

    def readbyteVector(self):
        rlen, i = self.readuint64()
        if rlen == 0:
            return "", i
        rdata = self.data[self.pos:self.pos + rlen]
        self.pos += rlen
        return (rlen,rdata), i+rlen
        pass


    @staticmethod
    def ispresent( seq, pmap):
        div = seq / 7
        rem = seq % 7
        if div >= len(pmap):
            return False
        tmp = ord(pmap[div]) & (0x40 >> rem)
        if tmp != 0:
            return True

        return False



#字节数组解析
class bufferdecoder:
    stopbit = 0x80
    databits = 0x7F
    signbit = 0x40

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.datalen = len(data)

    def datanoprocess(self):
        return self.datalen - self.pos

    def readint8(self):
        rint = int()
        firstch = 0
        for i in range(0, 2):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if (ch & streamdecoder.signbit):
                        rint = -1
                elif i == 1:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 1:
                            raise "readint8  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint8  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readint8 buffer end"
                break
            raise "readint8 no stop bit"

    def readdecimal(self):
        exponent, i = self.readint()
        mantissa, i = self.readint64()
        return exponent, mantissa

    def readdecimal_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return 0, 0, False  # False means NULL
        else:
            raise "readuint_optional buffer end"
        exponent, mantissa = self.readdecimal()
        if exponent > 0:
            exponent -= 1
        return exponent, mantissa, True

    # return int,notempty?
    def readuint_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return 0, False  # False means NULL
        else:
            raise "readuint_optional buffer end"
        rint, i = self.readuint()
        if rint > 0:
            rint -= 1
        return rint, True

    # return int,notempty?
    def readuint64_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return 0, False
        else:
            raise "readuint64_optional buffer end"
        rint, i = self.readuint64()
        if rint > 0:
            rint -= 1
        return rint, True

    # return int,notempty?
    def readint_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return 0, False
        else:
            raise "readint_optional buffer end"
        rint, i = self.readint()
        if rint > 0:
            rint -= 1
        return rint, True

    # return int,notempty?
    def readint64_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return 0, False
        else:
            raise "readint64_optional buffer end"
        rint, i = self.readint64()

        if rint > 0:
            rint -= 1
        return rint, True

    # return int,bytecnt
    def readuint(self):
        rint = 0
        firstch = 0
        for i in range(0, 5):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                if i == 0:
                    firstch = ch
                elif i == 4:
                    if (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readuint  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)

                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readuint buffer end"

        raise "readuint no stop bit"

    # return int,bytecnt
    def readuint64(self):
        rint = 0
        firstch = 0
        for i in range(0, 10):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                if i == 0:
                    firstch = ch
                elif i == 9:
                    if (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readuint64  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)

                self.pos += 1
                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readuint64 buffer end"

        raise "readuint64 no stop bit"

    # return int,bytecnt
    def readint(self):
        rint = 0
        firstch = 0
        for i in range(0, 5):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if (ch & streamdecoder.signbit):
                        rint = -1
                elif i == 4:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 7:
                            raise "readint  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readint buffer end"
                break
        raise "readint no stop bit"

    # return int,bytecnt
    def readint64(self):
        rint = 0
        firstch = 0
        for i in range(0, 10):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                if i == 0:
                    firstch = ch
                    if (ch & streamdecoder.signbit):
                        rint = -1
                elif i == 9:
                    if firstch & streamdecoder.signbit:
                        if (firstch & streamdecoder.databits) >> 4 != 7:
                            raise "readint64  over flow1"
                    elif (firstch & streamdecoder.databits) >> 4 != 0:
                        raise "readint64  over flow"
                rint <<= 7
                rint |= (ch & streamdecoder.databits)

                self.pos += 1
                if ch & streamdecoder.stopbit > 0:
                    return rint, i
            else:
                raise "readint64 buffer end"
                break
        raise "readint64 no stop bit"

    # return str,bytecnt
    def read_string_acii(self):
        retstr = []
        i = 0
        while 1:
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    retstr.append(chr(ch & streamdecoder.databits))
                    return str(retstr), i
                retstr.append(chr(ch))
                i += 1
            else:
                raise "read_string_acii buffer end"

    # return str,notempty?
    def read_string_acii_optional(self):
        if self.pos < self.datalen:
            ch = (self.data[self.pos])
            if ch == streamdecoder.stopbit:
                self.pos += 1
                return "", False  # FC_NULL_VALUE
            elif ch == 0:
                self.pos += 1
                if self.pos < self.datalen:
                    ch = self.data[self.pos]
                    if ch == streamdecoder.stopbit:
                        self.pos += 1
                        return "", True  # FC_EMPTY_VALUE
                    else:
                        self.pos -= 1
                else:
                    raise "read_string_acii_optional buffer end"

        else:
            raise "read_string_acii_optional buffer end"
        retstr, i = self.read_string_acii()
        return retstr, True

    def readpmap(self):
        rint = 0
        firstch = 0
        i = 0
        beginpos = self.pos
        for i in range(0, 100):
            if self.pos < self.datalen:
                ch = (self.data[self.pos])
                rint <<= 7
                rint |= (ch & streamdecoder.databits)
                self.pos += 1

                if ch & streamdecoder.stopbit > 0:
                    return rint
            else:
                raise Exception("readpmap buffer end")
        print self.data[beginpos:(self.pos + 1)]
        raise Exception("readpmap no stop bit ", i)

    def readbyteVector_optional(self):
        rlen, flag = self.readuint64_optional()
        if not flag:
            return "", flag
        rdata = self.data[self.pos:self.pos + rlen]
        self.pos += rlen
        return rdata, True
        pass

    def readbyteVector(self):
        rlen, i = self.readuint64()
        if rlen == 0:
            return "", i
        rdata = self.data[self.pos:self.pos + rlen]
        self.pos += rlen
        return rdata, i + rlen
        pass

    def read(self, field, isoption):
        if field.type == itemtype.type_int32:
            if isoption:
                return self.readint_optional()
            return self.readint()
        elif field.type == itemtype.type_uint32:
            if isoption:
                return self.readuint_optional()
            return self.readuint()
        elif field.type == itemtype.type_length:
            if isoption:
                return self.readuint_optional()
            return self.readuint()
        elif field.type == itemtype.type_uint64:
            if isoption:
                return self.readuint64_optional()
            return self.readuint64()
        elif field.type == itemtype.type_int64:
            if isoption:
                return self.readint64_optional()
            return self.readint64()
        elif field.type == itemtype.type_acsii:
            if isoption:
                return self.read_string_acii_optional()
            return self.read_string_acii()
        elif field.type == itemtype.type_decimal:
            if isoption:
                return self.readdecimal_optional()
            return self.readdecimal()
        elif field.type == itemtype.type_byteVector:
            if isoption:
                return self.readbyteVector_optional()
            return self.readbyteVector()

# 7f7f7f 7ffe
testint = 1200
testint >>= 1
print testint >>1

if __name__ == '__main__':
    print 'template test'
    data = [0x7f,0x7f,0x7f,0x7f,0xfe]

    decoder = bufferdecoder(data)
    print decoder.readint()

    decoder2 = streamdecoder(data)
    print decoder.readint()