import ctypes
dll = ctypes.windll.LoadLibrary( 'E:\Work\ht_hq_tc/branches\mb_market\ht_hq_tc\Debug/bk_hq_dll.dll' )

nRst = dll.TEST( )
print nRst