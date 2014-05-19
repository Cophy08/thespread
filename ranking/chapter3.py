# Who's #1? The Science of Rating and Ranking
# Chapter 3
# Colley's Methods

# based on winning percentage
# team i rating r_i = w_i / t_i (wins / games played)

# ties in ratings are a problem
# strength of opponent not factored in
# undefined at beginning of season

# r_i = (1 + w_i) / (2 + t_i)
# Will be .5 when the season starts
# Laplace's rule
# Strength of Schedule hidden within
# Because everyone starts at 1/2, points added to ratings are zero-sum
# Cr = b where r is unknown ratings and b is rhs vector equal to
# b_i = 1 + 1/2 * (w_i - l_i) and C is Collecy coefficient matrix
# C_ij = {2 + t_i if i == j
#        {-n_ij   if i != j 
# where n_ij is number of times teams i and j played each other

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


