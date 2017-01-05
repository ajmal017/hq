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



@click.command()
@click.option('--data-dir', default='data', help=u'数据目录')
def ensure_unique(data_dir):
    '''
    计算移动平均线
    '''
    filenames = os.listdir(os.path.join(CURDIR, data_dir))
    for filename in filenames:
        csv_path = os.path.join(CURDIR, data_dir, filename)
        df = _read_csv(csv_path)
        arr = df.index.values.tolist()
        is_right = all(arr[i] > arr[i+1] for i in xrange(len(arr)-1))
        if not is_right:
            print '%s is not right.' % csv_path

if __name__ == "__main__":
    ensure_unique()


