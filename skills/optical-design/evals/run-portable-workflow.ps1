[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutputRoot,
    [string]$SkillRoot = (Join-Path $PSScriptRoot '..')
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$skillPath = (Resolve-Path -LiteralPath $SkillRoot).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputRoot)
if (Test-Path -LiteralPath $outputPath) { throw 'OutputRoot must be a new directory.' }
$null = New-Item -ItemType Directory -Path $outputPath
$designScript = Join-Path $skillPath 'scripts/design.py'
$reviewScript = Join-Path $skillPath 'scripts/review.py'
$model = Join-Path $skillPath 'assets/portable-singlet.json'
$specification = Join-Path $skillPath 'assets/full-workflow/composite-spec.json'
$changes = Join-Path $skillPath 'assets/full-workflow/changes.json'
$perturbations = Join-Path $skillPath 'assets/full-workflow/perturbations.json'
$validation = Join-Path $skillPath 'assets/validation-spec.json'
$sourceHash = (Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash.ToLowerInvariant()
$validationHash = (Get-FileHash -LiteralPath $validation -Algorithm SHA256).Hash.ToLowerInvariant()
$calls = [System.Collections.Generic.List[object]]::new()

function Invoke-CheckedCli {
    param([string]$Name, [string[]]$CliArguments, [int]$ExpectedExit = 0)
    $stdout = Join-Path $outputPath ($Name + '.stdout.json')
    $stderr = Join-Path $outputPath ($Name + '.stderr.log')
    & uv run --python 3.11 --with optiland==0.6.2 @CliArguments 1> $stdout 2> $stderr
    $actualExit = $LASTEXITCODE
    $calls.Add([ordered]@{ name = $Name; exit_code = $actualExit; stdout = $stdout; stderr = $stderr })
    if ($actualExit -ne $ExpectedExit) {
        throw "$Name returned $actualExit; expected $ExpectedExit. Inspect $stderr and $stdout."
    }
}

function Read-Report {
    param([string]$Stage)
    return Get-Content -LiteralPath (Join-Path $outputPath "$Stage/report.json") -Raw | ConvertFrom-Json
}

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

Invoke-CheckedCli 'inspect' @($designScript, 'inspect', '--backend', 'optiland', '--model', $model,
    '--out', (Join-Path $outputPath 'inspect'), '--json')
$inspection = Read-Report 'inspect'
Assert-True ($inspection.action -eq 'inspect' -and $inspection.source_unchanged -and $inspection.baseline_restored) 'Inspection/source restoration failed.'

Invoke-CheckedCli 'edit' @($designScript, 'edit', '--backend', 'optiland', '--model', $model,
    '--spec', $specification, '--changes', $changes, '--out', (Join-Path $outputPath 'edit'), '--json')
$edited = Read-Report 'edit'
Assert-True ($edited.status -eq 'applied' -and $edited.saved_candidate_verified -and $edited.candidate.assessment.passes) 'Edited fixture did not yield a verified accepted candidate.'
$candidatePath = $edited.artifacts.candidate_model
$candidateHash = (Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
Assert-True ($candidateHash -eq $edited.artifacts.candidate_sha256) 'Saved candidate hash differs from edit receipt.'
Assert-True ($edited.candidate.objective_breakdown.aggregation -eq 'weighted_rms') 'Composite term evidence absent.'

Invoke-CheckedCli 'sensitivity' @($designScript, 'sensitivity', '--backend', 'optiland', '--model', $candidatePath,
    '--spec', $specification, '--perturbations', $perturbations, '--out', (Join-Path $outputPath 'sensitivity'), '--json')
$sensitivity = Read-Report 'sensitivity'
Assert-True ($sensitivity.status -eq 'completed' -and $sensitivity.evaluations -eq 5 -and $sensitivity.trials.Count -eq 4) 'Sensitivity did not retain exactly both sides of two parameters.'
Assert-True ($sensitivity.source.sha256 -eq $candidateHash -and $null -eq $sensitivity.candidate) 'Sensitivity model lineage or no-candidate contract failed.'
foreach ($ranking in $sensitivity.rankings) {
    foreach ($parameter in $ranking.parameters) {
        Assert-True ($parameter.metric_key -eq $ranking.metric_key -and $parameter.unit -eq $ranking.unit) 'Sensitivity mixed metric identities or units.'
    }
}

Invoke-CheckedCli 'validation-original' @($designScript, 'audit', '--backend', 'optiland', '--model', $model,
    '--spec', $validation, '--out', (Join-Path $outputPath 'validation-original'), '--json') 1
Invoke-CheckedCli 'validation-candidate' @($designScript, 'audit', '--backend', 'optiland', '--model', $candidatePath,
    '--spec', $validation, '--out', (Join-Path $outputPath 'validation-candidate'), '--json')
$checked = Read-Report 'validation-candidate'
Assert-True ($checked.source.sha256 -eq $candidateHash -and $checked.baseline.assessment.passes) 'Separate candidate audit failed or used different model bytes.'
Assert-True (((Get-FileHash -LiteralPath $validation -Algorithm SHA256).Hash.ToLowerInvariant()) -eq $validationHash) 'Frozen validation specification changed.'

Invoke-CheckedCli 'stale-edit' @($designScript, 'edit', '--backend', 'optiland', '--model', $candidatePath,
    '--spec', $specification, '--changes', $changes, '--out', (Join-Path $outputPath 'stale-edit'), '--json') 4
Assert-True (-not (Test-Path -LiteralPath (Join-Path $outputPath 'stale-edit/report.json'))) 'Stale edit wrote a successful receipt.'
Invoke-CheckedCli 'missing-changes' @($designScript, 'edit', '--backend', 'optiland', '--model', $model,
    '--spec', $specification, '--out', (Join-Path $outputPath 'missing-changes'), '--json') 2

$badSteps = Get-Content -LiteralPath $perturbations -Raw | ConvertFrom-Json
$badSteps.parameters[0].step_mm = 0
$badStepsPath = Join-Path $outputPath 'invalid-perturbations.json'
$badSteps | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $badStepsPath -Encoding utf8
Invoke-CheckedCli 'invalid-step' @($designScript, 'sensitivity', '--backend', 'optiland', '--model', $candidatePath,
    '--spec', $specification, '--perturbations', $badStepsPath, '--out', (Join-Path $outputPath 'invalid-step'), '--json') 4

$rejectSpec = Get-Content -LiteralPath $specification -Raw | ConvertFrom-Json
$rejectSpec.requirements[0].min = 500
$rejectSpec.requirements[0].max = 501
$rejectSpecPath = Join-Path $outputPath 'rejected-spec.json'
$rejectSpec | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $rejectSpecPath -Encoding utf8
Invoke-CheckedCli 'rejected-edit' @($designScript, 'edit', '--backend', 'optiland', '--model', $model,
    '--spec', $rejectSpecPath, '--changes', $changes, '--out', (Join-Path $outputPath 'rejected-edit'), '--json') 1
$rejected = Read-Report 'rejected-edit'
Assert-True ($null -eq $rejected.candidate -and -not $rejected.saved_candidate_verified) 'Rejected edit retained candidate acceptance.'

foreach ($stage in @('edit', 'sensitivity', 'validation-original', 'validation-candidate', 'rejected-edit')) {
    Invoke-CheckedCli ($stage + '-review') @($reviewScript, '--report', (Join-Path $outputPath "$stage/report.json"),
        '--out', (Join-Path $outputPath ($stage + '-review')), '--json')
}
$rejectedManifest = Get-Content -LiteralPath (Join-Path $outputPath 'rejected-edit-review.stdout.json') -Raw | ConvertFrom-Json
Assert-True (-not $rejectedManifest.accepted_candidate) 'Review promoted a rejected edit.'
Assert-True (((Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash.ToLowerInvariant()) -eq $sourceHash) 'Original source model changed.'

$summary = [ordered]@{
    schema = '1'; scenario = 'inspected-explicit-edit-and-local-sensitivity'; status = 'passed'
    source_sha256 = $sourceHash; candidate_sha256 = $candidateHash; validation_spec_sha256 = $validationHash
    edit_status = $edited.status; validation_status = $checked.status; sensitivity_evaluations = $sensitivity.evaluations
    scope = 'Portable numerical workflow assertions; no native engine, physical validation or yield claim'
    output = $outputPath; calls = $calls
}
$summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $outputPath 'workflow-summary.json') -Encoding utf8
$summary | ConvertTo-Json -Depth 20
