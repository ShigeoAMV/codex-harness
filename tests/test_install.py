import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('harness', ROOT / 'harness.py')
h = importlib.util.module_from_spec(spec)
if spec.loader and (ROOT / 'harness.py').exists():
    spec.loader.exec_module(h)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='harness test spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / '.codex'
        self.home.mkdir()
        self.agents = self.home / 'AGENTS.md'
        self.agents.write_bytes(b'# My rules\r\nKeep company policy.\r\n')
        self.bundle = {'version': '0.1.0', 'commit': 'a' * 40,
                       'rules': 'Work efficiently.\n', 'workflow': '# Workflows\n'}

    def apply(self, bundle=None):
        self.assertTrue(hasattr(h, 'install'), 'installer not implemented')
        return h.install(self.home, bundle or self.bundle)

    def test_install_preserves_original_bytes_and_is_idempotent(self):
        original = self.agents.read_bytes()
        self.apply()
        content = self.agents.read_bytes()
        self.assertTrue(content.startswith(original))
        self.assertEqual(content.count(b'<!-- codex-harness:start -->'), 1)
        self.assertEqual(self.apply(), 'unchanged')
        self.assertEqual(self.agents.read_bytes(), content)
        self.assertEqual(len(list((self.home / 'harness/backups').glob('*.json'))), 1)

    def test_rollback_restores_exact_original(self):
        original = self.agents.read_bytes()
        self.apply()
        h.rollback(self.home)
        self.assertEqual(self.agents.read_bytes(), original)
        self.assertFalse((self.home / 'harness/WORKFLOWS.md').exists())
        self.assertFalse((self.home / 'harness/state.json').exists())

    def test_update_then_rollback_returns_previous_version(self):
        self.apply()
        second = dict(self.bundle, version='0.2.0', commit='b' * 40, rules='New rules.\n')
        self.apply(second)
        self.assertEqual(h.status(self.home)['version'], '0.2.0')
        h.rollback(self.home)
        self.assertEqual(h.status(self.home)['version'], '0.1.0')
        h.rollback(self.home)
        self.assertEqual(self.agents.read_bytes(), b'# My rules\r\nKeep company policy.\r\n')

    def test_unmanaged_edits_survive_update_and_rollback(self):
        self.apply()
        self.agents.write_bytes(self.agents.read_bytes() + b'\nNew local policy.\n')
        self.apply(dict(self.bundle, version='0.2.0', rules='Updated.\n'))
        h.rollback(self.home)
        h.rollback(self.home)
        self.assertIn(b'New local policy.', self.agents.read_bytes())
        self.assertNotIn(b'codex-harness:start', self.agents.read_bytes())

    def test_managed_edit_refuses_update_and_rollback(self):
        self.apply()
        self.agents.write_bytes(self.agents.read_bytes().replace(b'Work efficiently.', b'My edit.'))
        before = self.agents.read_bytes()
        with self.assertRaisesRegex(h.HarnessError, 'modified'):
            self.apply(dict(self.bundle, version='0.2.0'))
        with self.assertRaisesRegex(h.HarnessError, 'modified'):
            h.rollback(self.home)
        self.assertEqual(self.agents.read_bytes(), before)
        self.assertFalse(h.status(self.home)['aligned'])

    def test_workflow_edit_detected(self):
        self.apply()
        (self.home / 'harness/WORKFLOWS.md').write_text('local edit')
        self.assertFalse(h.status(self.home)['aligned'])
        with self.assertRaises(h.HarnessError):
            self.apply()

    def test_existing_unowned_workflow_is_not_overwritten(self):
        (self.home / 'harness').mkdir()
        (self.home / 'harness/WORKFLOWS.md').write_text('mine')
        with self.assertRaisesRegex(h.HarnessError, 'unmanaged'):
            self.apply()
        self.assertNotIn(b'codex-harness:start', self.agents.read_bytes())

    def test_override_is_visible(self):
        self.apply()
        (self.home / 'AGENTS.override.md').write_text('Takes precedence')
        result = h.status(self.home)
        self.assertFalse(result['aligned'])
        self.assertIn('AGENTS.override.md', ' '.join(result['issues']))

    def test_malformed_markers_refuse_changes(self):
        self.agents.write_bytes(b'<!-- codex-harness:start -->\nOops')
        with self.assertRaises(h.HarnessError):
            self.apply()

    def test_missing_agents_removed_on_rollback(self):
        self.agents.unlink()
        self.apply()
        h.rollback(self.home)
        self.assertFalse(self.agents.exists())

    def test_failure_restores_files(self):
        original = self.agents.read_bytes()
        self.assertTrue(hasattr(h, 'atomic_write'), 'atomic writes not implemented')
        real_write = h.atomic_write
        failed = False
        def fail_once(path, value):
            nonlocal failed
            if path.name == 'WORKFLOWS.md' and not failed:
                failed = True
                raise OSError('disk failure')
            return real_write(path, value)
        with patch.object(h, 'atomic_write', side_effect=fail_once):
            with self.assertRaises(OSError):
                self.apply()
        self.assertEqual(self.agents.read_bytes(), original)
        self.assertFalse((self.home / 'harness/state.json').exists())

    def test_symlink_target_refused(self):
        target = Path(self.tmp.name) / 'outside.md'
        target.write_text('outside')
        self.agents.unlink()
        try:
            self.agents.symlink_to(target)
        except OSError:
            self.skipTest('symlinks unavailable to this Windows account')
        with self.assertRaisesRegex(h.HarnessError, 'link'):
            self.apply()
        self.assertEqual(target.read_text(), 'outside')

    def test_keyboard_interrupt_restores_files(self):
        original = self.agents.read_bytes()
        real_write = h.atomic_write
        interrupted = False
        def interrupt_once(path, value):
            nonlocal interrupted
            if path.name == 'WORKFLOWS.md' and not interrupted:
                interrupted = True
                raise KeyboardInterrupt()
            return real_write(path, value)
        with patch.object(h, 'atomic_write', side_effect=interrupt_once):
            with self.assertRaises(KeyboardInterrupt):
                self.apply()
        self.assertEqual(self.agents.read_bytes(), original)
        self.assertEqual(self.apply(), 'installed')

    def test_wrong_plugin_identity_is_not_aligned(self):
        from types import SimpleNamespace
        fake = SimpleNamespace(returncode=0, stdout=json.dumps({'installed': [
            {'name': 'superpowers', 'pluginId': 'superpowers@wrong-source',
             'version': '6.4.1', 'enabled': True}]}))
        with patch.object(h.subprocess, 'run', return_value=fake):
            self.assertTrue(h.plugin_status(self.home)['issues'])

    def test_mutable_plugin_ref_is_not_aligned(self):
        from types import SimpleNamespace
        (self.home / 'config.toml').write_text(
            '[marketplaces.superpowers-dev]\nsource_type="git"\n'
            'source="https://github.com/obra/superpowers.git"\nref="main"\n')
        fake = SimpleNamespace(returncode=0, stdout=json.dumps({'installed': [
            {'name': 'superpowers', 'pluginId': 'superpowers@superpowers-dev',
             'version': '6.4.1', 'enabled': True}]}))
        with patch.object(h.subprocess, 'run', return_value=fake):
            self.assertTrue(h.plugin_status(self.home)['issues'])


if __name__ == '__main__':
    unittest.main()
