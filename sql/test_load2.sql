load data local infile '/data/gh/hq/ohlc_daily/000001.txt'
into table ohlc_daily
fields terminated by ','
(date,code,open,high,close,low,volume,amount);


load data local infile '/data/gh/hq/ohlc_weekly/000001.txt'
into table ohlc_weekly
fields terminated by ','
(date,code,open,high,low,close);

load data local infile '/data/gh/hq/ohlc_monthly/000001.txt'
into table ohlc_monthly
fields terminated by ','
(date,code,open,high,low,close);


load data local infile '/data/gh/hq/macd_daily/000001.txt'
into table macd_daily
fields terminated by ',';

load data local infile '/data/gh/hq/macd_weekly/000001.txt'
into table macd_weekly
fields terminated by ',';

load data local infile '/data/gh/hq/macd_monthly/000001.txt'
into table macd_monthly
fields terminated by ',';

