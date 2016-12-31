#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

./macd.py macd --filename=ALL --data-dir=sina_ohlc_daily --macd-dir=sina_macd_daily
./macd.py macd --filename=ALL --data-dir=sina_ohlc_weekly --macd-dir=sina_macd_weekly
./macd.py macd --filename=ALL --data-dir=sina_ohlc_monthly --macd-dir=sina_macd_monthly

./macd.py macd --filename=ALL --data-dir=hs_ohlc_daily --macd-dir=hs_macd_daily
./macd.py macd --filename=ALL --data-dir=hs_ohlc_weekly --macd-dir=hs_macd_weekly
./macd.py macd --filename=ALL --data-dir=hs_ohlc_monthly --macd-dir=hs_macd_monthly

