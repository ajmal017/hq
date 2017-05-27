#!/usr/bin/env python
#-*-coding:utf-8-*-

'''
相关系数计算
'''

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



CURDIR = os.path.abspath(os.path.dirname(__file__))

ONEDAY = datetime.timedelta(days=1)
TODAY = datetime.datetime.now().date()


def get_data(code, start, end, ohlc_table='investing_ohlc_daily'):
    assert isinstance(start, int)
    assert isinstance(end, int)
    if not end:
        end = int(TODAY.strftime("%Y%m%d"))
    if not start:
        endday = datetime.datetime.strptime(str(end), "%Y%m%d")
        startday = endday - ONEDAY * 365
        start = int(startday.strftime("%Y%m%d"))
    sql_format = 'select date, close from %s where date >= %s and date <= %s and code = %s order by date desc;'
    sql = sql_format % (ohlc_table, start, end, code)
    df = pd.read_sql_query(sql, engine, index_col='date')
    df = df.iloc[::-1]
    return df


'''

美元指数

1 欧元/美元 57.6%
2 英镑/美元 11.9%
3 美元/日元 13.6%
7 美元/加拿大元 9.1%
4 美元/瑞士法郎 3.6%
41 美元/瑞典克朗 4.2%

计算公式
usdx = 50.14348112 * EURUSD ^ (-0.576) * USDJPY ^ (0.136) * GBPUSD ^ (-0.119) * USDCAD ^ (0.091) * USDSEK ^ (0.042) * USDCHF ^ (0.036)

code 的含义：
8830 美国黄金
8836 美国白银
8849 美国原油
8862 美国天然气

8827 美元指数
169 道琼斯指数
166 标普500指数
14958 纳斯达克综合指数
178 日经225

'''



@click.command()
@click.option('--start', default=0, help='开始日期')
@click.option('--end', default=0, help='结束日期')
@click.option('--a', default=15, help='标的a')
@click.option('--b', default=3, help='标的b')
def cov(start, end, a, b):
    df1 = get_data(a, start, end)
    df2 = get_data(b, start, end)
    # 取公共数据
    df3 = pd.concat([df1, df2], axis=1, join='inner')
    arr = np.transpose(df3.as_matrix())
    res = np.corrcoef(arr)
    print res
    return res


if __name__ == "__main__":
    cov()

