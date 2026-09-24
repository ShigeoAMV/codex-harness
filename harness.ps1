$ErrorActionPreference = 'Stop'
if ($env:HARNESS_PYTHON) {
    & $env:HARNESS_PYTHON "$PSScriptRoot/harness.py" @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python "$PSScriptRoot/harness.py" @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$PSScriptRoot/harness.py" @args
} else {
    throw 'Python 3.11+ required. Set HARNESS_PYTHON to its executable path.'
}
exit $LASTEXITCODE
