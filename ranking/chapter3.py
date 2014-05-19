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

team_points['massey_ratings'] = massey_ratings
team_points.sort('massey_ratings', ascending=False)

# Massey's Method
# masseyratings.com
# Part of the old BCS
# least squares method:
# r_i - r_j = y_k
# where y_k is MoV for game k and r_i and r_j are ratings
# of teams i and j
# Equation for every game k which creates m linear equations
# and n unknowns
# Xr = y
# Each row of coefficient matrix X is all 0s except 1 in i
# and -1 in j meaning i beat j in that game
# solution is X'Xr = X'y 
# M = X'X where Mij is the # of games played by team i and 
# off diagonal element Mij for i != j is negation of # of games
# played by team i against team j
# Becomes Mr = p where M is nxn matrix, r is n x 1 vector
# of unknown ratings and p n x 1 is cumulative point diffs

# Overall rating r_i = o_i + d_i
# overall pt_diff can be decomposed into f - a
# coefficient matrix M can be decomposed into T - P
# where T is diagonal matrix holding total # of games played
# by each team and P is off diagonal matrix holding
# number of pairwise matchups

t_matrix = np.diag(np.repeat(num_games, len(teams)))

p_matrix = np.diag(np.repeat(0, len(teams)))
for i in range(len(teams)):
    for j in range(len(teams)):
        if i == j:
            continue
        p_matrix[i][j] = abs(game_matrix[i][j])

rhs = np.dot(t_matrix, massey_ratings) - team_points.points_for.values
team_points['defense_ratings'] = np.linalg.lstsq((t_matrix + p_matrix), rhs)[0]
team_points['offense_ratings'] = massey_ratings - defense_ratings

team_points.sort('massey_ratings', ascending=False)['massey_ratings']

team_points.sort('offense_ratings', ascending=False)['offense_ratings']

team_points.sort('defense_ratings', ascending=False)['defense_ratings']



