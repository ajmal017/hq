create database stk;

create user 'newuser'@'localhost' identified by 'password';
grant all privileges on *.* to 'newuser'@'localhost';
flush privileges;

alter table `ohlc_daily` change `money` `amount` float(24, 4) not null;

$ mysql -uroot -p --local-infile=1
load data local infile '/tmp/all.data' into table daily fields terminated by ',' lines terminated by '\n';


