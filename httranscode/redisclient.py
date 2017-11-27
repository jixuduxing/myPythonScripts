# -*- coding: UTF-8 -*-
#redis 客户端
import redis
import io

wfile = io.open(__file__+'.log','wb')
wfile.write( 'key,pre_close,last,open,high,low,total_volume,total_amount\n')
def redissub(channal):
    red = redis.Redis(host='127.0.0.1', port=6379,db=2)
    # mbset = red.smembers('mbset')
    # for mb in mbset:
    #     yield mb
    # pipe = red.pipeline()
    ps = red.pubsub()
    # ps.
    # keys = red.keys('*')
    zqdmset = red.smembers('zqdmset')
    yield zqdmset,type(zqdmset)
    l = list(zqdmset)
    l.sort()
    for key in l:
        pre_close = red.hget(key,'pre_close')
        last = red.hget(key,'last')
        open = red.hget(key,'open')
        high = red.hget(key,'high')
        low = red.hget(key,'low')
        total_volume = red.hget(key,'total_volume')
        total_amount = red.hget(key,'total_amount')
        print pre_close,last,open,high,low,total_volume,total_amount
        # value = red.get('hq_'+key)
        # yield value
        # yield last,pre_close
        if (low != '0')| (high =='0'):
            # teststr = key+','+pre_close+','+last+','+open+','+high+','+low+','+ total_volume+','+total_amount
            teststr = key+','+str(int(pre_close) / 10) + ',' + str(int(last) / 10) + ',' + str(int(open) / 10) + ',' + str(
                int(high) / 10) + ',' + str(int(low) / 10) + ',' + str(int(total_volume) / 100) + ',' + str(
                int(total_amount) / 10000)

            # teststr = key+','+str((int(pre_close) + 5) / 10) + ',' + str((int(last) + 5) / 10) + ',' + str((int(open) + 5) / 10) + ',' + str(
            #     (int(high) + 5) / 10) + ',' + str((int(low) + 5) / 10) + ',' + str(
            #     (int(total_volume) + 50) / 100) + ',' + str((int(total_amount) + 5000) / 10000)

            # yield teststr
            wfile.write( teststr)
            wfile.write('\n')
            # if pre_close !='0' :
            #     yield float(last)*100/float(pre_close)-100,total_volume,total_amount
        else:
            # teststr = key + ',' + last + ',' + open + ',' + high + ',' + low + ',' + total_volume + ',' + total_amount
            # yield value
            pass
    # ps.subscribe(['sshq','blockhq'])
    ps.subscribe([channal])
    #
    # for item in ps.listen():
    #     if item['type'] == 'message':
    #         # pass
    #         yield item['data']
    #         # print item['data']
    #     else:
    #         print item

for itemvalue in redissub('blockhq'):
    print itemvalue
