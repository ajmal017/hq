#!/usr/bin/env python
#-*-coding:utf-8-*-

import json
import sys
import os
import math
import datetime

CURDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.join(CURDIR, "data")
def get_data(N=25):
    ff = os.listdir(DATADIR)
    data = {}
    for f in ff:
        with open(os.path.join(DATADIR, f)) as fp:
            t = json.loads(fp.read())
            year = int(f.split(".")[0])
            data[year] = {}
            for i in t:
                cty = i['country']
                gdp = i['gdp']
                if gdp.endswith(u"万亿"):
                    gdp = float(gdp.replace(u'万亿', '').encode("utf-8")) * 100000
                elif gdp.endswith(u"亿"):
                    gdp = float(gdp.replace(u'亿', '').encode("utf-8")) * 10
                elif gdp.endswith(u'千万'):
                    gdp = float(gdp.replace(u'千万', '').encode("utf-8"))
                data[year][cty] = gdp

    resp = {}
    YEARS = sorted(data.keys())  # 去掉前面20年
    topN = sorted(data[YEARS[-1]].items(), key=lambda i: i[1], reverse=True)[:N]
    topN = [i[0] for i in topN]  # 名字
    items = []
    for name in topN:
        item = {'name': name,
                'type': 'line',
               # 'stack': '总量',
                'data': []}
        for y in YEARS:
            try:
                item['data'].append(int(data[y][name]))
            except:
                item['data'].append(0)
        items.append(item)
    resp['years'] = YEARS
    resp['items'] = items
    resp['names'] = topN
    return resp

if __name__ == "__main__":
    print get_data(5)
