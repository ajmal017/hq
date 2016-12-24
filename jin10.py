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

import yyhtools

DEBUG = False

CURDIR = os.path.abspath(os.path.dirname(__file__))

def get_data():
    page_url = 'http://jin10.com/'
    s = requests.Session()
    s.headers.update(
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
        }
    )

    r = None
    for _ in range(3):
        try:
            time.sleep(0.5)
            r = s.get(page_url)
            break
        except requests.exceptions.ConnectionError as e:
            yyhtools.error("%s %s %s" % (page_url, api_url, curr_id))
            yyhtools.error(traceback.format_exc())
            return

    if r is None:
        return

    html = lxml.html.parse(StringIO(r.text))
    try:
        res = html.xpath('//table[@id=\"curr_table\"]')
    except Exception as e:
        yyhtools.error("%s %s %s" % (page_url, api_url, curr_id))
        yyhtools.error(traceback.format_exc())
        break
    if six.PY3:
        sarr = [etree.tostring(node).decode('utf-8') for node in res]
    else:
        sarr = [etree.tostring(node) for node in res]
        sarr = ''.join(sarr)

    if sarr == '':
        break
    df = pd.read_html(sarr)[0]
    if len(df) == 0:
        break
    if len(df) == 1 and df.iloc[0][u'日期'] == 'No results found...':
        break
    result = result.append(df, ignore_index=True)
    end_date = st_date - datetime.timedelta(days=1)

        if len(df) < 10:
            print df
        if DEBUG:
            break
    if len(result) > 0:
        if len(result.columns) == 6:
            result.columns = ['date', 'close', 'open', 'high', 'low', 'percentage']
        else:
            result.columns = ['date', 'close', 'open', 'high', 'low', 'amount', 'percentage']
        result['date'] = pd.to_datetime(result['date'], format=u"%Y年%m月%d日")
        return result
    return None


yyhtools.track.show()
yyhtools.send(yyhtools.get_logs(), style='stock', title='investing网站数据抓取完成')

