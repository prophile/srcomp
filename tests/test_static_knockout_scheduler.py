
from collections import OrderedDict
from datetime import datetime, timedelta
import mock

# Hack the path
import helpers as test_helpers

from scores import TeamScore
from matches import Match, UNKNOWABLE_TEAM, KNOCKOUT_MATCH, LEAGUE_MATCH
from static_knockout_scheduler import StaticScheduler

def get_config():
    return {
        0: {
            0: {
                'arena': 'A',
                'start_time': datetime(2014, 4, 27, 14, 30),
                'teams': ['S3', 'S5', 'S8', 'S10']
            },
            1: {
                'arena': 'A',
                'start_time': datetime(2014, 4, 27, 14, 35),
                'teams': ['S4', 'S6', 'S7', 'S9']
            }
        },
        1: {
            0: {
                'arena': 'A',
                'start_time': datetime(2014, 4, 27, 14, 45),
                'teams': ['S2', '000', '002', '011']
            },
            1: {
                'arena': 'A',
                'start_time': datetime(2014, 4, 27, 14, 50),
                'teams': ['S1', '001', '010', '012']
            }
        },
        2: {
            0: {
                'arena': 'A',
                'start_time': datetime(2014, 4, 27, 15, 00),
                'teams': ['100', '101', '110', '111']
            }
        }
    }

def get_scheduler(matches = None, positions = None, \
                    knockout_points = None, league_game_points = None, \
                    delays = None):
    matches = matches or []
    delays = delays or []
    match_period = timedelta(minutes = 5)
    league_game_points = league_game_points or {}
    knockout_points = knockout_points or {}
    if not positions:
        positions = OrderedDict()
        positions['AAA'] = 1
        positions['BBB'] = 2
        positions['CCC'] = 3
        positions['DDD'] = 4
        positions['EEE'] = 5
        positions['FFF'] = 6
        positions['GGG'] = 7
        positions['HHH'] = 8
        positions['III'] = 9
        positions['JJJ'] = 10

    league_schedule = mock.Mock(matches = matches, delays = delays, \
                                match_period = match_period)
    league_scores = mock.Mock(positions = positions, game_points = league_game_points)
    knockout_scores = mock.Mock(ranked_points = knockout_points)
    scores = mock.Mock(league = league_scores, knockout = knockout_scores)

    period_config = {
        "description": "A description of the period",
        "start_time":   datetime(2014, 03, 27,  13),
        "end_time":     datetime(2014, 03, 27,  17, 30),
    }
    config = {
        'match_periods': { 'knockout': [period_config] },
        'static_knockout': get_config(),
    }
    arenas = ['A']
    scheduler = StaticScheduler(league_schedule, scores, arenas, config)
    return scheduler

def test_full():
    scheduler = get_scheduler()
    scheduler.add_knockouts()

    period = scheduler.period

    expected = [
        {'A': Match(0, 'A', ['CCC', 'EEE', 'HHH', 'JJJ'], datetime(2014, 4, 27, 14, 30), datetime(2014, 4, 27, 14, 35), KNOCKOUT_MATCH) },
        {'A': Match(1, 'A', ['DDD', 'FFF', 'GGG', 'III'], datetime(2014, 4, 27, 14, 35), datetime(2014, 4, 27, 14, 40), KNOCKOUT_MATCH) },
        {'A': Match(2, 'A', ['BBB', '???', '???', '???'], datetime(2014, 4, 27, 14, 45), datetime(2014, 4, 27, 14, 50), KNOCKOUT_MATCH) },
        {'A': Match(3, 'A', ['AAA', '???', '???', '???'], datetime(2014, 4, 27, 14, 50), datetime(2014, 4, 27, 14, 55), KNOCKOUT_MATCH) },
        {'A': Match(4, 'A', ['???', '???', '???', '???'], datetime(2014, 4, 27, 15, 00), datetime(2014, 4, 27, 15, 05), KNOCKOUT_MATCH) },
    ]

    for i in range(len(expected)):
        e = expected[i]
        a = period.matches[i]

        assert e == a, "Match {0} in the knockouts".format(i)
