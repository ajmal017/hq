#!/usr/bin/env python
#-*-coding:utf-8-*-

from collections import OrderedDict

aa = OrderedDict((
    ("111", "道琼斯"),
    ("112", "纳斯达克"),
    ("113", "标普500"),
    ("114", "多伦多"),
    ("115", "巴西股票指数"),

    ("212", "巴黎CAC指数"),
    ("213", "德国DAX指数"),
    ("214", "荷兰AEX指数"),

    ("312", "台湾加权指数"),
    ("313", "日经225指数"),
    ("314", "韩国KOSPI"),
    ("315", "印尼雅加达"),
    ("317", "恒生指数"),
))

indexs = [ (k,  v) for k, v in aa.iteritems()]

