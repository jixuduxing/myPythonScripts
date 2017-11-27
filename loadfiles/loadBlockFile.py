# -*- coding: utf-8 -*-
#加载大智慧板块映射文件
import io
import codecs
import sys

import MySQLdb

db = MySQLdb.connect("172.190.28.217","root","password","testdb" ,charset="utf8")
# 使用cursor()方法获取操作游标
cursor = db.cursor()
cursor.execute('SET NAMES UTF8')

file = codecs.open('E:/tmp/block_list_hy.txt',encoding="utf-8")
i = 0
lines = file.readlines()

strsql = "insert into bkmap(blockcode,stockcode,blockname) values(%s,%s,%s);"

listcode = []
for line in lines[1:]:
    param = ()
    lines2 = line.split('|')
    print lines2[0]
    for code in lines2[4:]:
        curparam = ((lines2[0],code,lines2[1]),)
        param = param+ curparam
    if len(param):
        print param
        print cursor.executemany(strsql, param)

db.commit()
db.close()

# sortedlist = sorted(listcode)
# for item in sortedlist:
#     print item

testlist = [9,7,8,6,8,2,5,1,5,3,6,8]
print sorted(testlist)
