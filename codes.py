#!/usr/bin/python
#-*-coding:utf-8-*-

hsindexs = {
    "000001": "上证指数",
    "000002": "Ａ股指数",
    "000003": "Ｂ股指数",
    "000008": "综合指数",
    "000009": "上证380",
    "000010": "上证180",
    "000011": "基金指数",
    "000012": "国债指数",
    "000016": "上证50",
    "000017": "新综指",
    "000300": "沪深300",
    "399001": "深证成指",
    "399002": "深成指R",
    "399003": "成份Ｂ指",
    "399004": "深证100R",
    "399005": "中小板指",
    "399006": "创业板指",
    "000001": "上证指数",
    "000002": "Ａ股指数",
    "000003": "Ｂ股指数",
    "000008": "综合指数",
    "000009": "上证380",
    "000010": "上证180",
    "000011": "基金指数",
    "000012": "国债指数",
    "000016": "上证50",
    "000017": "新综指",
    "000300": "沪深300",
    "399001": "深证成指",
    "399002": "深成指R",
    "399003": "成份Ｂ指",
    "399004": "深证100R",
    "399005": "中小板指",
    "399006": "创业板指",
    "399100": "新 指 数",
    "399101": "中小板综",
    "399106": "深证综指",
    "399107": "深证Ａ指",
    "399108": "深证Ｂ指",
    "399333": "中小板R",
    "399606": "创业板R",
}


GOODS_URL = "http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php"

goods = [
    {'end': '2016-12-03', 'jys': 'LIFFE', 'pz': 'XAU', 'breed': 'XAU','hy':'',  'type': 'global', 'name': '伦敦金'},
    {'end': '2016-12-03', 'jys': 'LIFFE', 'pz': 'XAG', 'breed': 'XAG','hy':'',  'type': 'global', 'name': '伦敦银'},
    {'end': '2016-12-03', 'jys': 'IPE',   'pz': 'OIL', 'breed': 'OIL','hy':'',  'type': 'global', 'name': '布伦特原油'},
    {'end': '2016-12-03', 'jys': 'NYME',  'pz': 'CL',  'breed': 'CL', 'hy':'',  'type': 'global', 'name': 'NYME 原油'},
    {'end': '2016-12-03', 'jys': 'NYME',  'pz': 'NG',  'breed': 'NG', 'hy':'',  'type': 'global', 'name': 'NYME 天然气'},
    {'end': '2016-12-03', 'jys': 'CBOT',  'pz': 'BO',  'breed': 'BO', 'hy':'',  'type': 'global', 'name': 'CBOT黄豆油'},
    {'end': '2016-12-03', 'jys': 'CBOT',  'pz': 'C',   'breed': 'C',  'hy':'',  'type': 'global', 'name': 'CBOT玉米'},
    {'end': '2016-12-03', 'jys': 'CBOT',  'pz': 'S',   'breed': 'S',  'hy':'',  'type': 'global', 'name': 'CBOT黄豆'},
    {'end': '2016-12-03', 'jys': 'CBOT',  'pz': 'SM',  'breed': 'SM', 'hy':'',  'type': 'global', 'name': 'CBOT黄豆粉'},
    {'end': '2016-12-03', 'jys': 'CBOT',  'pz': 'W',   'breed': 'W',  'hy':'',  'type': 'global', 'name': 'CBOT小麦'},
]

def add_params(url, params):
    if 'name' in params:
        params.pop('name')
    from urllib import urlencode
    q = urlencode(params)
    return url + "?" + q

urls = [add_params(GOODS_URL, i) for i in goods]
import requests
import time
import lxml
import lxml.html
from lxml import etree
import pandas as pd
from cStringIO import StringIO
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import traceback

import yyhtools

def parse_df(url):
    for _ in range(3):
        text = ''
        try:
            time.sleep(0.05)
            request = Request(url)
            text = urlopen(request, timeout=10).read()
        except Exception as e:
            ytrack.fail(traceback.format_exc())
            continue
        #text = text.decode('GBK')
        html = lxml.html.parse(StringIO(text))
        res = html.xpath('//div[@class=\"historyList\"]/table[1]')
        sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr)
        if sarr == '':
            return None
        df = pd.read_html(sarr, skiprows = [0, 1])[0]
        if len(df) == 0:
            return None
        return df
    return None


def get_page(url):
    time.sleep(0.05)
    request = Request(url)
    text = urlopen(request, timeout=10).read()
    html = lxml.html.parse(StringIO(text))
    res = html.xpath('//div[@class=\"historyList\"]/table[2]')
    sarr = [etree.tostring(node) for node in res]
    sarr = ''.join(sarr)
    if sarr == '':
        return 0
    df = pd.read_html(sarr)[0]
    if len(df) == 0:
        return 0
    txt = df.iloc[0][0]
    ileft = txt.find(u"共")+1
    iright = txt.find(u"页", ileft)
    return int(txt[ileft:iright])


if __name__ == "__main__":
    for u in urls[:1]:
        df = parse_df(u)
        assert df is not None
        df.columns = ['date', 'close', 'open', 'high', 'low', 'volume']
        print len(df.columns)

    for u in urls[:1]:
        page = get_page(u)
        assert page
        print page

