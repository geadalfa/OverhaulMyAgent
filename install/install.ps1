# Windows PowerShell Installer untuk OverhaulMyAgent
param(
    [string]$TargetDir = "$HOME\.gemini"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   OverhaulMyAgent - Universal Multi-Harness Installer         " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "[*] Target Installation Directory: $TargetDir" -ForegroundColor Yellow

$TargetConfigDir = Join-Path $TargetDir "config"
$TargetKnowledgeDir = Join-Path $TargetDir "knowledge"
$TargetSkillsDir = Join-Path $TargetConfigDir "skills"
$TargetScriptsDir = Join-Path $TargetDir "scripts"
$TargetMcpDir = Join-Path $TargetDir "antigravity\mcp"

New-Item -ItemType Directory -Force -Path $TargetConfigDir | Out-Null
New-Item -ItemType Directory -Force -Path $TargetKnowledgeDir | Out-Null
New-Item -ItemType Directory -Force -Path $TargetSkillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $TargetScriptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $TargetMcpDir | Out-Null

if (Test-Path "$ScriptDir\GEMINI.md") {
    Copy-Item "$ScriptDir\GEMINI.md" "$TargetDir\GEMINI.md" -Force
    Write-Host "  [✓] GEMINI.md installed." -ForegroundColor Green
}

if (Test-Path "$ScriptDir\knowledge") {
    Copy-Item "$ScriptDir\knowledge\*" "$TargetKnowledgeDir\" -Recurse -Force
    Write-Host "  [✓] Knowledge base installed." -ForegroundColor Green
}

if (Test-Path "$ScriptDir\skills") {
    Copy-Item "$ScriptDir\skills\*" "$TargetSkillsDir\" -Recurse -Force
    Write-Host "  [✓] Skills installed." -ForegroundColor Green
}

if (Test-Path "$ScriptDir\tools") {
    Copy-Item "$ScriptDir\tools\*" "$TargetScriptsDir\" -Recurse -Force
    Write-Host "  [✓] Tools installed." -ForegroundColor Green
}

if (Test-Path "$ScriptDir\mcp\schemas") {
    Copy-Item "$ScriptDir\mcp\schemas\*" "$TargetMcpDir\" -Recurse -Force
    Write-Host "  [✓] MCP schemas installed." -ForegroundColor Green
}

Write-Host "`n[✓] OVERHAUL MY AGENT SUCCESSFULLY INSTALLED!" -ForegroundColor Green