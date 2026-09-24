import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='harness cli spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'source'
        self.repo.mkdir()
        self.home = Path(self.tmp.name) / 'codex home'
        for filename in ('harness.py', 'harness.ps1', 'harness.sh', 'harness.json'):
            shutil.copy2(ROOT / filename, self.repo / filename)
        shutil.copytree(ROOT / 'payload', self.repo / 'payload')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'v1')
        self.sha = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def cli(self, command, *args, wrapper=False):
        if wrapper:
            if os.name == 'nt':
                shell = shutil.which('pwsh') or shutil.which('powershell')
                prefix = [shell, '-NoProfile', '-File', str(self.repo / 'harness.ps1')]
            else:
                prefix = ['bash', str(self.repo / 'harness.sh')]
        else:
            prefix = [sys.executable, str(self.repo / 'harness.py')]
        env = dict(os.environ, HARNESS_PYTHON=sys.executable)
        return subprocess.run([*prefix, command, '--codex-home', str(self.home), *args],
                              capture_output=True, text=True, env=env, timeout=30)

    def test_actual_shell_install_update_and_rollback(self):
        original = b'Company rules\r\n'
        self.home.mkdir()
        (self.home / 'AGENTS.md').write_bytes(original)
        installed = self.cli('install', wrapper=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertIn('unchanged', self.cli('install', wrapper=True).stdout)
        payload = self.repo / 'payload/AGENTS.md'
        payload.write_text(payload.read_text() + '\nAdditional release rule.\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'v2')
        second_sha = self.git('rev-parse', 'HEAD').strip()
        updated = self.cli('update', '--ref', second_sha, wrapper=True)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        state = json.loads((self.home / 'harness/state.json').read_text())
        self.assertEqual(state['commit'], second_sha)
        self.assertEqual(self.cli('rollback', wrapper=True).returncode, 0)
        self.assertEqual(json.loads((self.home / 'harness/state.json').read_text())['commit'], self.sha)
        self.assertEqual(self.cli('rollback', wrapper=True).returncode, 0)
        self.assertEqual((self.home / 'AGENTS.md').read_bytes(), original)

    def test_update_requires_exact_revision(self):
        for args in ((), ('--ref', 'main'), ('--ref', 'f' * 40)):
            with self.subTest(args=args):
                result = self.cli('update', *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('ref', result.stderr)

    def test_dirty_source_refused_before_writes(self):
        with (self.repo / 'payload/AGENTS.md').open('a') as stream:
            stream.write('uncommitted edit')
        result = self.cli('install')
        self.assertEqual(result.returncode, 2)
        self.assertIn('clean checkout', result.stderr)
        self.assertFalse((self.home / 'AGENTS.md').exists())


if __name__ == '__main__':
    unittest.main()
