#!/usr/bin/env python
#-*-coding:utf-8-*-

'''

'''

import json
import sys
import os
import math
import datetime

import pandas as pd
import numpy as np


import click

import time
from functools import wraps


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




@click.group()
def cli():
    pass


header = ['date', 'open', 'high', 'low', 'close', 'volume', 'money']
header_size = len(header)

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


@print_time
def _macd(filename, max_days, data_dir, macd_dir):
    global header, header_size
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), data_dir)
    assert os.path.exists(data_dir)
    data_path = os.path.join(data_dir, filename)
    macd_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), macd_dir)
    if not os.path.exists(macd_dir):
        os.mkdir(macd_dir)
    csv_path = os.path.join(macd_dir, filename)

    if os.path.exists(csv_path) and not force:
        print("get from %s" % csv_path)
        return _read_csv(csv_path)
    if not os.path.exists(data_path):
        print("%s not exits." % data_path)
        return None

    if latest > 0:
        df = _read_csv(data_path, nrows=latest)
    else:
        df = _read_csv(data_path)
    if df.shape[0] > 1:
        assert df.index[0] > df.index[-1], df.index

    columns = [str(i) for i in range(1, max_days + 1)]
    for i in columns:
        if i == '1':
            df[i] = df['close']
        else:
            df[i] = df[str(int(i) - 1)] + df['close'].shift(1 - int(i))
    # 计算移动平均线
    df2 = df[columns]
    for i in range(2, max_days + 1):
        df2[str(i)] /= i
    df2.to_csv(csv_path)
    return df2


@click.command()
@click.option('--filename', default='SZ000001.txt', help=u'文件名')
@click.option('--max-days', default=250, help=u'最大macd周期')
@click.option('--data-dir', default='data', help=u'数据目录')
@click.option('--macd-dir', default='macd', help='macd目录')
def macd(filename, max_days, data_dir, macd_dir):
    '''
    计算移动平均线
    '''
    filename = filename.upper()
    print(filename, max_days, data_dir, macd_dir)
    if filename == 'ALL':
        filenames = os.listdir(data_dir)
    else:
        filenames = [filename]

    for filename in filenames:
        df = _macd(
            filename, max_days, latest, data_dir, macd_dir, force)

cli.add_command(macd)


if __name__ == "__main__":
    cli()
