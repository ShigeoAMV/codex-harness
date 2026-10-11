import importlib.util
import json
import os
from pathlib import Path
import hashlib
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checks', ROOT / 'checks.py')
c = importlib.util.module_from_spec(spec)
if (ROOT / 'checks.py').exists():
    spec.loader.exec_module(c)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='check project spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = self.root / 'harness.checks.json'

    def configure(self, argv, **overrides):
        check = dict(name='unit', stages=['dev'], argv=argv, timeout_seconds=5)
        check.update(overrides)
        self.config.write_text(json.dumps({'schema': 1, 'profile': 'internal', 'checks': [check]}))

    def run_check(self, stage='dev'):
        self.assertTrue(hasattr(c, 'verify'), 'check runner not implemented')
        return c.verify(self.root, stage)

    def report(self):
        return json.loads((self.root / '.harness-evidence/result.json').read_text())

    def test_success_is_recorded(self):
        self.configure([sys.executable, '-c', 'print("ok")'])
        self.assertEqual(self.run_check(), 0)
        self.assertEqual(self.report()['status'], 'PASS')

    def test_evidence_identifies_runtime_runner_and_completion(self):
        self.configure(['{python}', '-c', 'pass'])
        self.assertEqual(self.run_check(), 0)
        report = self.report()
        self.assertTrue(report.get('selection_complete'))
        self.assertGreaterEqual(report.get('finished_at', ''), report['started_at'])
        self.assertEqual(report.get('runtime', {}).get('python'), sys.version.split()[0])
        self.assertEqual(report.get('runner_sha256'),
                         hashlib.sha256((ROOT / 'checks.py').read_bytes()).hexdigest())
        self.assertEqual(report.get('not_run'), [])

    def test_boolean_schema_is_rejected(self):
        self.configure(['{python}', '-c', 'pass'])
        config = json.loads(self.config.read_text())
        config['schema'] = True
        self.config.write_text(json.dumps(config))
        self.assertEqual(self.run_check(), 2)
        self.assertEqual(self.report()['checks'], [])

    def test_failure_records_remaining_checks_without_running_them(self):
        self.configure(['{python}', '-c', 'raise SystemExit(7)'])
        config = json.loads(self.config.read_text())
        config['checks'].append(dict(config['checks'][0], name='later', argv=[
            '{python}', '-c', 'from pathlib import Path; Path("unexpected").touch()']))
        self.config.write_text(json.dumps(config))
        self.assertEqual(self.run_check(), 1)
        self.assertEqual(self.report()['not_run'], ['later'])
        self.assertFalse((self.root / 'unexpected').exists())

    def test_failure_blocks(self):
        self.configure([sys.executable, '-c', 'raise SystemExit(7)'])
        self.assertEqual(self.run_check(), 1)
        self.assertEqual(self.report()['checks'][0]['exit_code'], 7)
        self.assertEqual(self.report()['status'], 'FAIL')

    def test_missing_executable_is_error(self):
        self.configure(['nonexistent-harness-canary-executable'])
        self.assertNotEqual(self.run_check(), 0)
        self.assertEqual(self.report()['status'], 'ERROR')

    def test_timeout_is_error(self):
        self.configure([sys.executable, '-c', 'import time; time.sleep(20)'], timeout_seconds=1)
        self.assertNotEqual(self.run_check(), 0)
        self.assertEqual(self.report()['status'], 'ERROR')
        self.assertEqual(self.report()['checks'][0].get('reason'), 'timeout')

    def test_missing_stage_cannot_pass(self):
        self.configure([sys.executable, '-c', 'pass'])
        self.assertNotEqual(self.run_check('security'), 0)
        self.assertEqual(self.report()['status'], 'ERROR')

    def test_invalid_config_replaces_stale_pass(self):
        self.configure([sys.executable, '-c', 'pass'])
        self.assertEqual(self.run_check(), 0)
        self.config.write_text('{broken')
        self.assertNotEqual(self.run_check(), 0)
        self.assertEqual(self.report()['status'], 'ERROR')

    def test_missing_config_cannot_pass(self):
        self.assertNotEqual(self.run_check(), 0)
        self.assertEqual(self.report()['status'], 'ERROR')

    def test_argv_is_not_a_shell_string(self):
        self.configure('echo success')
        self.assertNotEqual(self.run_check(), 0)

    def test_invalid_timeout_and_stage_rejected(self):
        for fields in ({'timeout_seconds': 0}, {'timeout_seconds': True}, {'stages': ['typo']}):
            with self.subTest(fields=fields):
                self.configure([sys.executable, '-c', 'pass'], **fields)
                self.assertNotEqual(self.run_check(), 0)

    def test_duplicate_names_rejected(self):
        self.configure([sys.executable, '-c', 'pass'])
        conf = json.loads(self.config.read_text())
        conf['checks'].append(conf['checks'][0])
        self.config.write_text(json.dumps(conf))
        self.assertNotEqual(self.run_check(), 0)

    def test_arguments_preserve_spaces_and_metacharacters(self):
        text = 'literal spaces & $() ; value'
        self.configure([sys.executable, '-c', 'import sys; assert sys.argv[1] == ' + repr(text), text])
        self.assertEqual(self.run_check(), 0)

    def test_python_token_uses_current_runtime(self):
        self.configure(['{python}', '-c', 'pass'])
        self.assertEqual(self.run_check(), 0)

    @unittest.skipUnless(os.name == 'nt', 'Windows taskkill fallback')
    def test_timeout_cleanup_still_kills_child_when_taskkill_fails(self):
        self.configure([sys.executable, '-c', 'import time; time.sleep(4)'], timeout_seconds=1)
        start = time.monotonic()
        with patch.object(c.subprocess, 'run', side_effect=OSError('taskkill unavailable')):
            self.assertNotEqual(self.run_check(), 0)
        self.assertLess(time.monotonic() - start, 3)

    def prepare_release(self, code='pass'):
        self.configure([sys.executable, '-c', code], stages=['release'])
        (self.root / '.gitignore').write_text('.harness-evidence/\n')
        for args in (['init', '-q'], ['add', '.'],
                     ['-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture']):
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def test_release_accepts_clean_commit(self):
        self.prepare_release()
        self.assertEqual(self.run_check('release'), 0)
        self.assertEqual(len(self.report()['git']['commit']), 40)

    def test_release_refuses_dirty_checkout(self):
        self.prepare_release()
        (self.root / 'untracked.txt').write_text('dirty')
        self.assertNotEqual(self.run_check('release'), 0)
        self.assertEqual(self.report()['checks'], [])
        self.assertEqual(self.report().get('not_run'), ['unit'])

    def test_release_requires_the_requested_commit_before_running_checks(self):
        self.prepare_release('from pathlib import Path; Path("unexpected").touch()')
        self.assertEqual(c.verify(self.root, 'release', expected_commit='f' * 40), 2)
        self.assertEqual(self.report()['checks'], [])
        self.assertEqual(self.report()['not_run'], ['unit'])
        self.assertIn('Expected commit', self.report()['error'])
        self.assertFalse((self.root / 'unexpected').exists())

    def test_release_accepts_the_requested_full_commit(self):
        self.prepare_release()
        commit = self.git_head()
        self.assertEqual(c.verify(self.root, 'release', expected_commit=commit), 0)
        self.assertEqual(self.report()['expected_commit'], commit)
        self.assertEqual(self.report()['git']['commit'], commit)

    def git_head(self):
        return subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'],
                                       text=True).strip()

    def test_expected_commit_rejects_short_or_symbolic_refs_and_wrong_stage(self):
        self.prepare_release()
        for ref in ('main', self.git_head()[:12], ''):
            with self.subTest(ref=ref):
                self.assertEqual(c.verify(self.root, 'release', expected_commit=ref), 2)
                self.assertEqual(self.report()['checks'], [])
        self.assertEqual(c.verify(self.root, 'dev', expected_commit=self.git_head()), 2)

    def test_release_detects_mutation_by_check(self):
        self.prepare_release('from pathlib import Path; Path("changed.txt").write_text("changed")')
        self.assertNotEqual(self.run_check('release'), 0)
        self.assertEqual(self.report()['status'], 'ERROR')


if __name__ == '__main__':
    unittest.main()
