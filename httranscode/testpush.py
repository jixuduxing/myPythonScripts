# -*- coding: UTF-8 -*-
#从主站获取数据

from htclient import *
import threading

import logging
import os

from util.until import getCurrentFileName, InitLog,uchar_checksum

curpath = os.path.dirname(__file__)
curfilename = getCurrentFileName()

InitLog(curpath,'testpush')

def testpush():
    # port = 13000
    # ip = '121.43.72.79'
    port = 23456
    ip = '115.159.205.150'

    client = htclient()
    client.connect(ip, port)
    client.request10000(10000,1,3,1,1,0,['SZ300059','SH600837','SH000001'])
    index = 0
    t = threading.Thread(target=htclient.keepconn, args=(client,))
    t.start()
    while True:
        datarecv,datalen,type = client.recvhead()
        if datalen:
            # print 'type',type
            bodyrecv = client.recvbody(datalen)
            if len(bodyrecv):
                if type != 10001:
                    continue
                print time.asctime()
                itemlist, totalsize = client.parsebody(type, bodyrecv)
                print  itemlist,totalsize


testpush()

