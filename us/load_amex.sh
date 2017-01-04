#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $CURDIR

cd fix_amex_daily
for f in *.csv
do
    sql="load data local infile 'fix_amex_daily/"$f"' into table amex_ohlc_daily fields terminated by ',' (date,code,open,high,close,low);"
    echo $sql;
    # mysql -u stk --password=stkP@55word stk2 -e "$sql"
done

cd $CURDIR/amex_weekly
for f in *.csv
do
    sql="load data local infile 'amex_weekly/"$f"' into table amex_ohlc_weekly fields terminated by ',' (date,code,open,high,low,close);"
    echo $sql;
done

cd $CURDIR/amex_monthly
for f in *.csv
do
    sql="load data local infile 'amex_monthly/"$f"' into table amex_ohlc_monthly fields terminated by ',' (date,code,open,high,low,close);"
    echo $sql;
done

cd $CURDIR/amex_macd_daily
for f in *.csv
do
    sql="load data local infile 'amex_macd_daily/"$f"' into table amex_macd_daily fields terminated by ',' (date,code,ma5,ma10,ma15,ma20,ma25,ma30,ma35,ma40,ma45,ma50,ma55,ma60,ma65,ma70,ma75,ma80,ma85,ma90,ma95,ma100,ma105,ma110,ma115,ma120,ma125,ma130,ma135,ma140,ma145,ma150,ma155,ma160,ma165,ma170,ma175,ma180,ma185,ma190,ma195,ma200,ma205,ma210,ma215,ma220,ma225,ma230,ma235,ma240,ma245,ma250);"
    echo $sql;
done

cd $CURDIR/amex_macd_weekly
for f in *.csv
do
    sql="load data local infile 'amex_macd_weekly/"$f"' into table amex_macd_weekly fields terminated by ',' (date,code,ma5,ma10,ma15,ma20,ma25,ma30,ma35,ma40,ma45,ma50,ma55,ma60,ma65,ma70,ma75,ma80,ma85,ma90,ma95,ma100,ma105,ma110,ma115,ma120,ma125,ma130,ma135,ma140,ma145,ma150,ma155,ma160,ma165,ma170,ma175,ma180,ma185,ma190,ma195,ma200,ma205,ma210,ma215,ma220,ma225,ma230,ma235,ma240,ma245,ma250);"
    echo $sql;
done

cd $CURDIR/amex_macd_monthly
for f in *.csv
do
    sql="load data local infile 'amex_macd_monthly/"$f"' into table amex_macd_monthly fields terminated by ',' (date,code,ma5,ma10,ma15,ma20,ma25,ma30,ma35,ma40,ma45,ma50,ma55,ma60,ma65,ma70,ma75,ma80,ma85,ma90,ma95,ma100,ma105,ma110,ma115,ma120,ma125,ma130,ma135,ma140,ma145,ma150,ma155,ma160,ma165,ma170,ma175,ma180,ma185,ma190,ma195,ma200,ma205,ma210,ma215,ma220,ma225,ma230,ma235,ma240,ma245,ma250);"
    echo $sql;
done



