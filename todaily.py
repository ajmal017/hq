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
        df = pd.read_csv(csvpath, index_col=0, header=0, nrows=nrows)
    if 'date' in df:
        aday = df['date'].iloc[0]
        if (isinstance(aday, str) or isinstance(aday, unicode)) and len(aday) == len('2016-00-00'):
            FORMAT = '%Y-%m-%d'
        else:
            FORMAT = '%Y%m%d'
        df['date'] = pd.to_datetime(df['date'], format=FORMAT)
    return df


def _ohlc_daily(filename, src_dir, dest_dir, src_type='sinagoods'):
    assert src_type in ['sinagoods', 'hsindexs', 'investing', 'idxs']
    if src_type in ['sinagoods', 'hsindexs']:
        code = filename.split(".")[0]
    elif src_type == 'idxs':
        code = filename.split(".")[0]
        code = code.replace("A", "1").replace("B", "2").replace("C", "3")
    else:
        from codes import code2int
        code = code2int[filename.replace(".csv", "")]

    dst = os.path.join(CURDIR, dest_dir, "%s.txt" % code)
    src = os.path.join(CURDIR, src_dir, filename)

    if not os.path.exists(src):
        print("%s not exist.." % src)
        return
    if os.path.exists(dst):
        print("%s exist.." % dst)
        return
    df = _read_csv(src)
    if 'code' not in df.columns:
        df.insert(0, 'code', code)
    else:
        df['code'] = code

    if 'date' in df.columns:
        df = df.set_index('date')
    if df.shape[0] > 1 and df.index[0] < df.index[-1]:
        df = df.iloc[::-1]
    df.to_csv(dst, columns=['code', 'open', 'high', 'close', 'low'],
              date_format="%Y%m%d")
    return df


@click.command()
@click.option('--filename', default='A11.txt', help=u'文件名')
@click.option('--src-dir', default='idxs_ohlc_data', help=u'源目录')
@click.option('--dest-dir', default='idxs_ohlc_daily', help='目标目录')
@click.option('--src-type', default='idxs', help='srctype')
@print_time
def ohlc_daily(filename, src_dir, dest_dir, src_type):
    if filename == 'ALL':
        filenames = os.listdir(os.path.join(CURDIR, src_dir))
    else:
        filenames = [filename]
    for filename in filenames:
        _ohlc_daily(filename, src_dir, dest_dir, src_type)


if __name__ == "__main__":
    ohlc_daily()




