# -*- coding: UTF-8 -*-
#深圳binary测试客户端
from client import*
import os
from util.until import *
import threading

class  htszbinclient(szbinclient):

    def parsebody(self, header, bodyrecv):
        # print 'header.MsgType',header.MsgType
        if header.MsgType == msgtype_login:
            # print "msgtype_login"
            for stry in self.parse_login(header, bodyrecv):
                pass
                print stry
        elif header.MsgType == msgtype_gonggao:
            # print 'msgtype_gonggao'
            for stry in self.parse_gonggao(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_panhou:
            # print 'msgtype_panhou'
            for stry in self.parse_panhou(header, bodyrecv):
                pass
                # print stry
                # logging.debug(stry)
        elif header.MsgType == msgtype_quote_count:
            # print 'msgtype_quote_count'
            for stry in self.parse_quote_count(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_index_ex:
            # print 'msgtype_index_ex'
            for stry in self.parse_index_ex(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_hqkz_ex:
            for stry in self.parse_hqkz_ex(header,bodyrecv):
                pass
                print stry

        elif header.MsgType == msgtype_hkhq_ex:
            # print 'msgtype_hkhq_ex'
            for stry in self.parse_hkhq_ex(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_zrt_zubiwt:
            for stry in self.parse_zrt_zubiwt(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_xxjy_zubiwt:
            for stry in self.parse_xxjy_zubiwt(header, bodyrecv):
                pass
                print stry
        elif header.MsgType == msgtype_jzjj_zubiwt:
            for stry in self.parse_jzjj_zubiwt(header, bodyrecv):
                pass
                print stry
        elif header.MsgType in( msgtype_jzjj_zubi,msgtype_xxjy_zubi,msgtype_zrt_zubi):
            for stry in self.parse_zubi(header, bodyrecv):
                pass
                print stry
        elif header.MsgType == msgtype_logout:
            print "msgtype_logout"
            # self.parseHQKZ_RQST(header, bodyrecv)
        elif header.MsgType == msgtype_market_status:
            # print "msgtype_market_status"
            for stry in self.parse_market_status(header, bodyrecv):
                pass
                print stry
        elif header.MsgType == msgtype_stock_status:
            # print 'msgtype_stock_status'
            for stry in self.parse_stock_status(header, bodyrecv):
                pass
                # print stry
        elif header.MsgType == msgtype_heartbeat:
            # print 'msgtype_heartbeat'
            pass
        elif header.MsgType == msgtype_channel_heartbeat:
            # print 'msgtype_channel_heartbeat'
            for stry in self.parse_channel_heartbeat(header, bodyrecv):
                pass
                # print stry
            # self.parseZQDMINFO_RQST(header, bodyrecv)
        elif header.MsgType  == msgtype_volume_tj_ex:
            for stry in self.parse_volume_tj_ex(header, bodyrecv):
                pass
                # print stry
            pass
            # print 'volume_tj_ex'
        else:
            # pass
            print "unknown pack:%d" % header.MsgType


curpath = os.path.dirname(__file__)
curfilename = getCurrentFileName()

InitLog(curpath,'szclient')

client = htszbinclient()
client.connect('10.10.13.26',8020)
# client.connect('127.0.0.1',9080)
# client.connect('115.159.95.177',13141)

client.login()
# client.reqmarkets(['MB','SZ','SH'])
# client.reqmarkets(['MB'])
# client.reqmarkets(['SH'])
t =threading.Thread(target=szbinclient.keepconn,args=(client,))
# t.start()
client.work()