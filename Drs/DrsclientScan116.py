# -*- coding: UTF-8 -*-

__author__ = 'gao'
import logging
from DrsClient import *
import os
import sys


def PrintQt(qt):
    tmpstr = ''
    for (name,type) in qt._fields_:
        tmpstr = tmpstr+name+':'+  str(qt.__getattribute__(name))+','
    #GBK编码转到utf8
    tmpstr =tmpstr.decode('GBK').encode('utf-8')
    logging.debug(tmpstr)
    print tmpstr

def getCurrentFileName( ):
    filename = os.path.basename(__file__)
    return os.path.splitext(filename)[0]

def TestDrs(ip,port,markets ):
    try:
        for market in markets:
            client = DrsClient()

            client.connect(ip,port)
            print market
            client.Register(market)

            client.RecvSnapShotAndHandleData(client.ParseData,PrintQt)
            client.Close()
        print 'over'
    except Exception,ex:
        traceback.print_exc()
        print Exception,":",ex,ip,port,markets
        exit()

if __name__ == "__main__":
    print "你好"
    curpath = os.path.dirname(__file__)
    curfilename = getCurrentFileName()
    print curpath,curfilename
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=curpath+'/../log/'+curfilename+ '.txt',
                filemode='w')
    print curpath+'/../log/'+curfilename+ '.txt'
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.info("test info")
    try:
        print 'begin work'
        TestDrs('114.80.234.116',21000,('HK','HKIN','HKI') )
        TestDrs('114.80.234.116',21001,('NASDAQ','AMEX','NYSE','NASDAQ1','NYSE1','AMEX1') )
        TestDrs('114.80.234.116',21002,('LME','NYBOT','TOCOM','IPE','COMEX','NYMEX','COBOT','SGX') )
        TestDrs('114.80.234.116',21003,('SHFE','DCE','CZCE','SGE','DCEINDEX','DCEOPTION','HKUSDCNHOP') )
        TestDrs('114.80.234.116',21004,('FOREX','UDI','CNYOFFS','CNYRATE','CNYFOREX') )
        TestDrs('114.80.234.116',21005,('JP','US1','US2','SIN','CRB','BDI') )
        TestDrs('114.80.234.116',21006,('HKCNYF','HKSTOCKF','HKMETALFS','HKINDEXF','HS','HSAHP','LME','FORPM','HKPM') )


        # client = DrsClient()
        #
        # client.connect('183.136.164.100',7766)
        # # client.connect('114.80.234.116',21003)
        # client.Register("CZCE")
        # client.RecvAndHandleData(client.ParseData,PrintQt)
    except Exception,ex:
        traceback.print_exc()
        print Exception,":",ex
        #break
