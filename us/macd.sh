#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

./macd.py --filename=ALL --src-dir=fix_amex_daily --dest-dir=amex_macd_daily
./macd.py --filename=ALL --src-dir=amex_weekly --dest-dir=amex_macd_weekly
./macd.py --filename=ALL --src-dir=amex_monthly --dest-dir=amex_macd_monthly

./macd.py --filename=ALL --src-dir=fix_nasdaq_daily --dest-dir=nasdaq_macd_daily
./macd.py --filename=ALL --src-dir=nasdaq_weekly --dest-dir=nasdaq_macd_weekly
./macd.py --filename=ALL --src-dir=nasdaq_monthly --dest-dir=nasdaq_macd_monthly

./macd.py --filename=ALL --src-dir=fix_nyse_daily --dest-dir=nyse_macd_daily
./macd.py --filename=ALL --src-dir=nyse_weekly --dest-dir=nyse_macd_weekly
./macd.py --filename=ALL --src-dir=nyse_monthly --dest-dir=nyse_macd_monthly


