<#
.SYNOPSIS
    OverhaulMyAgent - Qoder harness installer (Windows PowerShell).

.DESCRIPTION
    Installs this repository as a user-scope Qoder local plugin under
    $env:USERPROFILE\.qoder\plugins\cache\local\overhaul-my-agent\<version>\,
    registers it in installed_plugins_v2.json and enables it in settings.json.
    Both files are merged (never blind-overwritten) and a timestamped .bak is
    kept. settings.json is always written as UTF-8 WITHOUT a BOM - Qoder's
    strict MCP reader rejects BOM-prefixed files with SETTINGS_JSON_INVALID,
    silently disabling every user MCP server.

.PARAMETER QoderHome
    Qoder config root. Defaults to $env:USERPROFILE\.qoder

.PARAMETER DryRun
    Print the plan without writing anything.

.EXAMPLE
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\install\install_qoder.ps1
#>
[CmdletBinding()]
param(
    [string] $QoderHome = $(if ($env:QODER_HOME) { $env:QODER_HOME } else { Join-Path $env:USERPROFILE ".qoder" }),
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSScriptRoot
$Manifest  = Join-Path $ScriptDir ".qoder-plugin\plugin.json"

if (-not (Test-Path $Manifest)) {
    Write-Error "Missing $Manifest - run this from a repository checkout."
    exit 1
}

$ManifestData  = Get-Content $Manifest -Raw | ConvertFrom-Json
$PluginName    = $ManifestData.name
$PluginVersion = $ManifestData.version
$Dest          = Join-Path $QoderHome "plugins\cache\local\$PluginName\$PluginVersion"

Write-Host "================================================================" -ForegroundColor Blue
Write-Host "   OverhaulMyAgent - Qoder Harness Installer                    " -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "[*] Repository : $ScriptDir"     -ForegroundColor Yellow
Write-Host "[*] Qoder home : $QoderHome"     -ForegroundColor Yellow
Write-Host "[*] Plugin     : $PluginName@local v$PluginVersion" -ForegroundColor Yellow
Write-Host "[*] Target     : $Dest"          -ForegroundColor Yellow
if ($DryRun) { Write-Host "[*] DRY-RUN - nothing will be written." -ForegroundColor Yellow }

if (-not (Test-Path $QoderHome)) {
    Write-Error "$QoderHome not found. Install and start Qoder once, then re-run."
    exit 1
}

# --- 1. Payload -------------------------------------------------------------
$PayloadItems = @("skills", "knowledge", "tools", "core", "references", "QODER.md", "AGENTS.md", "README.md", "LICENSE")

Write-Host "`n[*] Payload to install:" -ForegroundColor Blue
foreach ($Item in $PayloadItems) {
    if (Test-Path (Join-Path $ScriptDir $Item)) { Write-Host "      + $Item" }
}
Write-Host "      + .qoder-plugin\plugin.json"

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    foreach ($Item in $PayloadItems) {
        $Src = Join-Path $ScriptDir $Item
        if (-not (Test-Path $Src)) { continue }
        $Target = Join-Path $Dest $Item
        if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
        Copy-Item -Recurse -Force $Src $Target
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $Dest ".qoder-plugin") | Out-Null
    Copy-Item -Force $Manifest (Join-Path $Dest ".qoder-plugin\plugin.json")
    if (Test-Path (Join-Path $ScriptDir "core")) {
        $Refs = Join-Path $Dest "references"
        New-Item -ItemType Directory -Force -Path $Refs | Out-Null
        Copy-Item -Force (Join-Path $ScriptDir "core\*") $Refs -Recurse
    }
    Write-Host "  [OK] Plugin payload installed." -ForegroundColor Green
}

# --- 2. Registry + settings merge (UTF-8, no BOM) ---------------------------
function Read-JsonNoBom {
    param([string] $Path, [object] $Default)
    if (-not (Test-Path $Path)) { return $Default }
    $Bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) {
        $Bytes = $Bytes[3..($Bytes.Length - 1)]
    }
    $Text = [System.Text.Encoding]::UTF8.GetString($Bytes)
    try { return ($Text | ConvertFrom-Json) }
    catch { Write-Error "Refusing to merge into unparseable ${Path}: $_"; exit 1 }
}

function Write-JsonNoBom {
    param([string] $Path, [object] $Data)
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    if (Test-Path $Path) {
        Copy-Item -Force $Path "$Path.bak_qoder_install_$Stamp"
    }
    $Dir = Split-Path -Parent $Path
    if ($Dir -and -not (Test-Path $Dir)) { New-Item -ItemType Directory -Force -Path $Dir | Out-Null }
    $Json = ($Data | ConvertTo-Json -Depth 32)
    $Enc  = New-Object System.Text.UTF8Encoding($false)   # false = no BOM
    [System.IO.File]::WriteAllText($Path, $Json + "`n", $Enc)
}

if (-not $DryRun) {
    $Key     = "$PluginName@local"
    $Now     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    $RegPath = Join-Path $QoderHome "plugins\installed_plugins_v2.json"

    $Registry = Read-JsonNoBom -Path $RegPath -Default ([pscustomobject]@{ version = 2; plugins = [pscustomobject]@{} })
    if (-not $Registry.plugins) { $Registry | Add-Member -NotePropertyName plugins -NotePropertyValue ([pscustomobject]@{}) -Force }

    $InstalledAt = $Now
    $Existing = $Registry.plugins.$Key
    if ($Existing -and $Existing[0].installedAt) { $InstalledAt = $Existing[0].installedAt }

    $Entry = [pscustomobject]@{
        scope       = "user"
        installPath = ($Dest -replace '\\', '\')
        version     = $PluginVersion
        installedAt = $InstalledAt
        lastUpdated = $Now
        displayName = "OverhaulMyAgent"
    }
    if ($Registry.plugins.PSObject.Properties.Name -contains $Key) {
        $Registry.plugins.$Key = @($Entry)
    } else {
        $Registry.plugins | Add-Member -NotePropertyName $Key -NotePropertyValue @($Entry) -Force
    }
    Write-JsonNoBom -Path $RegPath -Data $Registry
    Write-Host "  [OK] registered $Key in installed_plugins_v2.json" -ForegroundColor Green

    $SetPath  = Join-Path $QoderHome "settings.json"
    $Settings = Read-JsonNoBom -Path $SetPath -Default ([pscustomobject]@{})
    if (-not ($Settings.PSObject.Properties.Name -contains "enabledPlugins")) {
        $Settings | Add-Member -NotePropertyName enabledPlugins -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    if ($Settings.enabledPlugins.PSObject.Properties.Name -contains $Key) {
        $Settings.enabledPlugins.$Key = $true
    } else {
        $Settings.enabledPlugins | Add-Member -NotePropertyName $Key -NotePropertyValue $true -Force
    }
    Write-JsonNoBom -Path $SetPath -Data $Settings
    Write-Host "  [OK] enabled $Key in settings.json" -ForegroundColor Green
    Write-Host "  [OK] Backups kept as .bak_qoder_install_*" -ForegroundColor Green
}

# --- 3. MCP guidance (never auto-merged: templates hold placeholders) -------
Write-Host "`n[*] MCP servers are NOT auto-installed." -ForegroundColor Blue
Write-Host "    Review mcp\qoder_settings.template.json, fill in your own tokens, then"
Write-Host "    merge the servers you want into $QoderHome\settings.json under `"mcpServers`"."
Write-Host "    Remember: Qoder does not support the `"disabledTools`" key - drop it."

Write-Host "`n[OK] OVERHAUL MY AGENT INSTALLED FOR QODER!" -ForegroundColor Green
Write-Host "[!] Restart Qoder so the plugin and its skills load." -ForegroundColor Yellow
Write-Host "    Verify: the skill listing should show ${PluginName}:plan-first and friends."
