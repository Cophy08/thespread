# Who's #1? The Science of Rating and Ranking
# Chapter 3
# Colley's Methods

import numpy as np
import pandas as pd

path = '/home/trey/Downloads/nfl'

games = pd.read_csv('%s/GAMES.csv' % path)
games.columns = [c.lower() for c in games.columns.values]
games = games[games.seas == 2013]
# games = games[games.ptsv != games.ptsh]
games = games[games.week <= 17]
games['winner'] = games.apply(lambda x: x.h if x.ptsh > x.ptsv
                              else x.v, axis=1)
games['loser'] = games.apply(lambda x: x.h if x.ptsh < x.ptsv
                              else x.v, axis=1)
num_games = games.week.max() - 1
teams = sorted(games.h.unique())
team_ids = {team: i for i, team in enumerate(teams)}
wins = dict(games.groupby('winner')['winner'].count())
losses =  dict(games.groupby('loser')['loser'].count())

b_vector = [(1 + .5 * (wins[team] - losses[team])) for team in teams]

game_matrix = np.eye(len(teams)) * (2 + num_games) # C in Colley

# Credit to Sean Taylor for an easy way to create this matrix
for w, l in games[['winner', 'loser']].itertuples(index=False):
    game_matrix[team_ids[w], team_ids[l]] -= 1
    game_matrix[team_ids[l], team_ids[w]] -= 1

colley_ratings = np.linalg.solve(game_matrix, b_vector)

team_ratings = pd.DataFrame(index=teams)
team_ratings['colley_ratings'] = colley_ratings
team_ratings['win_pct'] = [wins[team] / float(wins[team] + 
                                              losses[team])
                           for team in teams]
team_ratings.sort('colley_ratings', ascending=False)

# DEN falls to 3rd (scores not taken into account)
# CAR climbs to 2nd, played NFC West, Saints, Patriots
# No offense / defense

points_for = dict.fromkeys(teams, 0)
points_against = dict.fromkeys(teams, 0)

for team in teams:
    home_points = games[games.h == team]['ptsh'].sum()
    away_points = games[games.v == team]['ptsv'].sum()
    points_for[team] = home_points + away_points
    home_conceded = games[games.h == team]['ptsv'].sum()
    away_conceded = games[games.v == team]['ptsh'].sum()
    points_against[team] = home_conceded + away_conceded

team_points = pd.DataFrame(index=teams)
team_points['points_for'] = pd.Series(points_for)
team_points['points_against'] = pd.Series(points_against)
team_points['point_diff'] = team_points.points_for - team_points.points_against

colley_massey_ratings = np.linalg.solve(game_matrix, 
                                 team_points.point_diff.values)

team_ratings['colley_massey_ratings'] = colley_massey_ratings
team_ratings.sort('colley_massey_ratings', ascending=False)


