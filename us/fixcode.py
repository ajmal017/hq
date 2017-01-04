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

CURDIR = os.path.abspath(os.path.dirname(__file__))

from functools import wraps

import click
def print_time(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        s = time.time()
        ret = f(*args, **kwds)
        args = [i for i in args if isinstance(i, (int, float, str, unicode))]
        print('Func %s(%s, %s) cost %s seconds' %
              (f.func_name, args, kwds.keys(), time.time() - s))
        return ret
    return wrapper

sql = 'select symbol, id from us_symbol_int'
a = engine.execute(sql)
aa = a.fetchall()
codes = {}
for symbol, cid in aa:
    codes[symbol] = cid

def _read_csv(csvpath, usecols=[], nrows=None):
    '''
    参数控制只读某些列和前面的n行。
    注意：csv按时间倒序
    '''
    if usecols:
        if 0 not in usecols:
            usecols.insert(0, 0)
        df = pd.read_csv(
            csvpath, index_col=0, header=0, nrows=nrows, usecols=usecols)
    else:
        df = pd.read_csv(csvpath, index_col=0, header=0, nrows=nrows)
    if 'date' in df:
        aday = df['date'].iloc[0]
        if (isinstance(aday, str) or isinstance(aday, unicode)) and len(aday) == len('2016-00-00'):
            FORMAT = '%Y-%m-%d'
        else:
            FORMAT = '%Y%m%d'
        df['date'] = pd.to_datetime(df['date'], format=FORMAT)
    return df


def _fixcode(filename, data_dir):
    data_dir = os.path.join(CURDIR, data_dir)
    assert os.path.exists(data_dir)
    data_path = os.path.join(data_dir, filename)
    if not os.path.exists(data_path):
        print("%s not exits." % data_path)
        return None
    vv = filename.split(".")
    if len(vv) == 2:
        codes[vv[0]]
        # return
    else:
        print filename, data_dir

    code = codes[filename.replace(".csv", "")]
    df = _read_csv(data_path)
    df['code'] = code
    df.to_csv(data_path)
    return df


@click.command()
@click.option('--filename', default='AAMC.csv', help=u'文件名')
@click.option('--src-dir', default='amex_macd_weekly', help=u'数据目录')
@print_time
def fixcode(filename, src_dir):
    '''
    计算移动平均线
    '''
    if filename == 'ALL':
        filenames = os.listdir(os.path.join(CURDIR, src_dir))
    else:
        filenames = [filename]

    for filename in filenames:
        df = _fixcode(filename, src_dir)

if __name__ == "__main__":
    fixcode()
