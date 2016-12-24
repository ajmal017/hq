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
    engine = create_engine(config.mysqlserver, echo=False, encoding="utf-8")
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
    cnt = 0
    for news in allnews:
        try:
            data = {
                'id': long(news.attrs.get('id')),
                'html': str(news)
            }
            sql = "insert into jin10_news (id, html) values (%s, '%s');" % (data['id'], data['html'])
            engine.execute(sql)
            cnt += 1
        except:
            ytrack.fail(traceback.format_exc())
    ytrack.success("%s 成功更新 %s 条记录." % ('jin10_news', cnt))

get_data()

yyhtools.track.show()
# yyhtools.send(yyhtools.get_logs(), style='stock', title='investing网站数据抓取完成')

