#!/usr/bin/env bash

/data2/gh/hq/investing/run_daily.py --n=4 --curr-id=0 > /data2/logs/ist4.log 2>&1
/data2/gh/hq/investing/run_daily.py --n=3 --curr-id=0 > /data2/logs/ist3.log 2>&1
/data2/gh/hq/investing/run_daily.py --n=2 --curr-id=0 > /data2/logs/ist2.log 2>&1
/data2/gh/hq/investing/run_daily.py --n=1 --curr-id=0 > /data2/logs/ist1.log 2>&1
/data2/gh/hq/investing/run_daily.py --n=0 --curr-id=0 > /data2/logs/ist0.log 2>&1

