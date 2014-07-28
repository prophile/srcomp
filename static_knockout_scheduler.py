# A knockout scheduler which loads almost fixed data from the config.
# Assumes only a single arena

from collections import defaultdict

from matches import KnockoutScheduler, Match, MatchPeriod, \
                    UNKNOWABLE_TEAM, KNOCKOUT_MATCH, LEAGUE_MATCH

class StaticScheduler(KnockoutScheduler):
    def __init__(self, schedule, scores, arenas, config):
        super(StaticScheduler, self).__init__(schedule, scores, arenas, config)

    def get_team(self, team_ref):
        if not self._played_all_league_matches():
            return UNKNOWABLE_TEAM

        if team_ref.startswith('S'):
            # get a seeded position
            positions = self.scores.league.positions.keys()
            pos = int(team_ref[1:])
            pos -= 1 # seed numbers are 1 based
            return positions[pos]

        # get a position from a match
        assert len(team_ref) == 3
        round_num, match_num, pos = [int(x) for x in team_ref]
        match = self.knockout_rounds[round_num][match_num]

        assert match is not None, "Reference '{0}' to unscheduled match!".format(team_ref)

        ranking = self.get_ranking(match)
        return ranking[pos]

    def _add_match(self, match_info):
        new_matches = {}

        arena = match_info['arena']
        start_time = match_info['start_time']
        end_time = start_time + self.schedule.match_period
        num = len(self.schedule.matches)

        teams = []
        for team_ref in match_info['teams']:
            teams.append(self.get_team(team_ref))

        if len(teams) < 4:
            "Fill empty zones with None"
            teams += [None] * (4-len(teams))

        match = Match(num, arena, teams, start_time, end_time, KNOCKOUT_MATCH)
        self.knockout_rounds[-1].append(match)

        new_matches[match_info['arena']] = match

        self.schedule.matches.append(new_matches)
        self.period.matches.append(new_matches)

    def add_knockouts(self):
        period = self.config["match_periods"]["knockout"][0]
        self.period = MatchPeriod(period["start_time"], period["end_time"], \
                                  period["end_time"], period["description"], \
                                  [])

        knockout_conf = self.config["static_knockout"]

        for round_num in sorted(knockout_conf.keys()):
            self.knockout_rounds += [[]]
            for match_num in sorted(knockout_conf[round_num].keys()):
                match_info = knockout_conf[round_num][match_num]
                self._add_match(match_info)
