#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import six
import datetime
import time
import requests
import traceback

from bs4 import BeautifulSoup

import yyhtools

from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False)
except:
    engine = None

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
        yyhtools.error("requests.get('%s') is None" % page_url)
        return

    soup = BeautifulSoup(r.text.encode(r.encoding))
    allnews = soup.findAll("div", {"class": "newsline"})
    data = []
    for news in allnews:
        data.append({
            'id': long(news.attrs.get('id')),
            'html': str(news)
        })

    my_df = pd.DataFrame(data)
    my_df = my_df.set_index('id')
    min_id = my_df.index.min()
    sql = '''select id from jin10_news where id >= %s''' % min_id
    hl_df  = pd.read_sql_query(sql, engine, index_col='id')
    drop_ids = list(set(my_df.index.tolist()) & set(h1_df.index.tolist()))
    my_df.drop(drop_ids, inplace=True)
    try:
        my_df.to_sql('jin10_news', engine, if_exists='append', index=True, index_label='id')
    except:
        ytrack.fail(traceback.format_exc())
    else:
        ytrack.success("%s 成功更新 %s 条记录." % ('jin10_news', df.shape[0]))

get_data()

# yyhtools.track.show()
# yyhtools.send(yyhtools.get_logs(), style='stock', title='investing网站数据抓取完成')

