# -*- coding: UTF-8 -*-

import MySQLdb

#==============================================================================
#分时走势数据 --- 实时数据
# class FSZSItem:
# {
# public:
#     int time; //用行情客户端日期时间格式：year(12bits)|month(4)|day(5)|hour(5)|minute(6)
#     int	last; //最新价
#     int64_t volume; //成交量
#     int64_t amount; //成交额
#     int avg_price; //均价
#     int position; //持仓量
#     union
#     {
#         int64_t inner_volume; //内盘成交量（股票）
#         char zdj_ratio; //涨跌家数据（指数）
#     };
#
#     void Init();
#     bool Serialize(CMemStream* pStream) const;
#     bool Deserialize(CMemStream* pStream);
#     void Set(const FSZSItem* pValue);
# };

# 打开数据库连接
db = MySQLdb.connect("172.190.28.217","root","password","testdb" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# 使用execute方法执行SQL语句
# cursor.execute("SELECT VERSION()")
print cursor.execute("insert into test(test) values('tt');")
cursor.execute('select count(*) from test;')
# 使用 fetchone() 方法获取一条数据
data = cursor.fetchone()
print data
print "Database version : %s " % data

db.commit()
# 关闭数据库连接
db.close()
