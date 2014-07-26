from subprocess import Popen, PIPE
import yaml

SCORER_PROGRAM=('python', 'score.py')
SCORER_CWD='scoring-2014'

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
        yaml.dump(proton, process.stdin)
        process.stdin.close()
        output = yaml.load(process.stdout)
        process.wait()
        if process.returncode != 0:
            message = 'Proton process failed, code={}'.format(process.returncode)
            raise RuntimeError(message)
        return output


    def calculate_scores(self):
        output = self._run_process()
        return {tla: output['scores'][tla]['score']
                  for tla in self.scoresheet.iterkeys()}

