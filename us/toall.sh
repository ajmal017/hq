#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

./toweek.py --filename=ALL --src-dir=fix_amex_daily --dest-dir=amex_weekly
./toweek.py --filename=ALL --src-dir=fix_nasdaq_daily --dest-dir=nasdaq_weekly
./toweek.py --filename=ALL --src-dir=fix_nyse_daily --dest-dir=nyse_weekly

./tomonth.py --filename=ALL --src-dir=fix_amex_daily --dest-dir=amex_monthly
./tomonth.py --filename=ALL --src-dir=fix_nasdaq_daily --dest-dir=nasdaq_monthly
./tomonth.py --filename=ALL --src-dir=fix_nyse_daily --dest-dir=nyse_monthly

