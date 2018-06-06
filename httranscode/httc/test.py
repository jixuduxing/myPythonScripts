# -*- coding: UTF-8 -*-

from httcclient import *


curpath = os.path.dirname(__file__)
curfilename = getCurrentFileName()

InitLog(curpath,'httcclient')

client = httcclient()
# client.connect('10.10.13.26',8031)
client.connect('127.0.0.1',10001)
# client.connect('188.190.12.88',13131)
# client.connect('115.159.95.177',13141)

client.login()
# client.reqmarkets(['MB','SZ','SH'])
# client.reqmarkets(['MB'])
# client.reqmarkets(['SH'])
t =threading.Thread(target=httcclient.keepconn,args=(client,))
t.start()
def mycallback(str,type):
    if type == TCM_HQKZ_FunFlow:
        if str.code[:8] != 'SZ300059':
            return
        # print PrintStuct(str)
        print 'buy:',str.volume_buy1,str.volume_buy2,str.volume_buy3,str.volume_buy4,'sell:',str.volume_sell1,str.volume_sell2,str.volume_sell3,\
            str.volume_sell4,'buy:',str.trade_cnt_buy[0],str.trade_cnt_buy[1],str.trade_cnt_buy[2],str.trade_cnt_buy[3], \
            'sell:',str.trade_cnt_sell[0],str.trade_cnt_sell[1],str.trade_cnt_sell[2],str.trade_cnt_sell[3], \
            'zhuli:',str.amount_buy1 + str.amount_buy2 - str.amount_sell1- str.amount_sell2,str.time

        # print str,type
        pass
    elif type == 0:
        # print PrintStuct(str)
        pass
    else:
        # print PrintStuct(str)
        pass
        # print str

client.work(mycallback)