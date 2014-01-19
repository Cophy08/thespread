#!/usr/bin/python
# Loads and preprocesses NFL play-by-play data

# Loads the play by play data from a local Postgres database

import numpy as np
import pandas as pd
import pandas.io.sql as psql
import psycopg2
import cPickle
import re

# Load database credentials from a serialized file
# creds.pkl is a dict serialized with cPickle
# and takes the format
# {'user' : username, 'password': password}

with open('creds.pkl', 'rb') as pkl_file:
	creds = cPickle.load(pkl_file)

conn = psycopg2.connect(database = 'pbp', user = creds['user'], password = creds['password'])
sql = "select wpd.*, \
       case when wpd.off = g.v then g.sprv else -(g.sprv) end as sprv, g.ou, \
       case when wpd.off = wpd.winner then 1 else 0 end as teamwin, \
       (wpd.ptso - wpd.ptsd) as scorediff \
       from win_prob_data wpd \
       left join games g\
       on wpd.gid = g.gid\
       where wpd.pid >= 42246 and wpd.qtr <= 4 \
       and wpd.type != 'NOPL' \
       and wpd.dwn is not null and wpd.gid in (select gid from games \
       where week <= 17) \
       order by wpd.gid asc, wpd.pid asc"
df = psql.read_frame(sql, conn)

test_sql = "select gid, qtr, min, sec, off, def, yfog, \
			dwn, ytg, scorediff, teamwin, sec_adj \
			from win_prob_test_data \
			where dwn is not null and qtr <= 4 \
			order by gid asc, qtr asc, min desc, sec desc;"
test_df = psql.read_frame(test_sql, conn)

games_sql = "select * from games where week <= 17 order by gid asc;"
games_df = psql.read_frame(games_sql, conn)

test_lines_sql = "select tl.date, tnma.short_name as v, tnmb.short_name as h, tl.sprv, tl.ou \
                  from test_lines tl \
                  left join team_name_map tnma \
                  on tl.v = tnma.long_name \
                  left join team_name_map tnmb \
                  on tl.h = tnmb.long_name \
                  order by date asc;"
test_lines_df = psql.read_frame(test_lines_sql, conn)
conn.close()

# Create score differential variable and identify which plays belong to winning teams.
df['sec_adj_sqrt'] = 1/np.sqrt(1 + df['sec_adj'])
test_df['sec_adj_sqrt'] = 1/np.sqrt(1 + test_df['sec_adj'])

# The training data from armchairanalysis.com already has the spread and the total line. 
# Now we need to prep it for the test data (from advancednflstats.com).
# Test data lines are from: http://www.repole.com/sun4cast/data.html

test_df = pd.concat([test_df, pd.DataFrame(test_df['gid'].apply(lambda x: [i.strip() for i in re.split('@|_', x)][1:]).tolist(), 
             columns=['v','h'])], axis=1)

test_df = pd.merge(test_df, test_lines_df[['v', 'h', 'sprv', 'ou']], left_on=['v', 'h'], right_on=['v', 'h'])
test_df['sprv'][test_df['h'] == test_df['off']] = -test_df['sprv']
del test_df['v'], test_df['h']

del test_lines_df