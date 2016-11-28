create database stk;

create user 'newuser'@'localhost' identified by 'password';
grant all privileges on *.* to 'newuser'@'localhost';
flush privileges;


