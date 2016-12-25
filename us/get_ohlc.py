#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import six
import lxml.html
from lxml import etree
import pandas as pd
from pandas.compat import StringIO
import datetime
import time
import requests
import traceback
import string
import numpy as np

import yyhtools

from yyhtools import track as ytrack

from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False)
except:
    engine = None

s = requests.Session()
s.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    }
)
proxies = {
  "http": "socks5://127.0.0.1:1080",
  "https": "socks5://127.0.0.1:1080",
}

def get_cid(exchange, symbol):
    pass


def get_ohlc_enddate(exchange, symbol, enddate):
    time.sleep(0.005)
    page_url = 'http://www.google.com.hk/finance/historical?cid=120222725170627&enddate=%s&num=200' % (enddate.strftime("%Y-%m-%d"))
    try:
        r = s.get(page_url, proxies=proxies)
        html = lxml.html.parse(StringIO(r.text))
        res = html.xpath('//table[@class=\"gf-table historical_price\"]')
        print res
        sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr)
        if sarr == '':
            return None
        df = pd.read_html(sarr, skiprows=[0])[0]
        if len(df) == 0:
            return None
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df = df.drop_duplicates('date')
        if df['date'].dtypes == np.object:
            df['date'] = df['date'].astype(np.datetime64)
        return df
    except ValueError as e:
        print traceback.format_exc()
        ytrack.fail("_parse_fq_data: %s" % symbol)
        ytrack.fail(traceback.format_exc())
        # 时间较早，已经读不到数据
        return None
    except Exception as e:
        print traceback.format_exc()
        ytrack.fail("_parse_fq_data: %s" % symbol)
        ytrack.fail(traceback.format_exc())
        return None

def get_ohlc(exchange, symbol):
    df = get_ohlc_enddate('', '', datetime.datetime(year=2016, month=12, day=23))
    while df is not None:
        print df
        enddate = df.iloc[-1]['date'] - datetime.timedelta(days=1)
        df = get_ohlc_enddate('', '', enddate)


ytrack.show()
print get_ohlc('', '')
