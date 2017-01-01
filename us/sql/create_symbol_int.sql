drop table us_symbol_int;

create table if not exists `us_symbol_int` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `symbol` varchar(32) not null unique
);
