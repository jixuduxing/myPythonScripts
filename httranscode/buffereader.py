import struct


class buffereader:
    def __init__(self,data):
        self.data_ = data
        self.pos_ = 0

    def readint(self):
        unpackdata = struct.unpack( '<i',self.data_[self.pos_:self.pos_+4] )
        self.pos_ += 4
        return unpackdata[0]

    def readshort(self):
        unpackdata = struct.unpack( '<H',self.data_[self.pos_:self.pos_+2] )
        self.pos_ += 2
        return unpackdata[0]

    def readchar(self):
        unpackdata = struct.unpack( '<c',self.data_[self.pos_:self.pos_+1] )
        self.pos_ += 1
        return unpackdata[0]

    def readbyte(self):
        unpackdata = struct.unpack( '<B',self.data_[self.pos_:self.pos_+1] )
        self.pos_ += 1
        return unpackdata[0]

    def readbytes(self,readsize):
        buff = self.data_[self.pos_:self.pos_+readsize]
        self.pos_ += readsize
        return buff

    def readtuple(self,fmt):
        needsize = struct.calcsize(fmt)
        unpackdata = struct.unpack(fmt,self.data_[self.pos_:self.pos_+needsize])
        self.pos_ += needsize
        return unpackdata

    def readstring(self):
        stringlen = self.readshort()
        string = self.data_[ self.pos_:self.pos_+stringlen ]
        self.pos_ += stringlen
        return str(string)
