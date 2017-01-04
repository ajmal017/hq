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


CURDIR = os.path.dirname(os.path.abspath(__file__))

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
        #df = pd.read_csv(csvpath, index_col=0, header=0, nrows=nrows)
        df = pd.read_csv(csvpath, header=0, nrows=nrows)
    if 'date' in df:
        aday = df['date'].iloc[0]
        if (isinstance(aday, str) or isinstance(aday, unicode)) and len(aday) == len('2016-00-00'):
            FORMAT = '%Y-%m-%d'
        else:
            FORMAT = '%Y%m%d'
        df['date'] = pd.to_datetime(df['date'], format=FORMAT)
    return df

@print_time
def _fix_daily(filename, src_dir, dest_dir):
    src = os.path.join(CURDIR, src_dir, filename)
    dest = os.path.join(CURDIR, dest_dir, filename)
    if not os.path.exists(src):
        print("%s not exist.." % src)
        return
    if os.path.exists(dest):
        print("%s exists.." % dest)
        return

    df = _read_csv(src)
    n = len(df)
    if df.shape[0] > 1 and df['date'][0] < df['date'][n-1]:
        df = df.iloc[::-1]

    def fix_row(row):
        next_idx = row.name - 1
        last_idx = row.name + 1

        for k in ['open', 'close', 'high', 'low']:
            if row[k] == '-':
                row[k] = 0
            elif isinstance(row[k], (str, unicode)):
                row[k] = float(row[k])
        aa = [row['open'], row['close'], row['high'], row['low']]
        last_close = 0
        next_open = 0
        if last_idx <= n-1:
            try:
                last_close = float(df.loc[last_idx]['close'])
            except:
                pass
        if next_idx >= 0:
            try:
                next_open = float(df.loc[next_idx]['open'])
            except:
                pass
        aa.append(last_close)
        aa.append(next_open)
        aa = filter(None, aa)
        if len(aa) == 0:
            if next_idx < 0:
                print src
                print 'wrong data'
                return row
            next_row = df.loc[next_idx]
            aa = [next_row['open'],
                  next_row['close'],
                  next_row['high'],
                  next_row['low']]
        assert len(aa) > 0, src
        min_v = min(aa)
        max_v = max(aa)

        if row['open'] <= 0:
            if last_idx <= n -1:
                row['open'] = last_close
            else:
                row['open'] = min_v
        if row['close'] <= 0:
            if next_idx >= 0:
                row['close'] = next_open
            else:
                row['close'] = max_v
        if row['high'] <= 0:
            row['high'] = max_v
        if row['low'] <= 0:
            row['low'] = min_v
        return row

    df2 = df.apply(fix_row, axis=1)
    df2.to_csv(dest, columns=['date', 'code', 'open', 'high', 'close', 'low'],
               date_format="%Y%m%d", index=False)
    return df2


@click.command()
@click.option('--filename', default='a.csv', help=u'文件名')
@click.option('--src-dir', default='test_data', help=u'源目录')
@click.option('--dest-dir', default='test_data2', help=u'目标目录')
@print_time
def fix_daily(filename, src_dir, dest_dir):
    if filename == 'ALL':
        filenames = os.listdir(os.path.join(CURDIR, src_dir))
    else:
        filenames = [filename]
    for filename in filenames:
        _fix_daily(filename, src_dir, dest_dir)


if __name__ == "__main__":
    fix_daily()




