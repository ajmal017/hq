$ mysql -uroot -p --local-infile=1
load data local infile '/tmp/all.data' into table daily fields terminated by ',' lines terminated by '\n';
