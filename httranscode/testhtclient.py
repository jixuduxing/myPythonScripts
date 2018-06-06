# -*- coding: UTF-8 -*-
#从主站获取数据

from htclient import *

def Getlist( market,rankingway = 0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2955(market = market,rankingway = rankingway)
    index = 0

    datarecv,datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist,totalsize = client.parsebody( 2955,bodyrecv )
        # print 'totallist:', len(totallist), ',totalsize:', totalsize
        index += len(itemlist)
        totallist = totallist + itemlist
        while index <totalsize:
            client.reqest2955(reqbegin = index,market =market,rankingway = rankingway)
            datarecv, datalen = client.recvhead()
            if not datalen:
                print "recv head error"
                break
            bodyrecv = client.recvbody(datalen)
            itemlist, totalsize = client.parsebody(2955, bodyrecv)
            index += len(itemlist)
            totallist = totallist + itemlist
        print 'totallist:',len(totallist),',totalsize:',totalsize

    return totallist

def Getlist2984( rankingway = 0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2984(rankingway = rankingway,reqnum= 50)
    index = 0

    datarecv,datalen,c = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)
    totallist = []
    if datalen:

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist,totalsize = client.parsebody( 2984,bodyrecv )
        # print 'totallist:', len(totallist), ',totalsize:', totalsize
        index += len(itemlist)
        totallist = totallist + itemlist
        while index <totalsize:
            client.reqest2984(reqbegin = index,rankingway = rankingway,reqnum= 50)
            datarecv, datalen,c = client.recvhead()
            if not datalen:
                print "recv head error"
                break
            bodyrecv = client.recvbody(datalen)
            itemlist, totalsize = client.parsebody(2984, bodyrecv)
            index += len(itemlist)
            totallist = totallist + itemlist
        print 'totallist:',len(totallist),',totalsize:',totalsize
    return totallist

def Getlist2938(market, rankingway=0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2938(market=market, rankingway=rankingway)
    index = 0

    datarecv, datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist, totalsize = client.parsebody(2938, bodyrecv)

def Getlist2331(market, rankingway=0):
    port = 13000
    ip = '121.43.72.79'

    client = htclient()
    client.connect(ip, port)
    client.reqest2331(id=market, rankingway=rankingway)
    index = 0

    datarecv, datalen = client.recvhead()
    totallist = []
    if datalen:
        bodyrecv = client.recvbody(datalen)

        # wholedata = datarecv + bodyrecv
        # print len(wholedata)

        itemlist, totalsize = client.parsebody(2331, bodyrecv)
        index += len(itemlist)
        totallist = totallist + itemlist
        while index < totalsize:
            client.reqest2331(reqbegin=index, rankingway=rankingway, reqnum=50,id=market)
            datarecv, datalen = client.recvhead()
            if not datalen:
                print "recv head error"
                break
            bodyrecv = client.recvbody(datalen)
            itemlist, totalsize = client.parsebody(2331, bodyrecv)
            index += len(itemlist)
            totallist = totallist + itemlist
        print 'totallist:', len(totallist), ',totalsize:', totalsize


testlist = Getlist2984(1)
# testlist = Getlist(105,0)

# import io
# wfile = io.open(__file__+'.log','wb')
# wfile.write( 'key,pre_close,last,open,high,low,total_volume,total_amount\n')

# for item in testlist:
#     teststr = item.code_ + ',' +  str(item.preclose_)+ ',' +  str(item.new_) + ',' + str(item.open_) + ',' + str(item.high_) + ',' + str(item.low_)+ ',' +str(item.volumn_)+ ',' +str(item.amount_)
#     wfile.write(teststr)
#     wfile.write('\n')