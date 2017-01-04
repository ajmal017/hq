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
import click
import yyhtools

import yyhtools.track as ytrack
import yyhtools.notice as ynotice

DEBUG = False
from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False)
except:
    engine = None

# NASDAQ  纳斯达克交易所
# df1 = pd.read_csv("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download")
# df1.to_sql('nasdad', engine, if_exists='replace', index=True, index_label='id')

# NYSE 纽约证劵交易所
# df2 = pd.read_csv("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download")
# AMEX 美国证劵交易所
# df3 = pd.read_csv("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download")


# historical
# https://www.google.com.hk/finance/historical?q=NYSE:BABA
# https://www.google.com.hk/finance/historical?cid=23536317556137&startdate=2015-12-25&enddate=2016-12-23&num=30


s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
})
proxies = {
  "http": "socks5://127.0.0.1:1080",
  "https": "socks5://127.0.0.1:1080",
}
def get_cid(exchange, symbol):
    time.sleep(0.005)
    page_url = 'https://www.google.com.hk/finance/historical?q=%s:%s' % (exchange, symbol)
    r = s.get(page_url, proxies=proxies)
    html = lxml.html.parse(StringIO(r.text))
    try:
        res = html.xpath('//input[@name=\"cid\"]')
        if len(res) > 0:
            node = res[0]
            return node.value
        return ''
    except Exception as e:
        print traceback.format_exc()
        yyhtools.error(traceback.format_exc())
        return ''


def get_data(exchange):
    df = None
    for _ in range(3):
        try:
            time.sleep(0.5)
            csv_path = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=%s&render=download" % exchange
            df = pd.read_csv(csv_path)
            df['Symbol'] = df['Symbol'].apply(string.strip).apply(string.rstrip)
            break
        except requests.exceptions.ConnectionError as e:
            yyhtools.error(traceback.format_exc())
            return
    if df is None:
        return

    df.to_sql('us_%s' % exchange, engine, if_exists='replace', index=True, index_label='id')
    ytrack.success("us_%s 数据更新成功" % exchange)


@click.group()
def cli():
    pass

@cli.command()
def cids():
     n = len(df)
     cids = []
     for i in range(n):
         symbol = df.iloc[i]['Symbol']
         cid = get_cid(exchange, symbol)
         cids.append(cid)
         print symbol, cid

@cli.command()
def stocks():
    d = datetime.datetime.now().strftime("%Y%m%d")
    get_data('nasdaq')
    get_data('nyse')
    get_data('amex')
    ynotice.send(ytrack.get_logs(), style='stock', title='%s美股列表更新成功' % d)

if __name__ == "__main__":
    cli()
