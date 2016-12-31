#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

./fixdaily.py --filename=ALL --src-dir=amex_daily --dest-dir=fix_amex_daily
# ./fixdaily.py --filename=ALL --src-dir=nasdaq_daily --dest-dir=fix_nasdaq_daily
./fixdaily.py --filename=ALL --src-dir=nyse_daily --dest-dir=fix_nyse_daily
