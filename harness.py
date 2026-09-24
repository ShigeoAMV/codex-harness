#!/usr/bin/env python3
"""Portable Codex instructions. Python 3.11+, standard library only."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import uuid

ROOT = Path(__file__).resolve().parent
START = b'<!-- codex-harness:start -->'
END = b'<!-- codex-harness:end -->'


class HarnessError(Exception):
    pass


def checked(path):
    """Do not follow a linked managed file or directory, including Windows junctions."""
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 0x400):
            raise HarnessError(f'Refusing linked path: {part}')
    return path


def read(path):
    checked(path)
    return path.read_bytes() if path.exists() else None


def atomic_write(path, value):
    checked(path)
    if value is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.harness-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(name, path.stat().st_mode & 0o777)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(value).hexdigest() if value is not None else None


def encode(value):
    return base64.b64encode(value).decode('ascii') if value is not None else None


def decode(value):
    return base64.b64decode(value, validate=True) if value is not None else None


def split_block(data):
    data = data or b''
    if START not in data and END not in data:
        return data, None, b''
    if data.count(START) != 1 or data.count(END) != 1 or data.index(START) > data.index(END):
        raise HarnessError('Malformed or duplicate harness markers in AGENTS.md')
    first, last = data.index(START), data.index(END) + len(END)
    return data[:first], data[first:last], data[last:]


def load_state(home):
    raw = read(home / 'harness/state.json')
    state = json.loads(raw) if raw else None
    if state and state.get('schema') != 1:
        raise HarnessError('Unsupported installation state schema')
    return state


@contextmanager
def locked(home):
    folder = checked(home / 'harness')
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / 'install.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise HarnessError(f'Another operation or interrupted run owns {lock}; inspect before removing it') from exc
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def assert_owned(home, state):
    _, block, _ = split_block(read(home / 'AGENTS.md'))
    if digest(block) != state['rules_hash']:
        raise HarnessError('Managed AGENTS.md block modified or missing; preserve your edits before updating')
    if digest(read(home / 'harness/WORKFLOWS.md')) != state['workflow_hash']:
        raise HarnessError('Managed WORKFLOWS.md modified or missing; preserve your edits before updating')


def transact(changes):
    before = {path: read(path) for path in changes}
    try:
        for path, value in changes.items():
            atomic_write(path, value)
    except (Exception, KeyboardInterrupt):
        for path, value in before.items():
            atomic_write(path, value)
        raise


def install(home, bundle):
    with locked(home):
        state = load_state(home)
        agents = read(home / 'AGENTS.md')
        prefix, old_block, suffix = split_block(agents)
        workflow = read(home / 'harness/WORKFLOWS.md')
        if state:
            assert_owned(home, state)
        elif old_block is not None or workflow is not None:
            raise HarnessError('Found unmanaged harness content; refusing to take ownership')
        new_block = START + b'\n' + bundle['rules'].strip().encode('utf-8') + b'\n' + END
        new_workflow = bundle['workflow'].encode('utf-8')
        if state and (state['commit'], state['version'], state['rules_hash'], state['workflow_hash']) == (
                bundle['commit'], bundle['version'], digest(new_block), digest(new_workflow)):
            return 'unchanged'
        separator = b'\n\n' if old_block is None and prefix else b''
        new_agents = prefix + separator + new_block + (suffix if old_block else b'\n')
        backup_id = uuid.uuid4().hex
        backup = {'agents': encode(agents), 'workflow': encode(workflow), 'state': state,
                  'separator': encode(separator), 'installed_agents_hash': digest(new_agents)}
        backup_path = home / 'harness/backups' / (backup_id + '.json')
        atomic_write(backup_path, json_bytes(backup))
        new_state = {'schema': 1, 'version': bundle['version'], 'commit': bundle['commit'],
                     'rules_hash': digest(new_block), 'workflow_hash': digest(new_workflow),
                     'backup': backup_id}
        transact({home / 'AGENTS.md': new_agents, home / 'harness/WORKFLOWS.md': new_workflow,
                  home / 'harness/state.json': json_bytes(new_state)})
        return 'installed'


def rollback(home):
    with locked(home):
        state = load_state(home)
        if not state:
            raise HarnessError('No managed installation to roll back')
        assert_owned(home, state)
        if not re.fullmatch('[0-9a-f]{32}', state['backup']):
            raise HarnessError('Invalid backup identifier')
        backup = json.loads(read(home / 'harness/backups' / (state['backup'] + '.json')))
        agents = read(home / 'AGENTS.md')
        if digest(agents) == backup['installed_agents_hash']:
            restored_agents = decode(backup['agents'])
        else:
            prefix, _, suffix = split_block(agents)
            _, old_block, _ = split_block(decode(backup['agents']))
            separator = decode(backup['separator'])
            if old_block is None and separator and prefix.endswith(separator):
                prefix = prefix[:-len(separator)]
            restored_agents = prefix + (old_block or b'') + suffix
        transact({home / 'AGENTS.md': restored_agents,
                  home / 'harness/WORKFLOWS.md': decode(backup['workflow']),
                  home / 'harness/state.json': json_bytes(backup['state']) if backup['state'] else None})
        return 'rolled back'


def status(home):
    state = load_state(home)
    issues = []
    if state:
        try:
            assert_owned(home, state)
        except HarnessError as exc:
            issues.append(str(exc))
    else:
        issues.append('Harness not installed')
    override = read(home / 'AGENTS.override.md')
    if override and override.strip():
        issues.append('AGENTS.override.md takes precedence over the shared AGENTS.md')
    return {'installed': state is not None, 'version': state['version'] if state else None,
            'commit': state['commit'] if state else None, 'aligned': not issues, 'issues': issues}


def git(*args):
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, timeout=30)
    if result.returncode:
        raise HarnessError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout.decode('utf-8').strip()


def bundle_from_checkout(ref=None):
    commit = git('rev-parse', 'HEAD')
    if ref is not None and (not re.fullmatch('[0-9a-f]{40}', ref) or ref != commit):
        raise HarnessError('--ref must be the full 40-character SHA of the checked-out commit')
    if git('status', '--porcelain', '--untracked-files=normal'):
        raise HarnessError('Use a clean checkout; commit or preserve local changes first')
    manifest = json.loads((ROOT / 'harness.json').read_text(encoding='utf-8'))
    if manifest['schema'] != 1:
        raise HarnessError('Unsupported bundle schema')
    return {'version': manifest['version'], 'commit': commit,
            'rules': (ROOT / 'payload/AGENTS.md').read_text(encoding='utf-8'),
            'workflow': (ROOT / 'payload/WORKFLOWS.md').read_text(encoding='utf-8')}


def plugin_status(home):
    """Report only relevant plugin metadata, never config values or credentials."""
    manifest = json.loads((ROOT / 'harness.json').read_text(encoding='utf-8'))
    expected = manifest['superpowers']['version']
    result = {'expected_superpowers': expected, 'issues': [], 'superpowers': []}
    active = []
    try:
        env = dict(os.environ, CODEX_HOME=str(home))
        run = subprocess.run(['codex', 'plugin', 'list', '--json'], capture_output=True,
                             text=True, encoding='utf-8', env=env, timeout=20)
        if run.returncode:
            raise HarnessError('Codex plugin inventory unavailable')
        plugins = json.loads(run.stdout)['installed']
        active = [p for p in plugins if p['name'] == 'superpowers' and p.get('enabled')]
        result['superpowers'] = [{k: p.get(k) for k in ('pluginId', 'version')} for p in active]
        if (len(active) != 1 or active[0].get('version') != expected
                or active[0].get('pluginId') not in manifest['superpowers']['accepted_plugins']):
            result['issues'].append('Expected exactly one enabled Superpowers ' + expected
                                    + ' from an accepted source; reuse a matching existing installation')
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, HarnessError):
        result['issues'].append('Cannot verify Superpowers; check Codex plugin settings manually')
    config = read(home / 'config.toml')
    parsed = {}
    if config:
        parsed = tomllib.loads(config.decode('utf-8-sig'))
        if any(key.startswith('qodo@') and value.get('enabled', True)
               for key, value in parsed.get('plugins', {}).items()):
            result['qodo'] = 'present; not required or invoked by this harness'
    marketplace = parsed.get('marketplaces', {}).get('superpowers-dev', {})
    upstream = manifest['superpowers']['repository']
    uses_dev = any(p.get('pluginId') == manifest['superpowers']['plugin'] for p in active)
    if uses_dev and (marketplace.get('ref') != manifest['superpowers']['commit']
            or marketplace.get('source_type') != 'git'
            or marketplace.get('source') not in (upstream, upstream + '.git')):
        result['issues'].append('Superpowers marketplace source/ref differs from harness.json pin')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['install', 'status', 'update', 'rollback', 'verify'])
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')))
    parser.add_argument('--ref', help='Required for update: full checked-out Git commit SHA')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--stage', choices=['dev', 'security', 'release'], default='dev')
    args = parser.parse_args()
    try:
        home = args.codex_home.absolute()
        if args.command in ('install', 'update'):
            if args.command == 'update' and not args.ref:
                raise HarnessError('update requires --ref with an explicit commit SHA')
            print(install(home, bundle_from_checkout(args.ref)))
        elif args.command == 'rollback':
            print(rollback(home))
        elif args.command == 'status':
            report = status(home)
            report['plugins'] = plugin_status(home)
            report['issues'].extend(report['plugins']['issues'])
            if report['installed'] and report['commit'] != git('rev-parse', 'HEAD'):
                report['issues'].append('Installed revision differs from this checkout')
            report['aligned'] = not report['issues']
            print(json.dumps(report, indent=2))
            return 0 if report['aligned'] else 1
        else:
            from checks import verify
            return verify(args.project, args.stage)
        return 0
    except (HarnessError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
