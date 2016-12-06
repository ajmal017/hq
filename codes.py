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

urls = [
# 伦敦金
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=LIFFE&pz=XAU&hy=&breed=XAU&type=global&start=2016-09-03&end=2016-12-03',
# 伦敦银
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=LIFFE&pz=XAG&hy=&breed=XAG&type=global&start=2016-09-03&end=2016-12-03',
# 布伦特原油
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=IPE&pz=OIL&hy=&breed=OIL&type=global&start=2016-09-03&end=2016-12-03',
# NYME 原油
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=NYME&pz=CL&hy=&breed=CL&type=global&start=2016-09-03&end=2016-12-03',
# NYME 天然气
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=NYME&pz=NG&hy=&breed=NG&type=global&start=2016-09-03&end=2016-12-03',
# CBOT黄豆油
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=CBOT&pz=BO&hy=&breed=BO&type=global&start=2016-09-03&end=2016-12-03',
# CBOT玉米
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=CBOT&pz=C&hy=&breed=C&type=global&start=2016-09-03&end=2016-12-03',
# CBOT黄豆
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=CBOT&pz=S&hy=&breed=S&type=global&start=2016-09-03&end=2016-12-03',
# CBOT黄豆粉
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=CBOT&pz=SM&hy=&breed=SM&type=global&start=2016-09-03&end=2016-12-03',
# CBOT小麦
    'http://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?jys=CBOT&pz=W&hy=&breed=W&type=global&start=2016-09-03&end=2016-12-03',]



