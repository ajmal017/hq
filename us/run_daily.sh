#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

echo $CURDIR
echo "run_daily.py"

./run_daily.py --exchange=amex --symbol=ALL --date=20161225
./run_daily.py --exchange=amex --symbol=ALL --date=20161226
./run_daily.py --exchange=amex --symbol=ALL --date=20161227
./run_daily.py --exchange=amex --symbol=ALL --date=20161228
./run_daily.py --exchange=amex --symbol=ALL --date=20161229
./run_daily.py --exchange=amex --symbol=ALL --date=20161230
./run_daily.py --exchange=amex --symbol=ALL --date=20161231
./run_daily.py --exchange=amex --symbol=ALL --date=20170101
./run_daily.py --exchange=amex --symbol=ALL --date=20170102
./run_daily.py --exchange=amex --symbol=ALL --date=20170103
./run_daily.py --exchange=amex --symbol=ALL --date=20170104
./run_daily.py --exchange=amex --symbol=ALL --date=20170105
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161225
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161226
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161227
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161228
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161229
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161230
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20161231
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170101
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170102
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170103
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170104
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170105
./run_daily.py --exchange=nyse --symbol=ALL --date=20161225
./run_daily.py --exchange=nyse --symbol=ALL --date=20161226
./run_daily.py --exchange=nyse --symbol=ALL --date=20161227
./run_daily.py --exchange=nyse --symbol=ALL --date=20161228
./run_daily.py --exchange=nyse --symbol=ALL --date=20161229
./run_daily.py --exchange=nyse --symbol=ALL --date=20161230
./run_daily.py --exchange=nyse --symbol=ALL --date=20161231
./run_daily.py --exchange=nyse --symbol=ALL --date=20170101
./run_daily.py --exchange=nyse --symbol=ALL --date=20170102
./run_daily.py --exchange=nyse --symbol=ALL --date=20170103
./run_daily.py --exchange=nyse --symbol=ALL --date=20170104
./run_daily.py --exchange=nyse --symbol=ALL --date=20170105



