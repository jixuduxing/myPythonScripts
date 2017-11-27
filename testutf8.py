# -*- coding: UTF-8 -*-
from array import array

print str( [0x32, 0x31, 0xe5 , 0x9b , 0xbd , 0xe5 , 0x80 , 0xba , 0xe2 , 0x91 , 0xba , 0x00] )
# bytearray.
tt =  bytearray.fromhex("43 4f 4d 45 58 e9 bb 84 e9 87 91 31 37 31 30")
print tt
print int('e9',16)
#转换字节列表到数组 和string
data = [0x32, 0x31, 0xe5 , 0x9b , 0xbd , 0xe5 , 0x80 , 0xba , 0xe2 , 0x91 , 0xba , 0x00]
arr = array('B',data)
# for i in data:
#     arr.append(i)
print arr.tostring()
# print str(arr)
# print arr.decode('utf-8')
# .strip('\x00')


zw = '上工Ｂ股'
# zw = '三毛B股'
# chararray = array( 'B', zw )
chararray = array( 'B', zw.decode('utf-8').encode('GBK') )
print chararray

carray = array('B','Ｂ'.decode('utf-8').encode('GBK'))
print carray