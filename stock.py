#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys
import datetime
import time
import json
import math
import os
import functools
import traceback

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

import click

from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False)
except:
    engine = None

import yyhtools.track as ytrack
import yyhtools.notice as ynotice

DEBUG = 1

CURDIR = os.path.abspath(os.path.dirname(__file__))
TODAY = datetime.datetime.today()
DATE = str(TODAY.date())


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


def trade_cal(force=False):
    '''
    http://218.244.146.57/static/calAll.csv
    交易日历
    isOpen=1是交易日，isOpen=0为休市
    '''
    dst = os.path.join(CURDIR, 'trade.cal.csv')
    if os.path.exists(dst) and not force:
        df = pd.read_csv(dst, index_col=0)
        df = df.set_index('calendarDate')
        return df
    def date2int(date):
        y, m, d = date.split("/")
        return int(y) * 10000 + int(m) * 100 + int(d)
    df = pd.read_csv('http://218.244.146.57/static/calAll.csv')
    df['calendarDate'] = df['calendarDate'].map(date2int)
    df.to_csv(dst)
    df = df.set_index('calendarDate')
    ytrack.info('update trade_cal from network..')
    return df


tradecal_df = trade_cal()

def is_open_day(day):
    '''
    isOpen=1是交易日，isOpen=0为休市
    '''
    if isinstance(day, datetime.datetime):
        day = day.year * 10000 + day.month * 100 + day.day
    try:
        isOpen = tradecal_df.loc[day]['isOpen']
        return isOpen == 0
    except Exception as e:
        ytrack.error(traceback.format_exc())
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
            ytrack.fail("_parse_fq_data: %s" % url)
            ytrack.fail(traceback.format_exc())
            # 时间较早，已经读不到数据
            return None
        except Exception as e:
            ytrack.fail("_parse_fq_data: %s" % url)
            ytrack.fail(traceback.format_exc())
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


def _get_basics(force=False):
    fle = os.path.join(CURDIR, 'stock.basics.csv')
    if os.path.exists(fle) and not force:
        df = pd.read_csv(fle, dtype=str)
        df = df.set_index('code')
        return df
    df = ts.get_stock_basics()
    df.to_csv(fle, encoding="utf-8")
    ytrack.info('update stock_basics from network..')
    return df


basics_df = _get_basics()
basics_df['timeToMarket'] = basics_df['timeToMarket'].map(int)

def get_market_date(code):
    try:
        s = str(basics_df.ix[code]['timeToMarket'])
        if len(s) != 8:
            return None
        d = datetime.datetime.strptime(s, "%Y%m%d")
        return str(d.date())
    except Exception as e:
        ytrack.fail("get_market_date: %s" % code)
        ytrack.fail(traceback.format_exc())
        return None


def get_hfq_data(code, start=None, end=None,
                 index=False, retry_count=3, pause=0.01, drop_factor=True):
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


@click.group()
def cli():
    pass


@cli.command()
def update_stock_info():
    _get_basics(True)
    trade_cal(True)
    ynotice.send(ytrack.get_logs(), style='stock', title='更新股票基础数据和交易日期')

@cli.command()
def get_all_ohlcs():
    ytrack.info("Start get_all_ohlcs ..")
    for code in basics_df.index.values[:3]:
        dst = os.path.join(CURDIR, 'ohlc_daily/%s.txt' % code)
        if os.path.exists(dst):
            ytrack.info("%s exists.." % dst)
            continue
        df = get_hfq_data(code)
        if df is None:
            continue
        if 'code' not in df.columns:
            df.insert(0, 'code', code)
            df.to_csv(dst, date_format="%Y%m%d")
            ytrack.info("%s finished.." % dst)
    ytrack.info("End get_all_ohlcs ..")


ONEDAY = datetime.timedelta(days=1)

def get_day_date(day):
    return int(day.strftime("%Y%m%d"))

def get_week_date(day):
    a = day.isocalendar()
    return "%s%02d" % (a[0], a[1])

def get_month_date(date):
    return date.year * 100 + date.month

def _update_macd(date, code, ohlc_table):
    if code == 'ALL':
        sql = 'select code from %s where date = %s;' % (ohlc_table, date)
        df = pd.read_sql_query(sql, engine, index_col='code')
        codes = df.index.values.tolist()
    else:
        codes = [code]
    if len(codes) == 0:
        return None
    sql_format = 'select close from %s where date <= %s and code = "%s" order by date desc limit 250;'
    idxs = []
    matrix = []
    columns = ['ma%s' % i for i in range(1, 251)]
    for code in codes:
        sql = sql_format % (ohlc_table, date, code)
        df = pd.read_sql_query(sql, engine, index_col='close')
        arr = df.index.values.tolist()
        n = len(arr)
        assert n > 0
        if n < 250:
            arr += [np.nan] * (250 -n)
        matrix.append(arr)
        idxs.append(code)
    df = pd.DataFrame(matrix, index=idxs, columns=columns)
    for i in range(2, 251):
        df['ma%s' % i] += df['ma%s' % (i-1)]
    for i in range(2, 251):
        df['ma%s' % i] /= i
    df['date'] = date
    return df


def _update_macd_daily(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = int(date.strftime("%Y%m%d"))
    return _update_macd(d, code, 'ohlc_daily')


def _update_macd_weekly(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = get_week_date(date)
    return _update_macd(d, code, 'ohlc_weekly')


def _update_macd_monthly(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = date.year * 100 + date.month
    return _update_macd(d, code, 'ohlc_monthly')


def _update_ohlc_between(startDate, endDate, code):
    if code == 'ALL':
        sql = 'select distinct code from ohlc_daily where date >= %s and date <= %s;' % (startDate, endDate)
        df = pd.read_sql_query(sql, engine, index_col='code')
        codes = df.index.values.tolist()
    else:
        codes = [code]
    codess = '","'.join(codes)
    sql = '''select code, open from
               ( select date, code, open from ohlc_daily where
                 date >= %d and date <= %d and code in ("%s") order by date asc) as T
             group by code
             ''' % (startDate, endDate, codess)
    open_df  = pd.read_sql_query(sql, engine, index_col='code')
    sql = '''select code, close from
               ( select date, code, close from ohlc_daily where
                 date >= %d and date <= %d and code in ("%s") order by date desc) as T
             group by code
             ''' % (startDate, endDate, codess)
    close_df  = pd.read_sql_query(sql, engine, index_col='code')
    sql = '''select code, max(high) as high, min(low) as low
             from ohlc_daily where
             date >= %d and date <= %d and code in ("%s")
             group by code
             ''' % (startDate, endDate, codess)
    hl_df  = pd.read_sql_query(sql, engine, index_col='code')
    if len(open_df) > 0:
        set1 = set(open_df.index.values.tolist())
        set2 = set(close_df.index.values.tolist())
        set3 = set(hl_df.index.values.tolist())
        assert set1 == set2
        assert set2 == set3
        df = pd.concat([open_df, hl_df, close_df], axis=1)
        return df
    return None


def _update_ohlc_weekly(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    weekday = date.isocalendar()[2]
    startDate = int((date - (weekday - 1) * ONEDAY).strftime("%Y%m%d"))
    endDate = int(date.strftime("%Y%m%d"))
    df = _update_ohlc_between(startDate, endDate, code)
    if df is not None:
        d = get_week_date(date)
        df['date'] = d
    return df


def _update_ohlc_monthly(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    startDate = date.year * 10000 + date.month * 100 + 1
    endDate = int(date.strftime("%Y%m%d"))
    df = _update_ohlc_between(startDate, endDate, code)
    if df is not None:
        d = get_month_date(date)
        df['date'] = d
    return df


def _update_ohlc_daily(date, code):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")

    dt_s = date.strftime("%Y%m%d")
    dt_i = int(dt_s)
    dt_d = date.strftime("%Y-%m-%d")

    isOpen = tradecal_df.loc[dt_i]['isOpen']
    if not isOpen:
        ytrack.fail("%s is not Open.." % date)
        return
    if code == 'ALL':
        # 在date日（包括）之前上市的股票
        df = basics_df.loc[(basics_df['timeToMarket'] <= dt_i) & (basics_df['timeToMarket'] > 0) ]
        codes = df.index.values.tolist()
    else:
        codes = [code]

    quart = year_qua(dt_s)

    data = pd.DataFrame()
    if DEBUG:
        codes = codes[:3]
    for code in codes:
        df = _parse_fq_data(_get_index_url(False, code, quart), False, 3, 0.01)
        if df is None:  # 可能df为空，比如停牌
            ytrack.fail("Date=%s, code=%%s is None ." % (date, code))
            continue
        else:
            df = df[df.date==dt_d]
            df.insert(0, 'code', code)
            data = data.append(df)

    data = data.drop('factor', axis=1)
    data['date'] = dt_i
    for label in ['open', 'high', 'low', 'close']:
        data[label] = data[label].map(lambda x: '%.2f' % x)
        data[label] = data[label].astype(float)
    data = data.set_index('code')
    data = data.sort_index(ascending = False)
    # print data
    # data.to_sql("ohlc_daily", stock.engine, if_exists='append', index=True, index_label='code')
    return data



@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='code')
@click.option('--save/--no-save', default=True, help='保存')
def run_daily(date, code, save):
    if not date:
        day = datetime.datetime.now()
    else:
        day = datetime.datetime.strptime(str(date), "%Y%m%d")

    if is_open_day(day):
        ytrack.fail("%s is not Open.." % date)
        ynotice.send(ytrack.get_logs(), style='error', title='%s-不是交易日' % get_day_date(day))
        return

    ytrack.success("start run_daily(date=%s, code=%s, save=%s)" % (date, code, save))
    df1 = _update_ohlc_daily(date, code)
    if df1 is not None:
        sql = "delete from ohlc_daily where date = %s" % get_day_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df1.to_sql('ohlc_daily', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("ohlc_daily 成功更新 %s 条记录." % df1.shape[0])
    else:
        ytrack.success("ohlc_daily 需要更新的数据为空")


    df2 = _update_ohlc_weekly(date, code)
    if df2 is not None:
        sql = "delete from ohlc_weekly where date = %s" % get_week_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df2.to_sql('ohlc_weekly', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("ohlc_weekly 成功更新 %s 条记录." % df2.shape[0])
    else:
        ytrack.success("ohlc_weekly 需要更新的数据为空")

    df3 = _update_ohlc_monthly(date, code)
    if df3 is not None:
        sql = "delete from ohlc_monthly where date = %s" % get_month_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df3.to_sql('ohlc_monthly', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("ohlc_monthly 成功更新 %s 条记录." % df3.shape[0])
    else:
        ytrack.success("ohlc_monthly 需要更新的数据为空")

    macd_cols = ['date'] + ['ma%s' % i for i in range(5, 251, 5)]

    df4 = _update_macd_daily(date, code)
    if df4 is not None:
        df4 = df4[macd_cols]
        sql = "delete from macd_daily where date = %s" % get_day_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df4.to_sql('macd_daily', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("macd_daily 成功更新 %s 条记录." % df4.shape[0])
    else:
        ytrack.success("macd_daily 需要更新的数据为空")

    df5 = _update_macd_weekly(date, code)
    if df5 is not None:
        df5 = df5[macd_cols]
        sql = "delete from macd_weekly where date = %s" % get_week_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df5.to_sql('macd_weekly', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("macd_weekly 成功更新 %s 条记录." % df5.shape[0])
    else:
        ytrack.success("macd_weekly 需要更新的数据为空")

    df5 = _update_macd_weekly(date, code)
    if df5 is not None:
        df5 = df5[macd_cols]
        sql = "delete from macd_weekly where date = %s" % get_week_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df5.to_sql('macd_weekly', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("macd_weekly 成功更新 %s 条记录." % df5.shape[0])
    else:
        ytrack.success("macd_weekly 需要更新的数据为空")

    df6 = _update_macd_monthly(date, code)
    if df6 is not None:
        df6 = df6[macd_cols]
        sql = "delete from macd_monthly where date = %s" % get_month_date(day)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("删除数据成功")

        try:
            df6.to_sql('macd_monthly', engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("macd_monthly 成功更新 %s 条记录." % df6.shape[0])
    else:
        ytrack.success("macd_monthly 需要更新的数据为空")

    ynotice.send(ytrack.get_logs(), style='stock', title='%s-股票K线图更新' % get_day_date(day))



@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_ohlc_daily(date, code):
    _update_ohlc_daily(date, code)

@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_ohlc_weekly(date, code):
    _update_ohlc_weekly(date, code)

@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_ohlc_monthly(date, code):
    _update_ohlc_monthly(date, code)

@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_macd_daily(date, code):
    _update_macd_daily(date, code)


@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_macd_weekly(date, code):
    _update_macd_weekly(date, code)


@cli.command()
@click.option('--date', default=0, help='日期')
@click.option('--code', default='000001', help='股票代码')
def update_macd_monthly(date, code):
    _update_macd_monthly(date, code)


if __name__ == "__main__":
    cli()


