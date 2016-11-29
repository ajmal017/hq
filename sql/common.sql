create database stk;

create user 'newuser'@'localhost' identified by 'password';
grant all privileges on *.* to 'newuser'@'localhost';
flush privileges;

alter table `ohlc_daily` change `money` `amount` float(24, 4) not null;


