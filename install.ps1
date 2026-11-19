# Habit Tracker Collection v2.0 Installer (PowerShell 5.1+ / 7+)
<#
.SYNOPSIS
    Habit Tracker Collection v2.0 — Interactive Zero-Install Downloader (Windows PowerShell)
.DESCRIPTION
    Run in 1 line:
        irm https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.ps1 | iex
#>
$ErrorActionPreference = "Stop"

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
} catch {}

$REPO_RAW = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main"

$Templates = @(
    @{ Id = 1;  File = "01_Sunflower_Garden_Blush.xlsx";          Title = "Vườn Hướng Dương Pastel (Sunflower Garden)" }
    @{ Id = 2;  File = "02_Cactus_Bloom_Pastel_Weeks.xlsx";       Title = "Xương Rồng Nở Hoa — 5 Tuần Pastel" }
    @{ Id = 3;  File = "03_Rainbow_Executive_Donuts.xlsx";        Title = "Cầu Vồng Dashboard & 5 Biểu Đồ Tròn" }
    @{ Id = 4;  File = "04_Sage_Botanical_Habit_And_Budget.xlsx"; Title = "Lá Xanh Thói Quen + Ngân Sách Cá Nhân" }
    @{ Id = 5;  File = "05_Lavender_Dream_Wellness_Mood.xlsx";    Title = "Oải Hương Chăm Sóc Giấc Ngủ & Tâm Trạng" }
    @{ Id = 6;  File = "06_Midnight_Navy_Blush_Focus.xlsx";       Title = "Navy Tập Trung Deep Work & Điểm XP" }
    @{ Id = 7;  File = "07_Sakura_Zen_Study_Planner.xlsx";        Title = "Hoa Anh Đào Học Tập & Giờ Focus" }
    @{ Id = 8;  File = "08_Ocean_Coral_Fitness_Energy.xlsx";      Title = "San Hô Đại Dương Tập Luyện & Năng Lượng" }
    @{ Id = 9;  File = "09_Matcha_Cafe_Daily_Routine.xlsx";       Title = "Matcha Cafe Lịch Trình Sáng / Tối" }
    @{ Id = 10; File = "10_Aurora_Glow_RPG_Quest_Tracker.xlsx";   Title = "Cực Quang RPG Thăng Cấp Thói Quen" }
)

function Resolve-TargetFolder {
    if ($env:HABIT_OUT_DIR -and $env:HABIT_OUT_DIR.Trim() -ne "") {
        return $env:HABIT_OUT_DIR.Trim()
    }
    $cwd = (Get-Location).Path
    $sysPaths = @(
        "$env:SystemRoot",
        "$env:SystemRoot\System32",
        "$env:SystemRoot\SysWOW64",
        "$env:ProgramFiles",
        "${env:ProgramFiles(x86)}"
    ) | Where-Object { $_ }
    $inSys = $false
    foreach ($sp in $sysPaths) {
        if ($cwd.TrimEnd('\') -ieq $sp.TrimEnd('\') -or $cwd.StartsWith($sp.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            $inSys = $true
            break
        }
    }
    if ($inSys) {
        $desk = [Environment]::GetFolderPath("Desktop")
        if (-not $desk) { $desk = Join-Path $HOME "Desktop" }
        return (Join-Path $desk "template")
    }
    return (Join-Path $cwd "template")
}

function Test-ValidXlsx([string]$Path) {
    if (-not (Test-Path $Path)) { return $false }
    $fi = Get-Item $Path
    if ($fi.Length -lt 10240) { return $false }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    return ($bytes.Length -ge 2 -and $bytes[0] -eq 0x50 -and $bytes[1] -eq 0x4B)
}

function Download-Asset([string]$RelUrl, [string]$DestPath, [bool]$CheckXlsx = $true) {
    $url = "$REPO_RAW/$RelUrl"
    $parent = Split-Path -Parent $DestPath
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    try {
        Invoke-WebRequest -Uri $url -OutFile $DestPath -UseBasicParsing
        if ($CheckXlsx -and -not (Test-ValidXlsx $DestPath)) {
            Remove-Item -Force -ErrorAction SilentlyContinue $DestPath
            Write-Host "  [LOI] File khong hop le (khong phai .xlsx): $(Split-Path -Leaf $DestPath)" -ForegroundColor Red
            return $false
        }
        $kb = [math]::Round((Get-Item $DestPath).Length / 1024, 1)
        Write-Host "  [OK] $(Split-Path -Leaf $DestPath)  ($kb KB)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [LOI] Khong tai duoc $RelUrl : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Parse-Selection([string]$Raw) {
    $selectedIds = New-Object System.Collections.Generic.List[int]
    $extras = @{ All = $false; Pro = $false; GSheets = $false; Quit = $false }
    $tokens = $Raw.Trim() -split '[,\s]+' | Where-Object { $_ -ne "" }
    foreach ($tok in $tokens) {
        $u = $tok.ToUpperInvariant()
        if ($u -eq "0" -or $u -eq "Q" -or $u -eq "EXIT") { $extras.Quit = $true; return @{ Ids = @(); Extras = $extras } }
        elseif ($u -eq "A" -or $u -eq "ALL") { $extras.All = $true }
        elseif ($u -eq "P" -or $u -eq "PRO") { $extras.Pro = $true }
        elseif ($u -eq "G" -or $u -eq "GSHEETS") { $extras.GSheets = $true }
        elseif ($u -match '^(\d+)-(\d+)$') {
            $a = [int]$Matches[1]; $b = [int]$Matches[2]
            if ($a -gt $b) { $tmp = $a; $a = $b; $b = $tmp }
            for ($n = $a; $n -le $b; $n++) {
                if ($n -ge 1 -and $n -le 10 -and -not $selectedIds.Contains($n)) { $selectedIds.Add($n) }
            }
        } elseif ($u -match '^\d+$') {
            $n = [int]$u
            if ($n -ge 1 -and $n -le 10 -and -not $selectedIds.Contains($n)) { $selectedIds.Add($n) }
        }
    }
    if ($extras.All) {
        $selectedIds.Clear()
        1..10 | ForEach-Object { $selectedIds.Add($_) }
    }
    return @{ Ids = @($selectedIds); Extras = $extras }
}

$OutDir = Resolve-TargetFolder
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "   HABIT TRACKER COLLECTION v2.0 — BY DYU (100% OFFLINE EXCEL .XLSX)"    -ForegroundColor Yellow
Write-Host "   Khong Python • Khong Macro • Khong Internet • Excel 2016 - 365"       -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "  Thu muc luu file: $OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "  DANH SACH 10 MAU EXCEL OFFLINE (Mở là dùng ngay trên mọi máy):" -ForegroundColor White
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
foreach ($t in $Templates) {
    $num = ("[{0}]" -f $t.Id).PadRight(5)
    Write-Host ("  {0} {1,-42} — {2}" -f $num, $t.File, $t.Title) -ForegroundColor White
}
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  [A]   Tai TOAN BO 10 mau Excel Offline (Download All)" -ForegroundColor Green
Write-Host "  [P]   Tai them ban Pro Offline Excel 365 + VBA Scripts (Optional)" -ForegroundColor Cyan
Write-Host "  [G]   Tai them ban Google Sheets Edition (Optional)" -ForegroundColor Cyan
Write-Host "  [0]   Thoat" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Goi y: Nhap 1 so (vd: 1), nhieu so (vd: 1,3,7), dai (vd: 1-5), hoac A" -ForegroundColor Yellow

if ($env:HABIT_CHOICE) {
    $choice = $env:HABIT_CHOICE
    Write-Host "  > Chon mau (auto): $choice" -ForegroundColor DarkYellow
} else {
    $choice = Read-Host "  > Nhap lua chon cua ban"
}

$parsed = Parse-Selection $choice
if ($parsed.Extras.Quit) {
    Write-Host "  Tam biet! Chuc ban xay dung thoi quen thanh cong!" -ForegroundColor Cyan
    return
}

$queue = New-Object System.Collections.Generic.List[hashtable]
foreach ($id in $parsed.Ids) {
    $t = $Templates | Where-Object { $_.Id -eq $id }
    $queue.Add(@{ Rel = "templates/$($t.File)"; Dest = (Join-Path $OutDir $t.File); CheckXlsx = $true })
}
if ($parsed.Extras.Pro) {
    $proDir = Join-Path $OutDir "pro_excel365_offline"
    $vbaDir = Join-Path $OutDir "vba_scripts"
    foreach ($t in $Templates) {
        $pf = $t.File -replace '\.xlsx$', '_Pro.xlsx'
        $queue.Add(@{ Rel = "templates/pro_macro/$pf"; Dest = (Join-Path $proDir $pf); CheckXlsx = $true })
    }
    foreach ($vf in @("HabitTrackerPro.bas", "SheetTrackerEvents.cls", "README_VBA.md")) {
        $queue.Add(@{ Rel = "vba_scripts/$vf"; Dest = (Join-Path $vbaDir $vf); CheckXlsx = $false })
    }
}
if ($parsed.Extras.GSheets) {
    $gsDir = Join-Path $OutDir "google_sheets_edition"
    foreach ($t in $Templates) {
        $queue.Add(@{ Rel = "templates/google_sheets_edition/$($t.File)"; Dest = (Join-Path $gsDir $t.File); CheckXlsx = $true })
    }
}

if ($queue.Count -eq 0) {
    Write-Host "  Khong co lua chon hop le nao duoc chon. Vui long chay lai!" -ForegroundColor Yellow
    return
}

Write-Host ""
Write-Host "  Dang tai $($queue.Count) tep ve: $OutDir ..." -ForegroundColor Cyan
$okCount = 0
$idx = 0
foreach ($item in $queue) {
    $idx++
    Write-Host ("  [{0}/{1}] " -f $idx, $queue.Count) -NoNewline -ForegroundColor DarkGray
    if (Download-Asset -RelUrl $item.Rel -DestPath $item.Dest -CheckXlsx $item.CheckXlsx) {
        $okCount++
    }
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "  HOAN TAT: Da tai thanh cong $okCount / $($queue.Count) tep!" -ForegroundColor Green
Write-Host "  Thu muc:  $OutDir" -ForegroundColor White
Write-Host "  Cach dung: Nhan dup vao file .xlsx -> xem tab 'Huong Dan' -> tick ngay!" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Magenta

if ($env:HABIT_NO_OPEN -ne "1") {
    $openAns = Read-Host "  Mo thu muc 'template' ngay bay gio? (Y/n)"
    if ($openAns -eq "" -or $openAns -match '^[Yy]') {
        Start-Process explorer.exe $OutDir
    }
}
