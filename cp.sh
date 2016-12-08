#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

scp hs_macd_daily/000001.txt /data2/hs_indexs_macd_daily.txt
scp hs_macd_weekly/000001.txt /data2/hs_indexs_macd_weekly.txt
scp hs_macd_monthly/000001.txt /data2/hs_indexs_macd_monthly.txt

scp hs_ohlc_daily/000001.txt /data2/hs_indexs_ohlc_daily.txt
scp hs_ohlc_weekly/000001.txt /data2/hs_indexs_ohlc_weekly.txt
scp hs_ohlc_monthly/000001.txt /data2/hs_indexs_ohlc_monthly.txt

scp sina_macd_daily/XAU.txt /data2/sina_goods_macd_daily.txt
scp sina_macd_weekly/XAU.txt /data2/sina_goods_macd_weekly.txt
scp sina_macd_monthly/XAU.txt /data2/sina_goods_macd_monthly.txt

scp sina_ohlc_daily/XAU.txt /data2/sina_goods_ohlc_daily.txt
scp sina_ohlc_weekly/XAU.txt /data2/sina_goods_ohlc_weekly.txt
scp sina_ohlc_monthly/XAU.txt /data2/sina_goods_ohlc_monthly.txt

scp investing/investing_macd_daily/XAU.txt /data2/investing_macd_daily.txt
scp investing/investing_macd_weekly/XAU.txt /data2/investing_macd_weekly.txt
scp investing/investing_macd_monthly/XAU.txt /data2/investing_macd_monthly.txt

scp investing/investing_ohlc_daily/XAU.txt /data2/investing_ohlc_daily.txt
scp investing/investing_ohlc_weekly/XAU.txt /data2/investing_ohlc_weekly.txt
scp investing/investing_ohlc_monthly/XAU.txt /data2/investing_ohlc_monthly.txt


