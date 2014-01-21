drop table if exists win_prob_test_data;

create table win_prob_test_data (
gid char(20),
qtr int,
min int,
sec char(2),
off char(3),
def char(3),
dwn int,
ytg int,
ydline int,
scorediff int,
teamwin int,
ptso int,
ptsd int,
season int
);

-- Note has 2012 season in there as well

\copy win_prob_test_data from 2013_nfl_pbp_data_through_wk_12_reduced.csv with csv header delimiter as ',';


-- Clean up some parsing errors
update win_prob_test_data
	set min = 43, sec = 35
	where gid = '20130929_NE@ATL'
	and sec = '**';

update win_prob_test_data
	set min = 23, sec = 19
	where gid = '20131017_SEA@ARI'
	and sec = '**';

update win_prob_test_data
	set min = 7, sec = 30
	where gid = '20131103_KC@BUF'
	and sec = '**';

update win_prob_test_data
	set min = 54, sec = 10
	where gid = '20131121_NO@ATL'
	and sec = '**';

delete from win_prob_test_data
	where sec = '**';

delete from win_prob_test_data
	where season = 2012;
	
alter table win_prob_test_data
	alter sec type int using (sec::integer);

alter table win_prob_test_data
	add column yfog int;

update win_prob_test_data
	set yfog = 100 - ydline;

alter table win_prob_test_data
	add column sec_adj int;

update win_prob_test_data
	set sec_adj = min * 60 + sec;
