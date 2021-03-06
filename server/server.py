#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import math
import time
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

engine = create_engine(config.mysqlserver, echo=False, encoding="utf-8")

FROM_SQL = True
ohlc_cols = ','.join(['date', 'open', 'close', 'low', 'high'])
macd_cols = ','.join(['date'] + ['ma%s' % i for i in range(5, 91, 5)])
all_macd_cols = ','.join(['date'] + ['ma%s' % i for i in range(5, 251, 5)])

def get_aastocks():
    data = []
    with open(os.path.join(CURDIR, "stock.csv")) as fp:
        # code,display_name,name,start_date,end_date,type
        for i in fp:
            data.append(i.split(","))
    return data


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


def get_db_data(src, code, table, enddate='', limit=60):
    '''
    src in ['astock', 'hsindexs', 'sinagoods', 'investing']
    enddate 表示小于（不包括）这一天的数据
    '''
    data = {
        'dates': [],
        'ohlcs': [],
        'mas': {},
        'n': 0,
        'hasMore': 0
    }

    assert src in ['astock', 'hsindexs', 'sinagoods', 'investing', 'nasdaq', 'nyse', 'amex',
                   'idxs']
    _macd_cols = macd_cols
    if src == 'hsindexs':
        table_prefix = 'hs_indexs_'
        code = int(code)
    elif src == 'sinagoods':
        table_prefix = 'sina_goods_'
        code = '"%s"' % code
    elif src == 'investing':
        table_prefix = 'investing_'
        _macd_cols = all_macd_cols
        code = int(code)
    elif src in ('nasdaq', 'nyse', 'amex'):
        table_prefix = '%s_' % src
        code = int(code)
    elif src == 'idxs':
        table_prefix = 'idxs_'
        code = int(code)
        _macd_cols = all_macd_cols
    else:
        table_prefix = 'hs_stocks_'
        code = int(code)

    t0 = time.time()
    # limit+1 表示还没有新的数据
    if enddate:
        sql = '''select date from %sohlc_%s
        where date < %s and code = %s
        order by date desc limit %s
        ''' % (table_prefix, table, enddate, code, limit+1)
    else:
        sql = '''select date from %sohlc_%s
        where date > 0 and code = %s
        order by date desc limit %s
        ''' % (table_prefix, table, code, limit+1)
    date_df = pd.read_sql_query(sql, engine, index_col='date')
    nrows = len(date_df.index.values)
    if nrows == 0:
        return data
    elif nrows <= limit:
        data['n'] = nrows
        data['hasMore'] = 0
        startdate = date_df.index.values[-1]
    else:
        data['n'] = limit
        data['hasMore'] = 1
        startdate = date_df.index.values[-2]

    if enddate:
        ohlc_sql = '''
        SELECT %s FROM %sohlc_%s
        where date < %s and date >= %s and code = %s
        order by date desc limit %s
        ''' % (ohlc_cols, table_prefix, table, enddate, startdate, code, limit)
    else:
        ohlc_sql = '''
        SELECT %s FROM %sohlc_%s
        where date > %s and code = %s
        order by date desc limit %s
        ''' % (ohlc_cols, table_prefix, table, startdate, code, limit)
    ohlc_df  = pd.read_sql_query(ohlc_sql, engine, index_col='date')

    if enddate:
        macd_sql = '''
        SELECT %s FROM %smacd_%s
        where date < %s and date >= %s and code = %s
        order by date desc limit %s
        ''' % (_macd_cols, table_prefix, table, enddate, startdate, code, limit)
    else:
        macd_sql = '''
        SELECT %s FROM %smacd_%s
        where date > %s and code = %s
        order by date desc limit %s
        ''' % (_macd_cols, table_prefix, table, startdate, code, limit)
    macd_df  = pd.read_sql_query(macd_sql, engine, index_col='date')

    t1 = time.time()
    ohlc_df = ohlc_df.iloc[::-1]
    macd_df = macd_df.iloc[::-1]
    data['dates'] = ohlc_df.index.values.tolist()
    data['ohlcs'] = ohlc_df.to_records(index=False).tolist()
    for col in macd_df.columns:
        if col.startswith("ma"):
            data['mas'][col] = map(lambda i: i if i > 0 else '-', macd_df[col].values.tolist())

    t2 = time.time()

    data['t1'] = t1- t0
    data['t2'] = t2- t1
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
        try:
            engine.table_names()
        except Exception as e:
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

import sinacodes
import istcodes

@route(r'/ohlc/pages/(\w+)', name='pages')
class PagesHandler(RequestHandler):

    @try_except
    def get(self, page):
        html = "html/%s.html" % page
        if page == 'hsindexs':
            resp = {"data":sinacodes.idxs}
        elif page == 'astock':
            resp = {}
            page = self.get_args('page', 1, int)
            page_size = 100
            skip_size = (page-1) * page_size
            # sql = '''select
            # code, name, industry, area, pe, outstanding, totals, timeToMarket
            # from stock_list limit %s offset %s''' % (page_size, skip_size)
            sql = '''select
            stock_list.code,
            stock_list.name,
            stock_list.industry,
            stock_list.area,
            stock_list.pe,
            stock_list.outstanding,
            stock_list.totals,
            stock_list.timeToMarket,
            stock_list.totals * stock_today.trade as marketCap
            from stock_list, stock_today where stock_list.code  = stock_today.code order by marketCap'''
            # desc limit %s offset %s''' % (page_size, skip_size)
            a = engine.execute(sql)
            resp['data'] = a.fetchall()
            resp['current_page'] = page
            c = engine.execute("select count(stock_list.code) from stock_list, stock_today where stock_list.code = stock_today.code")
            total_rows = c.fetchone()[0]
            resp['total_page'] = total_rows / page_size + ( 1 if total_rows % page_size else 0)
        elif page == 'aastocks':
            resp = {}
            page = self.get_args('page', 1, int)
            page_size = 100
            skip_size = (page-1) * page_size
            resp['data'] = get_aastocks()
            resp['current_page'] = page
            total_rows = len(resp['data'])
            resp['total_page'] = total_rows / page_size + ( 1 if total_rows % page_size else 0)
        elif page in ('nasdaq', 'nyse', 'amex'):
            html_page = page
            resp = {}
            page = self.get_args('page', 1, int)
            page_size = 100
            skip_size = (page-1) * page_size
            sql = '''select Symbol, Name, LastSale, MarketCap, industry, IPOYear
            from us_%s order by MarketCap ''' % html_page
            # desc limit %s offset %s''' % (html_page, page_size, skip_size)
            a = engine.execute(sql)
            resp['data'] = a.fetchall()
            resp['current_page'] = page
            c = engine.execute("select count(id) from us_%s" % html_page)
            total_rows = c.fetchone()[0]
            resp['total_page'] = total_rows / page_size + ( 1 if total_rows % page_size else 0)
        elif page in ['sz50s', 'hs300', 'zz500s']:
            resp = {}
            sql = '''select stock_%s.*, stock_list.industry
            from stock_%s,stock_list
            where stock_%s.code = stock_list.code
            ''' % (page, page, page)
            a = engine.execute(sql)
            resp['data'] = a.fetchall()
            if page in ['hs300', 'zz500s', 'sz50s']:
                resp['data'] = sorted(resp['data'], key=lambda item:item[1], reverse=True)
            resp['title'] = page
        elif page == 'dji':
            # 道琼斯指数成分股
            ss = ['AXP',  # 美国运通
                  'BA',  # 波音
                  'CVX',  # 雪佛龙
                  'CSCO',  # 思科
                  'AAPL',  # 苹果
                  'V',     # Visa
                  'CAT',   # 卡特彼勒
                  '3M',    # 3M
                  'VZ',    # 威瑞森
                  'HD',    # 家得宝
                  'IBM',   # IBM
                  'MSFT',  # 微软
                  'DIS',   # 迪士尼
                  'DD',    # 杜邦
                  'PG',    # 宝洁
                  'GS',    # 高盛
                  'INTC',  # 因特尔
                  'WMT',   # 沃尔玛
                  'GE',    # 通用电气
                  'MRK',   # 默克
                  'UNH',   # 联合健康保险
                  'PFE',   # 辉瑞
                  'UTX',   # 联合技术
                  'XOM',   # 艾克生美孚
                  'JPM',   # 摩根大通
                  'NKE',   # 耐克
                  'MCD',   # 麦丹劳
                  'KO',    # 可口可乐
                  'MMM',   # 3m
                  'TRV',   # 旅行家
                  'JNJ']   # 强生
            ss = "'" + "','".join(ss) + "'"
            resp = {}
            page = self.get_args('page', 1, int)

            sql = '''select Symbol, Name, LastSale, MarketCap, industry, IPOYear
            from us_nyse where Symbol in (%s) order by MarketCap ''' % ss
            a = engine.execute(sql)
            resp['data'] = a.fetchall()

            sql = '''select Symbol, Name, LastSale, MarketCap, industry, IPOYear
            from us_nasdaq where Symbol in (%s) order by MarketCap ''' % ss
            a = engine.execute(sql)
            resp['data'] += a.fetchall()
            resp['current_page'] = page
            resp['total_page'] = 1

        elif page == 'sinagoods':

            resp = {"data": sinacodes.goods}
        elif page == 'idxs':
            import idxs
            resp = {"data": idxs.indexs}
        elif page == 'istindexs':
            resp = {"data":istcodes.indexs}
        elif page == 'istfxpros':
            resp = {"data": istcodes.fxpros}
        elif page == 'istgoods':
            resp = {"data": istcodes.goods}
        elif page == 'istdebts':
            resp = {"data": istcodes.debts}
        else:
            tt = os.path.join(CURDIR, "html", "%s.html" % page)
            if not os.path.exists(tt):
                html = "html/index.html"
            resp = {}
        self.render(html, **resp)


    @try_except
    def post(self, page):
        if not page:
            raise Exception("wrong page.")
        if page == 'gdp':
            import gdp
            data = gdp.get_data(25)
            self.reply_data(data)
        else:
            raise Exception("unkown page.")


@route(r'/ohlc/(\w+)/(\w+)', name='kline')
class KlineHandler(RequestHandler):
    '''
    委托下单

    src in ['astock', 'hsindexs', 'sinagoods', 'investing']
    '''
    @try_except
    def get(self, src, code):
        resp = {
            "src": src,
            "code": code,
            "monthly": True,
            "weekly": True,
            "daily": True,
        }
        resp['title'] = "%s_%s" % (src, code)
        if src == 'hsindexs':
            resp['title'] = "%s(%s)" % (sinacodes.hsindexs.get(code, '').decode("utf-8"), code)
        elif src == 'sinagoods':
            for i in sinacodes.goods:
                if i[0] == code:
                    # resp['title'] = i[1]
                    resp['title'] = "%s(%s)" % (i[1].decode("utf-8"), code)
                    break
        elif src == 'idxs':
            import idxs
            resp['title'] = idxs.aa.get(code, code)
        elif src == 'investing':
            item = istcodes.currid2item.get(int(code))
            if item:
                resp['title'] = "%s(%s)" % (item['name'].decode("utf-8"), code)
        elif src in ('nasdaq', 'nyse', 'amex'):
            sql = 'select id from us_symbol_int where binary symbol = "%s"' % code
            a = engine.execute(sql)
            b = a.fetchone()
            if b:
                resp['code'] = b[0]
                # resp['weekly'] = resp['daily'] = False
            else:
                resp['text'] = 'no code'
                self.render("html/error.html", **resp)
        else:
            # 沪深股票
            sql = '''select code, name
            from stock_list where code = %s''' % int(code)
            a = engine.execute(sql)
            b = a.fetchone()
            if b:
                resp['title'] ="%s(%06d)" % (b[1], b[0])
        self.render("html/kline.html", **resp)

    @try_except
    def post(self, src, code):
        if not code:
            raise Exception('用户名或密码错误')
        duration = self.get_args('duration')
        enddate = self.get_args('enddate', '')
        if duration == 'daily':
            data = get_db_data(src, code, 'daily', enddate=enddate)
            # data = get_daily_data(code, enddate)
        elif duration == 'weekly':
            data = get_db_data(src, code, 'weekly', enddate=enddate)
            # data = get_weekly_data(code, enddate)
        else:
            data = get_db_data(src, code, 'monthly', enddate=enddate)
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

