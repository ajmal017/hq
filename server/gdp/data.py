#!/usr/bin/env python
#-*-coding:utf-8-*-

import json
import sys
import os
import math
import datetime

def get_data(N=1):
    ff = os.listdir("data")
    data = {}
    for f in ff:
        with open("data/%s" % f) as fp:
            t = json.loads(fp.read())
            year = int(f.split(".")[0])
            data[year] = {}
            for i in t:
                cty = i['country']
                gdp = i['gdp']
                if gdp.endswith(u"万亿"):
                    gdp = float(
                        gdp.replace(u'万亿', '').encode("utf-8")) * 100000
                elif gdp.endswith(u"亿"):
                    gdp = float(gdp.replace(u'亿', '').encode("utf-8")) * 10
                elif gdp.endswith(u'千万'):
                    gdp = float(gdp.replace(u'千万', '').encode("utf-8"))
                data[year][cty] = gdp

    YEARS = sorted(data.keys())
    topN = sorted(data[YEARS[-1]].items(),
                  key=lambda i: i[1], reverse=True)[:N]
    topN = [i[0] for i in topN]
    print data
    return topN

if __name__ == "__main__":
    print get_data(5)
