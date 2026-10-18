[CmdletBinding()]
param(
    [ValidateSet('source', 'checkpoint', 'artifact')]
    [string]$Category = 'source',
    [string]$Path
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$folderIds = @{
    source = '16EEN7wlyD2IL0YhfCoJdiRxlnUF36H6r'
    checkpoint = '126H_DQHB_dkC4vZHjNc-RkM48PLfz_af'
    artifact = '1f_yCFjyXoS5YP3I00rAS5GbIBZSqKv0s'
}
$tempArchive = $null

try {
    if ($Category -eq 'source') {
        $commit = (& git -C $repoRoot rev-parse --short HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $commit) { throw 'Source backup requires a committed Git revision.' }
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $fileName = "LightOCR-source-$commit-$stamp.zip"
        $tempArchive = Join-Path ([IO.Path]::GetTempPath()) $fileName
        & git -C $repoRoot archive --format=zip --output=$tempArchive HEAD
        if ($LASTEXITCODE -ne 0) { throw 'git archive failed.' }
    }
    else {
        if (-not $Path) { throw "-Path is required for category '$Category'." }
        $resolved = (Resolve-Path -LiteralPath $Path).Path
        if (-not ($resolved.StartsWith($repoRoot, [StringComparison]::OrdinalIgnoreCase))) {
            throw 'Only files inside this LightOCR project may be backed up.'
        }
        $item = Get-Item -LiteralPath $resolved
        if ($item.PSIsContainer) {
            $blocked = Get-ChildItem -LiteralPath $resolved -Force -Recurse | Where-Object {
                $_.Name -in @('.env', '.venv', 'data', 'datasets', 'dataset')
            } | Select-Object -First 1
            if ($blocked) { throw "Refusing to archive a path containing excluded content: $($blocked.FullName)" }
            $fileName = "LightOCR-$Category-$($item.Name)-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"
            $tempArchive = Join-Path ([IO.Path]::GetTempPath()) $fileName
            Compress-Archive -Path (Join-Path $resolved '*') -DestinationPath $tempArchive -CompressionLevel Optimal
        }
        else {
            if ($item.Name -match '^\.env($|\.)') { throw 'Refusing to upload environment or credential files.' }
            $fileName = $item.Name
            $tempArchive = $resolved
        }
    }

    $metadata = @{ name = $fileName; parents = @($folderIds[$Category]) } | ConvertTo-Json -Compress
    $response = & gws drive files create --json $metadata --upload $tempArchive --upload-content-type 'application/zip' --format json
    if ($LASTEXITCODE -ne 0) { throw 'Google Drive upload failed.' }
    $response | Write-Output
}
finally {
    if ($tempArchive -and $tempArchive.StartsWith([IO.Path]::GetTempPath(), [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $tempArchive)) {
        Remove-Item -LiteralPath $tempArchive -Force
    }
}
