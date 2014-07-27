
import mock

# Hack the path
import helpers as test_helpers

from scores import LeagueScores, TeamScore

def get_basic_data():
    the_data = {
        'match_number': 123,
        'arena_id': 'A',
        'teams': {
            'JMS': {
                'score': 4,
                'disqualified': True,
                'zone': 3
            },
            'PAS': {
                'score': 0,
                'present': False,
                'zone': 4
            },
            'RUN': {
                'score': 8,
                'zone': 1
            },
            'ICE': {
                'score': 2,
                'zone': 2
            }
        }
    }
    return the_data

def load_data(the_data):
    teams = the_data['teams'].keys()
    return load_datas([the_data], teams)

def load_datas(the_datas, teams):
    my_datas = the_datas[:]
    the_files = ['whatever-{0}.yaml'.format(i) for i in xrange(len(the_datas))]
    def loader(*args):
        assert len(my_datas), "Should not be loading additional files"
        return my_datas.pop(0)

    with mock.patch('matches.yaml_loader.load') as mock_loader, \
            mock.patch('scores.results_finder') as mock_finder:

        mock_finder.return_value = the_files
        mock_loader.side_effect = loader

        scores = LeagueScores('somewhere', teams, test_helpers.FakeScorer)
        return scores

def load_basic_data():
    return load_data(get_basic_data())

def test_game_points():
    scores = load_basic_data()

    games = scores.game_points
    assert len(games) == 1

    id_ = ('A', 123)
    assert id_ in games

    game = games[id_]

    assert game == {'JMS': 4, 'PAS': 0, 'RUN': 8, 'ICE': 2}

def test_league_points():
    scores = load_basic_data()

    leagues = scores.ranked_points
    assert len(leagues) == 1

    id_ = ('A', 123)
    assert id_ in leagues

    league = leagues[id_]

    assert league == {'JMS': 0, 'PAS': 0, 'RUN': 8, 'ICE': 6}

def test_team_points():
    scores = load_basic_data()

    expected = {
        'JMS': TeamScore(0, 4),
        'PAS': TeamScore(0, 0),
        'RUN': TeamScore(8, 8),
        'ICE': TeamScore(6, 2),
    }

    teams_data = scores.teams
    assert teams_data == expected


def test_last_scored_match():
    m_1 = get_basic_data()
    m_1['match_number'] = 1
    scores = load_data(m_1)

    lsm = scores.last_scored_match
    assert lsm == 1, "Should match id of only match present."

def test_last_scored_match_none():
    scores = load_datas([], [])

    lsm = scores.last_scored_match
    assert lsm is None, "Should be none when there are no scores."

def test_last_scored_match_some_missing():
    scores = load_basic_data()

    lsm = scores.last_scored_match
    assert lsm == 123, "Should match id of only match present."

def test_last_scored_match_many_scores():
    m_1 = get_basic_data()
    m_1['match_number'] = 1

    m_2B = get_basic_data()
    m_2B['match_number'] = 2
    m_2B['arena_id'] = 'B'

    scores = load_datas([m_1, m_2B], m_1['teams'].keys())

    lsm = scores.last_scored_match

    assert lsm == 2, "Should latest match id, even when in other arena."


def test_league_ranker_simple():
    team_scores = { 'ABC': TeamScore(), 'DEF': TeamScore(4, 5) }
    ranking = LeagueScores.rank_league(team_scores)
    expected_map = {
        'DEF': 1,
        'ABC': 2,
    }
    expected_order = ['DEF', 'ABC']

    assert expected_map == ranking
    order = ranking.keys()
    assert expected_order == order

def test_league_ranker_league_tie():
    team_scores = {
        'ABC': TeamScore(4, 0),
        'DEF': TeamScore(4, 5),
        'GHI': TeamScore(),
    }
    ranking = LeagueScores.rank_league(team_scores)
    expected_map = {
        'DEF': 1,
        'ABC': 2,
        'GHI': 3,
    }
    expected_order = ['DEF', 'ABC', 'GHI']

    assert expected_map == ranking
    order = ranking.keys()
    assert expected_order == order

def test_league_ranker_game_tie():
    team_scores = {
        'ABC': TeamScore(0, 5),
        'DEF': TeamScore(4, 5),
        'GHI': TeamScore(),
    }
    ranking = LeagueScores.rank_league(team_scores)
    expected_map = {
        'DEF': 1,
        'ABC': 2,
        'GHI': 3,
    }
    expected_order = ['DEF', 'ABC', 'GHI']

    assert expected_map == ranking
    order = ranking.keys()
    assert expected_order == order

## TODO: how do we resolve full ties?
## TODO: build something to alert us that we have a full tie.

def test_league_ranker_full_tie():
    team_scores = {
        'ABC': TeamScore(4, 5),
        'DEF': TeamScore(4, 5),
        'GHI': TeamScore(),
    }
    ranking = LeagueScores.rank_league(team_scores)
    expected_map = {
        'DEF': 1,
        'ABC': 1,
        'GHI': 3,
    }
    expected_order = ['ABC', 'DEF', 'GHI']

    assert expected_map == ranking
    order = ranking.keys()
    assert expected_order == order
