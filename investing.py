#!/usr/bin/env python
#-*-coding:utf-8-*-

import six
import lxml.html
from lxml import etree
import pandas as pd
from pandas.compat import StringIO
import datetime
import time
import requests

def get_data():
    s = requests.Session()
    s.headers.update(
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
        }
    )

    s.get('http://cn.investing.com/currencies/eur-usd-historical-data')


    s.headers.update({
        "X-Requested-With": "XMLHttpRequest"
    })


    data = {"action": "historical_data",
            "curr_id": "1",
            "st_date": "1990/09/01",
            "end_date": "2016/12/02",
            "interval_sec": "Daily"}
    end_date = datetime.datetime(2016, 12, 2, 0, 0)
    result = pd.DataFrame()
    while True:
        time.sleep(0.1)
        st_date = end_date - datetime.timedelta(days=500)
        data['st_date'] = str(st_date.strftime("%Y/%m/%d"))
        data['end_date'] = str(end_date.strftime("%Y/%m/%d"))

        r = s.post("http://cn.investing.com/instruments/HistoricalDataAjax",
                   data=data)

        html = lxml.html.parse(StringIO(r.text))
        try:
            res = html.xpath('//table[@id=\"curr_table\"]')
        except Exception as e:
            print e
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
    if len(result) > 0:
        result.columns = ['date', 'close', 'open', 'high', 'low', 'percentage']
        result['date'] = pd.to_datetime(result['date'], format=u"%Y年%m月%d日")
        return result
    return None

df = get_data()
print df
if df is not None:
    df.to_csv("t1.csv")

