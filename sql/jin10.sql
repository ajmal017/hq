drop table jin10_news;

create table if not exists `jin10_news` (
  /*`id` int(11) not null auto_increment,*/
  `id` bigint(25) not null,
  `html` text not null,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  primary key (`id`)
);
