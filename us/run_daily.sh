#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

echo $CURDIR
echo "run_daily.py"


./run_daily.py --exchange=amex --symbol=ALL --date=20170105
./run_daily.py --exchange=nasdaq --symbol=ALL --date=20170105
./run_daily.py --exchange=nyse --symbol=ALL --date=20170105



