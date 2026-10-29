param([int]$Port = 8010)
$ErrorActionPreference = 'Stop'
$demoWorkspace = Split-Path -Parent $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$sharedPython = Join-Path $demoWorkspace 'tmp\multiagent_venv\Scripts\python.exe'
if (Test-Path -LiteralPath $projectPython) { $demoPython = $projectPython }
elseif (Test-Path -LiteralPath $sharedPython) { $demoPython = $sharedPython }
else { throw 'Create a Python 3.12 venv and install requirements.txt as described in README.md.' }
Set-Location -LiteralPath $demoWorkspace
Write-Host "Open http://127.0.0.1:$Port . Press Ctrl+C to stop."
& $demoPython -m uvicorn week10_multiagent_demo.api:app --host 127.0.0.1 --port $Port --workers 1
