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
import numpy as np

import click

from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False)
except:
    engine = None

import yyhtools
import yyhtools.track as ytrack
import yyhtools.notice as ynotice

CURDIR = os.path.abspath(os.path.dirname(__file__))

ONEDAY = datetime.timedelta(days=1)

def get_day_date(day):
    return int(day.strftime("%Y%m%d"))

def get_week_date(day):
    a = day.isocalendar()
    return "%s%02d" % (a[0], a[1])

def get_month_date(date):
    return date.year * 100 + date.month

def _update_macd(date, code, ohlc_table):
    if code == 0:
        sql = 'select distinct code from %s where date = %s;' % (ohlc_table, date)
        df = pd.read_sql_query(sql, engine, index_col='code')
        codes = df.index.values.tolist()
    else:
        codes = [code]
    codes = map(int, codes)
    if len(codes) == 0:
        return None
    # 获取 date 当天存在的股票

    sql_format = 'select close from %s where date <= %s and code = %s order by date desc limit 250;'
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


def _update_macd_daily(date, code, ohlc_table):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = int(date.strftime("%Y%m%d"))
    return _update_macd(d, code, ohlc_table)


def _update_macd_weekly(date, code, ohlc_table):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = get_week_date(date)
    return _update_macd(d, code, ohlc_table)


def _update_macd_monthly(date, code, ohlc_table):
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    d = date.year * 100 + date.month
    return _update_macd(d, code, ohlc_table)


def _update_ohlc_between(startDate, endDate, code, table):
    print startDate, endDate, code, table
    if code == 0:
        sql = 'select distinct code from %s where date >= %s and date <= %s;' % (table, startDate, endDate)
        print sql
        df = pd.read_sql_query(sql, engine, index_col='code')
        codes = df.index.values.tolist()
    else:
        codes = [code]
    # 获取需要更新的代码
    codess = ','.join(map(str, codes))
    print codess
    sql = '''select code, open from
               ( select date, code, open from %s where
                 date >= %d and date <= %d and code in (%s) order by date asc) as T
             group by code
             ''' % (table, startDate, endDate, codess)
    open_df  = pd.read_sql_query(sql, engine, index_col='code')
    sql = '''select code, close from
               ( select date, code, close from %s where
                 date >= %d and date <= %d and code in (%s) order by date desc) as T
             group by code
             ''' % (table, startDate, endDate, codess)
    close_df  = pd.read_sql_query(sql, engine, index_col='code')
    sql = '''select code, max(high) as high, min(low) as low
             from %s where
             date >= %d and date <= %d and code in (%s)
             group by code
             ''' % (table, startDate, endDate, codess)
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


def _update_ohlc_weekly(date, code, table):
    assert table in ['investing_ohlc_weekly']
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    weekday = date.isocalendar()[2]
    startDate = int((date - (weekday - 1) * ONEDAY).strftime("%Y%m%d"))
    endDate = int(date.strftime("%Y%m%d"))
    df = _update_ohlc_between(startDate, endDate, code, table.replace("weekly", "daily"))
    if df is not None:
        d = get_week_date(date)
        df['date'] = d
    return df


def _update_ohlc_monthly(date, code, table):
    assert table in ['investing_ohlc_monthly']
    if not date:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(str(date), "%Y%m%d")
    startDate = date.year * 10000 + date.month * 100 + 1
    endDate = int(date.strftime("%Y%m%d"))
    df = _update_ohlc_between(startDate, endDate, code, table.replace("monthly", "daily"))
    if df is not None:
        d = get_month_date(date)
        df['date'] = d
    return df


s = requests.Session()
s.headers.update({
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
})
proxies = {
    "http": "socks5://127.0.0.1:1080",
    "https": "socks5://127.0.0.1:1080",
}


def get_all_symbols(exchange):
    try:
        sql = 'select Symbol, cid from us_%s_cid' % exchange
        a = engine.execute(sql)
        aa = a.fetchall()
        cids = {}
        symbols = []
        for symbol, cid in aa:
            if not cid or cid == '0':
                continue
            symbols.append(symbol)
        yyhtools.success("get all symbols len(symbols) = %s" % (len(symbols)))
        return symbols
    except Exception as e:
        yyhtools.success("get empty symbols")
        yyhtools.error(trackback.format_exc())
        return []


def get_date_ohlc(exchange, symbol, date):
    for _ in range(3):
        try:
            time.sleep(0.005)
            page_url = 'https://www.google.com.hk/finance/historical?q=%s:%s' % (exchange, symbol)
            r = s.get(page_url, proxies=proxies)
            html = lxml.html.parse(StringIO(r.text))
            res = html.xpath('//table[@class=\"gf-table historical_price\"]')
            sarr = [etree.tostring(node) for node in res]
            sarr = ''.join(sarr)
            if sarr == '':
                return None
            df = pd.read_html(sarr, skiprows = [0])[0]
            df.columns = ['date', 'open', 'high', 'low', 'close', 'amount']
            df['date'] = pd.to_datetime(df['date'], format=u"%Y-%m-%d")
            df = df.drop_duplicates('date')
            df = df[df.date==date]
            if len(df) > 0:
                df['date'] = int(date.strftime("%Y%m%d"))
            return df
        except Exception as e:
            print traceback.format_exc()
            yyhtools.error(traceback.format_exc())
            return '0'


def _update_ohlc_daily(date, symbol, table, exchange):
    if symbol == 'ALL':
        items = get_all_symbols(exchange)
    else:
        items = [symbol]

    data = pd.DataFrame()
    cur_idx = 0
    total = len(items)
    for t in items:
        cur_idx +=1
        print "%s/%s .. " % (cur_idx, total)
        df = get_date_ohlc(exchange, symbol, date)
        if df is not None:
            if len(df) == 1:
                data = data.append(df)
            else:
                yyhtools.info("%s %s %s获取重复数据." % (exchange, symbol, date))
                yyhtools.error(str(df))

    yyhtools.info("_update_ohlc_daily finished")
    if len(data) == 0:
        return None
    return data



@click.command()
@click.option("--exchange", default="nyse", help="exchange")
@click.option('--date', default=0, help='日期')
@click.option('--symbol', default='BABA', help='BABA')
def run_daily(exchange, date, symbol):
    if not date:
        day = datetime.datetime.now() - datetime.timedelta(days=0)
        day = day.replace(hour=0, minute=0, second=0, microsecond=0)
        date = int(day.strftime("%Y%m%d"))
    else:
        day = datetime.datetime.strptime(str(date), "%Y%m%d")

    def my_update_someday_data(df, date, save_table):
        sql = "delete from %s where date = %s" % (save_table, date)
        ytrack.success("execute: %s" % sql)
        try:
            engine.execute(sql)
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("%s删除数据成功" % save_table)

        try:
            df.to_sql(save_table, engine, if_exists='append', index=True, index_label='code')
        except:
            ytrack.fail(traceback.format_exc())
        else:
            ytrack.success("%s 成功更新 %s 条记录." % (save_table, df.shape[0]))


    ytrack.success("start run_daily(date=%s, exchange=%s, symbol=%s)" % (date, exchange, symbol))


    table1 = "%s_ohlc_daily" % exchange
    df1 = _update_ohlc_daily(day, symbol, table1, exchange)
    if df1 is not None:
        my_update_someday_data(df1, get_day_date(day), table1)
    else:
        ytrack.success("%s 需要更新的数据为空" % table1)

    table2 = '%s_ohlc_weekly' % exchange
    df2 = _update_ohlc_weekly(date, symbol, table2)
    if df2 is not None:
        my_update_someday_data(df2, get_week_date(day), table2)
    else:
        ytrack.success("%s 需要更新的数据为空" % table2)

    table3 = '%s_ohlc_monthly' % exchange
    df3 = _update_ohlc_monthly(date, symbol, table3)
    if df3 is not None:
        my_update_someday_data(df3, get_month_date(day), table3)
    else:
        ytrack.success("%s 需要更新的数据为空" % table3)


    macd_cols = ['date'] + ['ma%s' % i for i in range(5, 251, 5)]
    df4 = _update_macd_daily(date, symbol, table1)
    if df4 is not None:
        df4 = df4[macd_cols]
        my_update_someday_data(df4, get_day_date(day), '%s_macd_daily' % exchange)
    else:
        ytrack.success("%s_macd_daily 需要更新的数据为空" % exchange)

    df5 = _update_macd_weekly(date, symbol, table2)
    if df5 is not None:
        df5 = df5[macd_cols]
        my_update_someday_data(df5, get_week_date(day), '%s_macd_weekly' % exchange)
    else:
        ytrack.success("%s_macd_weekly 需要更新的数据为空" % exchange)

    df6 = _update_macd_monthly(date, symbol, table3)
    if df6 is not None:
        df6 = df6[macd_cols]
        my_update_someday_data(df6, get_month_date(day), '%s_macd_monthly'%exchange)
    else:
        ytrack.success("%s_macd_monthly 需要更新的数据为空"% exchange)

    ynotice.send(ytrack.get_logs(), style='stock', title='%s-%s-K线图更新' % (get_day_date(day), exchange))



if __name__ == "__main__":
    run_daily()

