from subprocess import Popen, PIPE
import yaml

SCORER_PROGRAM=('python', 'score.py')
SCORER_CWD='scoring-2014'

# Running the scorer can be slow, so we cache results
_score_cache = {}

class Scorer(object):
    def __init__(self, scoresheet):
        self.scoresheet = scoresheet

    def _generate_proton(self):
        return {'match_number': 0, # dummy data
                'arena_id': 'main', # dummy data
                'teams': self._generate_teams_proton()}

    def _generate_teams_proton(self):
        return {tla: dict(data, zone=zone)
                for zone, (tla, data) in enumerate(self.scoresheet.iteritems())}

    def _run_process(self):
        proton = self._generate_proton()
        process = Popen(SCORER_PROGRAM,
                        stdin=PIPE,
                        stdout=PIPE,
                        cwd=SCORER_CWD)
        program_input = yaml.dump(proton)
        cached_output = _score_cache.get(program_input, None)
        if cached_output is not None:
            return cached_output
        process.stdin.write(program_input)
        process.stdin.close()
        output = yaml.load(process.stdout)
        process.wait()
        if process.returncode != 0:
            message = 'Proton process failed, code={}'.format(process.returncode)
            raise RuntimeError(message)
        _score_cache[program_input] = output
        return output


    def calculate_scores(self):
        output = self._run_process()
        return {tla: output['scores'][tla]['score']
                  for tla in self.scoresheet.iterkeys()}

