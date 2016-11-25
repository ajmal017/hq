#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys
import datetime
import time
import json
import math
import os

import lxml.html
from lxml import etree
import pandas as pd
import numpy as np
import re
from pandas.compat import StringIO
import six
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from logbook import Logger, FileHandler
import tushare as ts

TODAY = datetime.datetime.today()
DATE = str(TODAY.date())
log = Logger('Logbook')
error_handler = FileHandler("%s-error.log" % DATE)
info_handler = FileHandler("%s-info.log" % DATE)

def error(msg):
    with error_handler.applicationbound():
        log.error(msg)

def info(msg):
    with info_handler.applicationbound():
        log.info(msg)


def year_qua(date):
    mon = int(date[5:7])
    assert 1 <= mon <= 12
    q = int(math.ceil(mon/3.0))
    return [date[0:4], str(q)]


def today():
    day = datetime.datetime.today().date()
    return str(day)


def today_last_year():
    lasty = datetime.datetime.today().date() + datetime.timedelta(-365)
    return str(lasty)


def day_last_week(days=-7):
    lasty = datetime.datetime.today().date() + datetime.timedelta(days)
    return str(lasty)


def get_now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def get_quarts(start, end):
    idx = pd.period_range('Q'.join(year_qua(start)), 'Q'.join(year_qua(end)),
                          freq='Q-JAN')
    return [str(d).split('Q') for d in idx][::-1]


def trade_cal():
    '''
    http://218.244.146.57/static/calAll.csv
    交易日历
    isOpen=1是交易日，isOpen=0为休市
    '''
    df = pd.read_csv('http://218.244.146.57/static/calAll.csv')
    return df


def is_holiday(date):
    '''
    判断是否为交易日，返回True or False
    '''
    df = trade_cal()
    holiday = df[df.isOpen == 0]['calendarDate'].values
    if isinstance(date, str):
        today = datetime.datetime.strptime(date, '%Y-%m-%d')
    if today.isoweekday() in [6, 7] or date in holiday:
        return True
    else:
        return False


# 复权数据HEADER
HIST_FQ_COLS = ['date', 'open', 'high', 'close', 'low', 'volume', 'amount', 'factor']
def _parse_fq_data(url, index, retry_count, pause):
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(url)
            text = urlopen(request, timeout=10).read()
            text = text.decode('GBK')
            html = lxml.html.parse(StringIO(text))
            res = html.xpath('//table[@id=\"FundHoldSharesTable\"]')
            if six.PY3:
                sarr = [etree.tostring(node).decode('utf-8') for node in res]
            else:
                sarr = [etree.tostring(node) for node in res]
                sarr = ''.join(sarr)
            if sarr == '':
                return None
            df = pd.read_html(sarr, skiprows = [0, 1])[0]
            if len(df) == 0:
                return pd.DataFrame()
            if index:
                df.columns = HIST_FQ_COLS[0:7]
            else:
                df.columns = HIST_FQ_COLS
            if df['date'].dtypes == np.object:
                df['date'] = df['date'].astype(np.datetime64)
                df = df.drop_duplicates('date')
        except ValueError as e:
            error(str(e))
            # 时间较早，已经读不到数据
            return None
        except Exception as e:
            error(str(e))
        else:
            return df
    raise IOError("NETWORK_URL_ERROR_MSG")


def _get_index_url(index, code, qt):
    if index:
        url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s/type/S.phtml?year=%s&jidu=%s' % (
            code, qt[0], qt[1])
    else:
        url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/%s.phtml?year=%s&jidu=%s' % (
            code, qt[0], qt[1])
    return url


def _get_basics():
    fle = 'stock.basics.csv'
    if os.path.exists(fle):
        df = pd.read_csv(fle, dtype=str)
        df = df.set_index('code')
        return df
    df = ts.get_stock_basics()
    df.to_csv(fle, encoding="utf-8")
    info('update stock_basics from network..')
    return df


basics_df = _get_basics()

def get_market_date(code):
    try:
        s = str(basics_df.ix[code]['timeToMarket'])
        if len(s) != 8:
            return None
        d = datetime.datetime.strptime(s, "%Y%m%d")
        return str(d.date())
    except Exception as e:
        error(str(e))
        return None


def get_hfq_data(code, start=None, end=None,
               index=False, retry_count=3, pause=0.005, drop_factor=True):
    '''
    获取前复权数据
    '''
    if not start:
        start = get_market_date(code)
        if not start:
            return
    if not end:
        end = today()

    qs = get_quarts(start, end)
    qt = qs[0]
    data = _parse_fq_data(_get_index_url(index, code, qt), index,
                          retry_count, pause)
    if data is None:
        data = pd.DataFrame()
    if len(qs)>1:
        for d in range(1, len(qs)):
            qt = qs[d]
            df = _parse_fq_data(_get_index_url(index, code, qt), index,
                                retry_count, pause)
            if df is None:  # 可能df为空，比如停牌
                continue
            else:
                data = data.append(df, ignore_index=True)
    if len(data) == 0 or len(data[(data.date>=start)&(data.date<=end)]) == 0:
        return None

    data = data.drop_duplicates('date')
    if drop_factor:
        data = data.drop('factor', axis=1)
    data = data[(data.date>=start) & (data.date<=end)]
    for label in ['open', 'high', 'close', 'low']:
        data[label] = data[label].map(lambda x: '%.2f' % x)
        data[label] = data[label].astype(float)
    data = data.set_index('date')
    data = data.sort_index(ascending = False)
    return data


def get_all_ohlcs():
    for code in basics_df.index.values:
        dst = 'ohlc_daily/%s.txt' % code
        if os.path.exists(dst):
            info("%s exists.." % dst)
            continue
        df = get_hfq_data(code)
        if df is None:
            continue
        if 'code' not in df.columns:
            df.insert(0, 'code', code)
        df.to_csv(dst, date_format="%Y%m%d")
        info("%s finished.." % dst)


if __name__ == "__main__":
    info("Start get_all_ohlcs ..")
    get_all_ohlcs()
    info("End get_all_ohlcs ..")

