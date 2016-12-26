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

CURDIR = os.path.abspath(os.path.dirname(__file__))

def get_ohlc_enddate(cid, enddate):
    time.sleep(0.005)
    page_url = 'http://www.google.com.hk/finance/historical?cid=%s&enddate=%s&num=200' % (cid, enddate.strftime("%Y-%m-%d"))
    df = None
    try:
        r = s.get(page_url, proxies=proxies)
        html = lxml.html.parse(StringIO(r.text))
        res = html.xpath('//table[@class=\"gf-table historical_price\"]')
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
    except Exception as e:
        print df
        print "_parse_fq_data: %s %s" % (cid, enddate)
        print traceback.format_exc()
        return None


def get_ohlc(exchage, cid, symbol):
    print 'start %s %s %s.. ' % (exchage, cid, symbol)
    dst = '%s/%s_daily/%s.csv' % (CURDIR, exchage, symbol)
    if os.path.exists(dst):
        ytrack.error('%s exists.' % dst)
        return
    data = pd.DataFrame()
    df = get_ohlc_enddate(cid, datetime.datetime.now())
    while df is not None:
        # print df
        data = data.append(df, ignore_index=True)
        enddate = df.iloc[-1]['date'] - datetime.timedelta(days=1)
        df = get_ohlc_enddate(cid, enddate)
    if data is not None and len(data) > 0:
        data = data.drop_duplicates('date')
        data = data.set_index('date')
        data = data.sort_index(ascending = False)
        code = get_code(symbol)
        data.insert(0, 'code', code)
        data.to_csv(dst, columns=['code', 'open', 'high', 'close', 'low'],
                    date_format="%Y%m%d")
    return data


def get_code(symbol):
    try:
        a = engine.execute("select id from us_symbol_int where symbol='%s'" % symbol)
        aa = a.fetchall()
        if not aa:
            b = engine.execute("insert into us_symbol_int(symbol) values ('%s')" % symbol)
            a = engine.execute("select id from us_symbol_int where symbol='%s'" % symbol)
            aa = a.fetchall()
        return aa[0][0]
    except Exception as e:
        print traceback.format_exc()
        return 0


def get_data(exchage):
    sql = 'select cid, Symbol from us_%s' % exchage
    a = engine.execute(sql)
    aa = a.fetchall()
    for cid, symbol in aa:
        if not cid:
            continue
        df = get_ohlc(exchage, cid, symbol)
        print '%s finished..' % symbol

get_data('nasdaq')
print 'nasdaq finished..'
get_data('nyse')
print 'nyse finished..'
get_data('amex')
print 'amex finished..'

