drop table if exists team_name_map;

create table team_name_map (
short_name char(3),
long_name text
);

\copy team_name_map from team_name_map.csv with csv header delimiter as ',';

drop table if exists test_lines;

create table test_lines (
date date,
v text,
visit_score int,
h text,
home_score int,
sprv float,
ou float
);

\copy test_lines from nfl2013lines.csv with csv header delimiter as ',';