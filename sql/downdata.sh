#!/usr/bin/env bash

declare -a arr=("macd_daily" "macd_weekly" "macd_monthly" "ohlc_daily" "ohlc_weekly" "ohlc_monthly")

for i in "${arr[@]}"
do
    echo "$i"
    mkdir -p data/$i
    scp yhyan:/data/gh/hq/$i/000001.txt data/$i
    scp yhyan:/data/gh/hq/$i/000002.txt data/$i
done
