drop table if exists win_prob_data;

create table win_prob_data (
gid int,
pid int,
off char(3),
def char(3),
type char(4),
dseq int,
len int,
qtr int,
min char(10),
sec int,
ptso int,
ptsd int,
timo int,
timd int,
dwn int default null,
ytg int default null,
yfog int default null
);

\copy win_prob_data from flat_file_reduced.csv with csv header delimiter as ',';

update win_prob_data
		set min = case when min ~ ':' then 0 else min::integer end;

alter table win_prob_data
	alter min type int using (min::integer);

drop table if exists games;

create table games (
gid int,
seas int,
week int,
day char(3),
v char(3),
h char(3),
stad char(60),
temp char(5),
humd int,
wspd char(5),
wdir char(5),
cond char(60),
surf char(60),
ou real,
sprv real,
ptsv int,
ptsh int
);

\copy games from GAMES.csv with csv header delimiter as ',' null as '\N';

alter table win_prob_data 
add column sec_adj int,
add column winner char(3);

update win_prob_data
	set sec_adj = 
	case when qtr = 1 then (min + 45) * 60 + sec
		 when qtr = 2 then (min + 30) * 60 + sec
		 when qtr = 3 then (min + 15) * 60 + sec
		 when qtr = 4 then (min * 60) + sec 
		 end
		 ;

drop table if exists winners;

create table winners (
gid int,
winner char(3)
);

insert into winners
select gid,
case 
when v > h then v 
when h > v then h 
when v = h then 'TIE' 
end as winner
from games g;

update win_prob_data wpd
set winner = w.winner
from winners w
where w.gid = wpd.gid;

-- delete from win_prob_data
-- 	where type in (select distinct type from win_prob_data where dwn is null);
