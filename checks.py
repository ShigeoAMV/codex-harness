"""Run explicit project checks. This is NOT a tamper-resistant release authority."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from harness import HarnessError, atomic_write, digest, json_bytes, locked, read

STAGES = {'dev', 'security', 'release'}


def validate(config, stage):
    if not isinstance(config, dict) or config.get('schema') != 1:
        raise HarnessError('Expected checks schema 1')
    if config.get('profile') not in ('internal', 'public'):
        raise HarnessError('profile must be internal or public')
    checks = config.get('checks')
    if not isinstance(checks, list) or not checks:
        raise HarnessError('Configure actual project checks; an empty template cannot pass')
    seen = set()
    for check in checks:
        if not isinstance(check, dict):
            raise HarnessError('Each check must be an object')
        name = check.get('name')
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise HarnessError('Check names must be nonempty and unique')
        seen.add(name)
        stages, argv, timeout = check.get('stages'), check.get('argv'), check.get('timeout_seconds')
        if not isinstance(stages, list) or not stages or any(s not in STAGES for s in stages):
            raise HarnessError('Each check needs explicit dev/security/release stages')
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a or '\0' in a for a in argv):
            raise HarnessError('argv must be a nonempty string array, not a shell string')
        if type(timeout) is not int or not 1 <= timeout <= 86400:
            raise HarnessError('timeout_seconds must be an integer from 1 to 86400')
    selected = [check for check in checks if stage in check['stages']]
    if not selected:
        raise HarnessError(f'No required checks configured for {stage}')
    return selected


def git_identity(project):
    def run(*args):
        proc = subprocess.run(['git', '-C', str(project), *args], capture_output=True,
                              text=True, encoding='utf-8', timeout=15)
        return proc.stdout.strip() if proc.returncode == 0 else None
    try:
        commit = run('rev-parse', 'HEAD')
        dirty = run('status', '--porcelain', '--untracked-files=normal')
        return {'commit': commit, 'dirty': bool(dirty) if dirty is not None else None}
    except (OSError, subprocess.TimeoutExpired):
        return {'commit': None, 'dirty': None}


def run_check(check, project):
    start = time.monotonic()
    result = {'name': check['name'], 'status': 'ERROR', 'exit_code': None}
    print('RUN ' + check['name'], flush=True)
    try:
        argv = [sys.executable if value == '{python}' else value for value in check['argv']]
        with subprocess.Popen(argv, cwd=project, start_new_session=(os.name != 'nt')) as proc:
            try:
                result['exit_code'] = proc.wait(timeout=check['timeout_seconds'])
                result['status'] = 'PASS' if proc.returncode == 0 else 'FAIL'
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                try:
                    if os.name == 'nt':
                        killer = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/taskkill.exe'
                        killed = subprocess.run([str(killer), '/PID', str(proc.pid), '/T', '/F'],
                                                capture_output=True, timeout=15)
                        if killed.returncode:
                            result['cleanup_warning'] = 'Process-tree termination failed; check for remaining children'
                    else:
                        os.killpg(proc.pid, signal.SIGKILL)
                except (OSError, subprocess.TimeoutExpired):
                    result['cleanup_warning'] = 'Process-tree termination failed; check for remaining children'
                finally:
                    proc.kill()
                    proc.wait(timeout=10)
                result['error'] = 'Check timed out or was interrupted'
    except OSError as exc:
        result['error'] = str(exc)
    result['seconds'] = round(time.monotonic() - start, 3)
    return result


def verify(project, stage):
    project = project.absolute()
    evidence = project / '.harness-evidence'
    report = {'schema': 1, 'stage': stage, 'status': 'ERROR', 'checks': [],
              'started_at': datetime.now(timezone.utc).isoformat(),
              'authority': 'development evidence only; not a release approval'}
    # Single writer: another run must not replace this run's report.
    with locked(evidence):
        report_path = evidence / 'result.json'
        atomic_write(report_path, json_bytes(report))  # invalidate any stale PASS first
        try:
            if stage not in STAGES:
                raise HarnessError('Unknown stage')
            raw = read(project / 'harness.checks.json')
            if raw is None:
                raise HarnessError('Missing harness.checks.json')
            report['config_sha256'] = digest(raw)
            config = json.loads(raw)
            selected = validate(config, stage)
            report['profile'] = config['profile']
            report['git'] = git_identity(project)
            if stage == 'release' and (not report['git']['commit'] or report['git']['dirty'] is not False):
                raise HarnessError('Release checks require a clean Git commit; ignore .harness-evidence/')
            for check in selected:
                result = run_check(check, project)
                report['checks'].append(result)
                if result['status'] != 'PASS':
                    report['status'] = result['status']
                    break
            else:
                if stage == 'release' and git_identity(project) != report['git']:
                    raise HarnessError('Checkout changed during release verification')
                if read(project / 'harness.checks.json') != raw:
                    raise HarnessError('Check configuration changed during verification')
                report['status'] = 'PASS'
            executed = {item['name'] for item in report['checks']}
            report['not_run'] = [item['name'] for item in selected if item['name'] not in executed]
        except (HarnessError, OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
            report['status'] = 'ERROR'
            report['error'] = str(exc)
        finally:
            atomic_write(report_path, json_bytes(report))
    print(report['status'] + ': ' + str(report_path), flush=True)
    if report.get('error'):
        print(report['error'], flush=True)
    return {'PASS': 0, 'FAIL': 1, 'ERROR': 2}[report['status']]
