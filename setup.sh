#!/bin/bash

# Script to transform data from armchairanalysis.com
# into format ready for insertion into Postgres database
# trey.causey at gmail

# Dependencies: 
# armchair analysis data
# Advanced NFL Stats 2013 play by play data https://docs.google.com/file/d/0BxEXxf9odCnMYlJpaGx2NG5RZVk/edit
# csvkit http://csvkit.readthedocs.org/en/latest/
# PostgreSQL 

# Usage:
# setup.sh armchair_analysis_zipfilename desired_database_name

if [ -d thespread ]; then
	if [ -d thespread/data ]; then
		echo "Data directories found."
	else
		echo "Creating directories..."
		mkdir data
	fi
else
	echo "Creating directories..."
	mkdir thespread
	mkdir thespread/data
fi

if [ -f $1 ]; then
	unzip $1 -d thespread/data
	cd thespread/data
else
	echo "Data file not found."
	exit 1
fi

if [ -f FLAT\ FILE.csv ]; then
	echo "Flat file found."
else
	echo "Flat file not found."
	exit 1
fi

if [ -f flat_file_reduced.csv ]; then
	echo "Reduced flat file already found."
else
	echo "Creating reduced flat file."
	csvcut --columns 1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18 FLAT\ FILE.csv > flat_file_reduced.csv
fi

echo "Your password is required to check if the database already exists."
echo "Creating database $2. This will delete any existing database with that name."
read -p "Continue? (y/n)"
if [ $REPLY != "y" ]; then
	echo "Aborting."
	exit 1
fi
echo "WARNING: This requires superuser access. You may need to provide your password several times."
echo "Trying to drop existing play-by-play data, may produce an error."
dropdb $2
sudo -u postgres createdb -O $USER $2
psql -f ../../training_data.sql pbp

echo "Adding 2013 play by play data from Advanced NFL Stats. Password required."
cd ../..
pwd

if [ -f 2013_nfl_pbp_data_through_wk_12.csv ]; then
	iconv --from-code=iso-8859-1 --to-code=utf-8 2013_nfl_pbp_data_through_wk_12.csv > 2013_nfl_pbp_data_through_wk_12_utf8.csv
	csvcut -c 1,2,3,4,5,6,7,8,9,10,15,16,17,18 2013_nfl_pbp_data_through_wk_12_utf8.csv > 2013_nfl_pbp_data_through_wk_12_reduced.csv
	psql -f test_data.sql pbp
else
	echo "Advanced NFL Stats 2013 play by play data not found. Download it from www.advancednflstats.com/2010/04/play-by-play-data.html."
	exit 1
fi

echo "Adding 2013 lines and team name maps. Password required."

if [ -f team_name_map.csv ] && [ -f nfl2013lines.csv ]; then
		echo "Creating tables for team name map and 2013 lines. You may need to provide your password."
		psql -f 2013lines.sql pbp
else
	echo "Lines and team name map not found."
	exit 1
fi

exit 0