drop table amex;

create table if not exists `amex`(
  `id` int(11) primary key,
  `cid` varchar(128),
  `Symobl` varchar(32),
  `Name` varchar(256),
  `LastSale` varchar(64),
  `MarketCap` varchar(64),
  `IPOyear` varchar(64),
  `Sector` varchar(256),
  `Summary` varchar(2048),
);

