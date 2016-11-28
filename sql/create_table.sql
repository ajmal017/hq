drop table ohlc_daily;

create table if not exists `ohlc_daily` (
  `id` int(11) not null auto_increment,
  `date` int(11) not null,
  `code` char(6) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  `volume` float(24, 4),
  `money` float(24, 4),
  primary key  (`date`, `code`)
);

show index from ohlc_daily;


drop table ohlc_weekly;

create table if not exists `ohlc_weekly` (
  `id` int(11) not null auto_increment,
  `date` int(11) not null,
  `code` char(6) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  primary key  (`date`, `code`)
);

show index from ohlc_weekly;


drop table ohlc_monthly;

create table if not exists `ohlc_monthly` (
  `id` int(11) not null auto_increment,
  `date` int(11) not null,
  `code` char(6) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  primary key  (`date`, `code`)
);

show index from ohlc_monthly;

