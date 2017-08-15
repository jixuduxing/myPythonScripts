# -*- coding: UTF-8 -*-
from array import array

print str(123)
nums=[1, 3, 5, 7, 9, 11, 13];
#列表转为字符串
print str(nums)

print str( [0x32, 0x31, 0xe5 , 0x9b , 0xbd , 0xe5 , 0x80 , 0xba , 0xe2 , 0x91 , 0xba , 0x00] )
# bytearray.
tt =  bytearray.fromhex("32 31 e5 9b bd e5 80 ba e2 91 ba 00")
print tt

data = [0x32, 0x31, 0xe5 , 0x9b , 0xbd , 0xe5 , 0x80 , 0xba , 0xe2 , 0x91 , 0xba , 0x00]
arr = array('B',data)
# for i in data:
#     arr.append(i)
print arr.tostring()
# print str(arr)
# print arr.decode('utf-8')
# .strip('\x00')