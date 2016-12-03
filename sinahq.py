#!/usr/bin/env python

import requests

r = requests.get('http://hq.sinajs.cn/rn=1479737518332&list=hf_CHA50CFD,DINIW,hf_CL,hf_GC,hf_SI,hf_S,hf_C,hf_OIL,hf_CAD,hf_XAU,hf_XAG,hf_NG')

print r.text


# 期货历史数据
# http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=IF&pz=DXF&hy=&breed=DXF&type=global&start=2016-11-03&end=2016-12-03


# 外汇和指数， hexun.com，和讯网
# http://webforex.hermes.hexun.com/forex/kline?code=FOREXGBPUSD&start=20161202000000&number=1000&type=5


# python 翻墙
# http://zhengheng.me/2016/08/25/python-requests-socks5/
# http://liuxiaohui.net/2016/07/27/Make-the-python-requests-work-via-socks-proxy-on-CentOS-server.html

# google财经
# https://www.google.com.hk/finance?ei=JkRDWOHQLoG52Abf1ZT4CA
# 美股和全球指数

