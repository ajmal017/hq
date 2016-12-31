#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

cat hs_macd_daily/*.txt    >  /data2/hs_indexs_macd_daily.txt
cat hs_macd_weekly/*.txt   >  /data2/hs_indexs_macd_weekly.txt
cat hs_macd_monthly/*.txt  >  /data2/hs_indexs_macd_monthly.txt

cat hs_ohlc_daily/*.txt    >  /data2/hs_indexs_ohlc_daily.txt
cat hs_ohlc_weekly/*.txt   >  /data2/hs_indexs_ohlc_weekly.txt
cat hs_ohlc_monthly/*.txt  >  /data2/hs_indexs_ohlc_monthly.txt

cat sina_macd_daily/*.txt   >   /data2/sina_goods_macd_daily.txt
cat sina_macd_weekly/*.txt  >   /data2/sina_goods_macd_weekly.txt
cat sina_macd_monthly/*.txt >   /data2/sina_goods_macd_monthly.txt

cat sina_ohlc_daily/*.txt   >    /data2/sina_goods_ohlc_daily.txt
cat sina_ohlc_weekly/*.txt  >    /data2/sina_goods_ohlc_weekly.txt
cat sina_ohlc_monthly/*.txt >    /data2/sina_goods_ohlc_monthly.txt

cat investing/investing_macd_daily/*.txt   >   /data2/investing_macd_daily.txt
cat investing/investing_macd_weekly/*.txt  >   /data2/investing_macd_weekly.txt
cat investing/investing_macd_monthly/*.txt >   /data2/investing_macd_monthly.txt

cat investing/investing_ohlc_daily/*.txt   >   /data2/investing_ohlc_daily.txt
cat investing/investing_ohlc_weekly/*.txt  >   /data2/investing_ohlc_weekly.txt
cat investing/investing_ohlc_monthly/*.txt >   /data2/investing_ohlc_monthly.txt


