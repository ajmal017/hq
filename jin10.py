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
from yyhtools import track as ytrack

from sqlalchemy import create_engine

try:
    import config
    engine = create_engine(config.mysqlserver, echo=False, encoding="utf-8")
except:
    engine = None

from sqlalchemy.orm import sessionmaker
Session = sessionmaker()
Session.configure(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, BigInteger, Text, TIMESTAMP

class News(Base):
    __tablename__ = "jin10_news"

    id = Column(BigInteger, primary_key=True)
    html = Column(Text)
    created_at = Column(TIMESTAMP)



def get_data():
    page_url = 'http://www.jin10.com/'
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
            yyhtools.error("%s" % (page_url))
            yyhtools.error(traceback.format_exc())
            return

    if r is None:
        yyhtools.error("requests.get('%s') is None" % page_url)
        return

    soup = BeautifulSoup(r.text.encode(r.encoding))
    allnews = soup.findAll("div", {"class": "newsline"})
    cnt = 0
    session = Session()
    for news in allnews:
        try:
            id = long(news.attrs.get('id')) / 100
            html = str(news)
            session.merge(News(id=id, html=html))
            cnt += 1
        except:
            ytrack.fail(traceback.format_exc())
    session.commit()
    ytrack.success("%s 成功更新 %s 条记录." % ('jin10_news', cnt))

get_data()

# yyhtools.track.show()
yyhtools.send(yyhtools.get_logs(), style='stock', title='jin10数据成功更新')

