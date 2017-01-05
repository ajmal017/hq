#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR
./macd.py macd --filename=ALL --data-dir=investing_ohlc_daily --macd-dir=investing_macd_daily
./macd.py macd --filename=ALL --data-dir=investing_ohlc_weekly --macd-dir=investing_macd_weekly
./macd.py macd --filename=ALL --data-dir=investing_ohlc_monthly --macd-dir=investing_macd_monthly
