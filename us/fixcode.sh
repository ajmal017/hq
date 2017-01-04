#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

./fixcode.py --filename=ALL --src-dir=amex_macd_monthly
./fixcode.py --filename=ALL --src-dir=amex_macd_weekly

./fixcode.py --filename=ALL --src-dir=nyse_macd_monthly
./fixcode.py --filename=ALL --src-dir=nyse_macd_weekly

./fixcode.py --filename=ALL --src-dir=nasdaq_macd_monthly
./fixcode.py --filename=ALL --src-dir=nasdaq_macd_weekly


