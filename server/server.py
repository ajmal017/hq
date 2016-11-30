#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import math
import datetime
import json
import sys
import traceback
from itertools import chain
from functools import wraps
import logging

import tornado
import tornado.httpserver
from tornado import gen
from tornado.web import url
from tornado.options import define, options

from sqlalchemy import create_engine
import pandas as pd

import config

CURDIR = os.path.abspath(os.path.dirname(__file__))

engine = create_engine(config.mysqlserver, echo=False)

FROM_SQL = True
ohlc_cols = ','.join(['date', 'open', 'close', 'low', 'high'])
macd_cols = ','.join(['date', 'ma5'] + ['ma%s' % i for i in range(10, 251, 10)])


def read_csv(csvpath, usecols=[], nrows=None):
    '''
    参数控制只读某些列和前面的n行。
    注意：csv按时间倒序
    '''
    csvpath = "%s/%s" % (CURDIR, csvpath)
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


def get_db_data(code, table, enddate='', limit=120):
    data = {
        'dates': [],
        'ohlcs': [],
        'mas': {},
    }

    if enddate:
        sql = 'select date from ohlc_%s where date <= %s and code = "%s" order by date desc limit %s' % (table, enddate, code, limit)
    else:
        sql = 'select date from ohlc_%s where date > 0 and code = "%s" order by date desc limit %s' % (table, code, limit)
    date_df = pd.read_sql_query(sql, engine, index_col='date')
    startdate = date_df.index.values[-1]
    if enddate:
        ohlc_sql = 'SELECT %s FROM ohlc_%s where date <= %s and date >= %s and code = "%s" order by date desc limit %s' % (ohlc_cols, table, enddate, startdate, code, limit)
    else:
        ohlc_sql = 'SELECT %s FROM ohlc_%s where date > %s and code = "%s" order by date desc limit %s' % (ohlc_cols, table, startdate, code, limit)
    ohlc_df  = pd.read_sql_query(ohlc_sql, engine, index_col='date')
    if enddate:
        macd_sql = 'SELECT %s FROM macd_%s where date <= %s and date >= %s and code = "%s" order by date desc limit %s' % (macd_cols, table, enddate, startdate, code, limit)
    else:
        macd_sql = 'SELECT %s FROM macd_%s where date > %s and code = "%s" order by date desc limit %s' % (macd_cols, table, startdate, code, limit)
    macd_df  = pd.read_sql_query(macd_sql, engine, index_col='date')
    ohlc_df = ohlc_df.iloc[::-1]
    macd_df = macd_df.iloc[::-1]
    data['dates'] = ohlc_df.index.values.tolist()
    data['ohlcs'] = ohlc_df.to_records(index=False).tolist()
    for col in macd_df.columns:
        if col.startswith("ma"):
            data['mas'][col] = map(lambda i: i if i > 0 else '-', macd_df[col].values.tolist())
    return data


def get_daily_data(code, enddate):
    data = {
        'dates': [],
        'ohlcs': [],
        'mas': {},
    }
    ohlc_df = read_csv("data/ohlc_daily/SZ000001.TXT", nrows=250,
                       usecols=['open', 'close', 'low', 'high'])
    ohlc_df = ohlc_df.reindex_axis(['open', 'close', 'low', 'high'], axis=1)
    macd_df = read_csv("data/macd_daily/SZ000001.TXT", nrows=250)
    if enddate:
        ohlc_df = ohlc_df.iloc[:125:-1]
        macd_df = macd_df.iloc[:125:-1]
    else:
        ohlc_df = ohlc_df.iloc[125::-1]
        macd_df = macd_df.iloc[125::-1]

    data['dates'] = ohlc_df.index.values.tolist()
    data['ohlcs'] = ohlc_df.to_records(index=False).tolist()
    for col in macd_df.columns:
        icol = int(col)
        if icol >= 10 and icol % 10 != 0:
            continue
        data['mas']['ma%s' % col] = map(lambda i: '-' if math.isnan(i) else i, macd_df[col].values.tolist())
    return data

def get_weekly_data(code, enddate):
    data = {
        'dates': [],
        'ohlcs': [],
        'mas': {},
    }
    ohlc_df = read_csv("data/ohlc_weekly/SZ000001.TXT", nrows=250,
                       usecols=['open', 'close', 'low', 'high'])
    ohlc_df = ohlc_df.reindex_axis(['open', 'close', 'low', 'high'], axis=1)
    macd_df = read_csv("data/macd_weekly/SZ000001.TXT", nrows=250)
    ohlc_df = ohlc_df.iloc[::-1]
    macd_df = macd_df.iloc[::-1]
    data['dates'] = ohlc_df.index.values.tolist()
    data['ohlcs'] = ohlc_df.to_records(index=False).tolist()
    for col in macd_df.columns:
        icol = int(col)
        if icol >= 10 and icol % 10 != 0:
            continue
        data['mas']['ma%s' % col] = map(lambda i: '-' if math.isnan(i) else i, macd_df[col].values.tolist())
    return data

def get_monthly_data(code, enddate):
    data = {
        'dates': [],
        'ohlcs': [],
        'mas': {},
    }

    ohlc_df = read_csv("data/ohlc_monthly/SZ000001.TXT", nrows=250,
                       usecols=['open', 'close', 'low', 'high'])
    ohlc_df = ohlc_df.reindex_axis(['open', 'close', 'low', 'high'], axis=1)
    macd_df = read_csv("data/macd_monthly/SZ000001.TXT", nrows=250)
    ohlc_df = ohlc_df.iloc[::-1]
    macd_df = macd_df.iloc[::-1]
    data['dates'] = ohlc_df.index.values.tolist()
    data['ohlcs'] = ohlc_df.to_records(index=False).tolist()
    for col in macd_df.columns:
        icol = int(col)
        if icol >= 10 and icol % 10 != 0:
            continue
        data['mas']['ma%s' % col] = map(lambda i: '-' if math.isnan(i) else i, macd_df[col].values.tolist())
    return data





class Route(object):

    _routes = {}

    def __init__(self, pattern, kwargs={}, name=None, host='.*$'):
        self.pattern = pattern
        self.kwargs = {}
        self.name = name
        self.host = host

    def __call__(self, handler_class):
        spec = url(self.pattern, handler_class, self.kwargs, name=self.name)
        self._routes.setdefault(self.host, []).append(spec)
        return handler_class

    @classmethod
    def routes(cls, application=None):
        if application:
            for host, handlers in cls._routes.items():
                application.add_handlers(host, handlers)
        else:
            return reduce(lambda x, y: x + y, cls._routes.values()) if cls._routes else []

    @classmethod
    def url_for(cls, name, *args):
        named_handlers = dict([(spec.name, spec)
                               for spec in cls.routes() if spec.name])
        if name in named_handlers:
            return named_handlers[name].reverse(*args)
        raise KeyError("%s not found in named urls" % name)

route = Route


def try_except(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            f(self, *args, **kwargs)
        except Exception as e:
            logger.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.reply_error('未知错误: %s' % str(e))
    return wrapper



class RequestHandler(tornado.web.RequestHandler):

    def prepare(self):
        pass

    def on_finish(self):
        pass


    def reply_error(self, msg='未知错误'):
        resp = json.dumps({"code": 1, "msg": msg})
        logger.info(resp)
        self.set_header('Content-Type', 'application/json')
        self.write(resp)
        self.finish()

    def reply_data(self, data):
        resp = json.dumps({"code": 0, "data": data})
        self.write(resp)
        self.finish()

    def get_args(self, key, default=None, type=None):
        if type == list:
            if default is None:
                default = []
            return self.get_arguments(key, default)
        value = self.get_argument(key, default)
        if value and type:
            try:
                value = type(value)
            except ValueError:
                value = default
        return value


class ErrorHandler(RequestHandler):

    def get(self, *args, **kwargs):
        self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.reply_error('错误的请求路径')


@route(r'/stk/kline/(\w+)', name='kline')
class KlineHandler(RequestHandler):
    '''
    委托下单
    '''
    @try_except
    def get(self, code):
        self.render("kline.html", code=code)

    @try_except
    def post(self, code):
        if not code:
            raise Exception('用户名或密码错误')
        duration = self.get_args('duration')
        enddate = self.get_args('enddate', '')
        if duration == 'daily':
            data = get_db_data(code, 'daily', enddate=enddate)
            # data = get_daily_data(code, enddate)
        elif duration == 'weekly':
            data = get_db_data(code, 'weekly', enddate=enddate)
            # data = get_weekly_data(code, enddate)
        else:
            data = get_db_data(code, 'monthly', enddate=enddate)
            # data = get_monthly_data(code, enddate)
        if not data:
            self.reply_error('数据错误')
        else:
            self.reply_data(data)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = Route.routes()
        handlers.append((r"/(.*)", ErrorHandler))
        settings = dict(
            debug=True,
            cookie_secret='078dace7a01f4741b9204ddc12052b3a',
            xsrf_cookies=False,
            gzip=True,
            autoescape=None,
            static_path=CURDIR
        )

        tornado.web.Application.__init__(self, handlers, **settings)


define("port", default=8889, help="Run server on a specific port", type=int)


def run_server():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ins = tornado.ioloop.IOLoop.instance()
    # 定时记录监控数据
    INTERVAL = datetime.timedelta(seconds=600)
    def monitor_crontab():
        logger.info("hello")
        ins.add_timeout(INTERVAL, monitor_crontab)
    ins.add_timeout(INTERVAL, monitor_crontab)
    logger.info("Start...")
    ins.start()

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('server.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = get_logger()


if __name__ == "__main__":
    tornado.options.parse_command_line()
    run_server()

