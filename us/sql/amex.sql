drop table amex_ohlc_daily;

create table if not exists `amex_ohlc_daily` (
  `date` int(11) not null,
  `code` int(11) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  primary key (`date`, code)
);

show index from amex_ohlc_daily;


drop table amex_ohlc_weekly;

create table if not exists `amex_ohlc_weekly` (
  `date` int(11) not null,
  `code` int(11) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  primary key (`date`, code)
);

show index from amex_ohlc_weekly;


drop table amex_ohlc_monthly;

create table if not exists `amex_ohlc_monthly` (
  `date` int(11) not null,
  `code` int(11) not null,
  `open` float(24, 4),
  `high` float(24, 4),
  `low` float(24, 4),
  `close` float(24, 4),
  primary key (`date`, code)
);

show index from amex_ohlc_monthly;

drop table amex_macd_daily;

create table if not exists `amex_macd_daily` (
`date` int(11) not null,
`code` int(11) not null,
`ma5` float(24, 4),
`ma10` float(24, 4),
`ma15` float(24, 4),
`ma20` float(24, 4),
`ma25` float(24, 4),
`ma30` float(24, 4),
`ma35` float(24, 4),
`ma40` float(24, 4),
`ma45` float(24, 4),
`ma50` float(24, 4),
`ma55` float(24, 4),
`ma60` float(24, 4),
`ma65` float(24, 4),
`ma70` float(24, 4),
`ma75` float(24, 4),
`ma80` float(24, 4),
`ma85` float(24, 4),
`ma90` float(24, 4),
`ma95` float(24, 4),
`ma100` float(24, 4),
`ma105` float(24, 4),
`ma110` float(24, 4),
`ma115` float(24, 4),
`ma120` float(24, 4),
`ma125` float(24, 4),
`ma130` float(24, 4),
`ma135` float(24, 4),
`ma140` float(24, 4),
`ma145` float(24, 4),
`ma150` float(24, 4),
`ma155` float(24, 4),
`ma160` float(24, 4),
`ma165` float(24, 4),
`ma170` float(24, 4),
`ma175` float(24, 4),
`ma180` float(24, 4),
`ma185` float(24, 4),
`ma190` float(24, 4),
`ma195` float(24, 4),
`ma200` float(24, 4),
`ma205` float(24, 4),
`ma210` float(24, 4),
`ma215` float(24, 4),
`ma220` float(24, 4),
`ma225` float(24, 4),
`ma230` float(24, 4),
`ma235` float(24, 4),
`ma240` float(24, 4),
`ma245` float(24, 4),
`ma250` float(24, 4),
primary key (`date`, code)
);

show index from amex_macd_daily;
drop table amex_macd_monthly;

create table if not exists `amex_macd_monthly` (
`date` int(11) not null,
`code` int(11) not null,
`ma5` float(24, 4),
`ma10` float(24, 4),
`ma15` float(24, 4),
`ma20` float(24, 4),
`ma25` float(24, 4),
`ma30` float(24, 4),
`ma35` float(24, 4),
`ma40` float(24, 4),
`ma45` float(24, 4),
`ma50` float(24, 4),
`ma55` float(24, 4),
`ma60` float(24, 4),
`ma65` float(24, 4),
`ma70` float(24, 4),
`ma75` float(24, 4),
`ma80` float(24, 4),
`ma85` float(24, 4),
`ma90` float(24, 4),
`ma95` float(24, 4),
`ma100` float(24, 4),
`ma105` float(24, 4),
`ma110` float(24, 4),
`ma115` float(24, 4),
`ma120` float(24, 4),
`ma125` float(24, 4),
`ma130` float(24, 4),
`ma135` float(24, 4),
`ma140` float(24, 4),
`ma145` float(24, 4),
`ma150` float(24, 4),
`ma155` float(24, 4),
`ma160` float(24, 4),
`ma165` float(24, 4),
`ma170` float(24, 4),
`ma175` float(24, 4),
`ma180` float(24, 4),
`ma185` float(24, 4),
`ma190` float(24, 4),
`ma195` float(24, 4),
`ma200` float(24, 4),
`ma205` float(24, 4),
`ma210` float(24, 4),
`ma215` float(24, 4),
`ma220` float(24, 4),
`ma225` float(24, 4),
`ma230` float(24, 4),
`ma235` float(24, 4),
`ma240` float(24, 4),
`ma245` float(24, 4),
`ma250` float(24, 4),
primary key (`date`, code)
);

show index from amex_macd_monthly;
drop table amex_macd_weekly;

create table if not exists `amex_macd_weekly` (
`date` int(11) not null,
`code` int(11) not null,
`ma5` float(24, 4),
`ma10` float(24, 4),
`ma15` float(24, 4),
`ma20` float(24, 4),
`ma25` float(24, 4),
`ma30` float(24, 4),
`ma35` float(24, 4),
`ma40` float(24, 4),
`ma45` float(24, 4),
`ma50` float(24, 4),
`ma55` float(24, 4),
`ma60` float(24, 4),
`ma65` float(24, 4),
`ma70` float(24, 4),
`ma75` float(24, 4),
`ma80` float(24, 4),
`ma85` float(24, 4),
`ma90` float(24, 4),
`ma95` float(24, 4),
`ma100` float(24, 4),
`ma105` float(24, 4),
`ma110` float(24, 4),
`ma115` float(24, 4),
`ma120` float(24, 4),
`ma125` float(24, 4),
`ma130` float(24, 4),
`ma135` float(24, 4),
`ma140` float(24, 4),
`ma145` float(24, 4),
`ma150` float(24, 4),
`ma155` float(24, 4),
`ma160` float(24, 4),
`ma165` float(24, 4),
`ma170` float(24, 4),
`ma175` float(24, 4),
`ma180` float(24, 4),
`ma185` float(24, 4),
`ma190` float(24, 4),
`ma195` float(24, 4),
`ma200` float(24, 4),
`ma205` float(24, 4),
`ma210` float(24, 4),
`ma215` float(24, 4),
`ma220` float(24, 4),
`ma225` float(24, 4),
`ma230` float(24, 4),
`ma235` float(24, 4),
`ma240` float(24, 4),
`ma245` float(24, 4),
`ma250` float(24, 4),
primary key (`date`, code)
);

show index from amex_macd_weekly;
