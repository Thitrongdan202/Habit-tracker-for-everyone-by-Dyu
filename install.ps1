# Habit Tracker Collection v2.1 Installer (PowerShell 5.1+ / 7+)
<#
.SYNOPSIS
    Habit Tracker Collection v2.1 - Interactive Zero-Install Downloader (Windows PowerShell)
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
    @{ Id = 1;  Stem = "01_Sunflower_Garden_Blush";          Title = "Vuon Huong Duong Pastel (Sunflower Garden)" }
    @{ Id = 2;  Stem = "02_Cactus_Bloom_Pastel_Weeks";       Title = "Xuong Rong No Hoa - 5 Tuan Pastel" }
    @{ Id = 3;  Stem = "03_Rainbow_Executive_Donuts";        Title = "Cau Vong Dashboard & 5 Bieu Do Tron" }
    @{ Id = 4;  Stem = "04_Sage_Botanical_Habit_And_Budget"; Title = "La Xanh Thoi Quen & Song Xanh" }
    @{ Id = 5;  Stem = "05_Lavender_Dream_Wellness_Mood";    Title = "Oai Huong Cham Soc Giac Ngu & Tam Trang" }
    @{ Id = 6;  Stem = "06_Midnight_Navy_Blush_Focus";       Title = "Navy Tap Trung Deep Work & Diem XP" }
    @{ Id = 7;  Stem = "07_Sakura_Zen_Study_Planner";        Title = "Hoa Anh Dao Hoc Tap & Gio Focus" }
    @{ Id = 8;  Stem = "08_Ocean_Coral_Fitness_Energy";      Title = "San Ho Dai Duong Tap Luyen & Nang Luong" }
    @{ Id = 9;  Stem = "09_Matcha_Cafe_Daily_Routine";       Title = "Matcha Cafe Lich Trinh Sang / Toi" }
    @{ Id = 10; Stem = "10_Aurora_Glow_RPG_Quest_Tracker";   Title = "Cuc Quang RPG Thang Cap Thoi Quen" }
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

function Test-ValidExcelZip([string]$Path) {
    if (-not (Test-Path $Path)) { return $false }
    $fi = Get-Item $Path
    if ($fi.Length -lt 10240) { return $false }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    return ($bytes.Length -ge 2 -and $bytes[0] -eq 0x50 -and $bytes[1] -eq 0x4B)
}

function Download-Asset([string]$RelUrl, [string]$DestPath, [bool]$CheckZip = $true) {
    $url = "$REPO_RAW/$RelUrl"
    $parent = Split-Path -Parent $DestPath
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    try {
        Invoke-WebRequest -Uri $url -OutFile $DestPath -UseBasicParsing
        if ($CheckZip -and -not (Test-ValidExcelZip $DestPath)) {
            Remove-Item -Force -ErrorAction SilentlyContinue $DestPath
            Write-Host "  [LOI] File khong hop le: $(Split-Path -Leaf $DestPath)" -ForegroundColor Red
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

function Parse-TemplateIds([string]$Raw) {
    $selectedIds = New-Object System.Collections.Generic.List[int]
    $quit = $false
    $all = $false
    $tokens = $Raw.Trim() -split '[,\s]+' | Where-Object { $_ -ne "" }
    foreach ($tok in $tokens) {
        $u = $tok.ToUpperInvariant()
        if ($u -eq "0" -or $u -eq "Q" -or $u -eq "EXIT") { $quit = $true; break }
        elseif ($u -eq "A" -or $u -eq "ALL") { $all = $true }
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
    if ($all) {
        $selectedIds.Clear()
        1..10 | ForEach-Object { $selectedIds.Add($_) }
    }
    return @{ Ids = @($selectedIds); Quit = $quit }
}

$OutDir = Resolve-TargetFolder
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "   HABIT TRACKER COLLECTION v2.1 - BY DYU (UNIFIED 4-TAB EDITION)"       -ForegroundColor Yellow
Write-Host "   Hoat anh dong 6 giai doan | Luu data da thang/nam | Thanh Tuu Nam"   -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "  Thu muc luu file: $OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "  BUOC 1 - CHON PHIEN BAN PHU HOP:" -ForegroundColor White
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  [1] Ban PRO INTERACTIVE (.xlsm)  [KHUYEN DUNG CHO EXCEL DESKTOP]" -ForegroundColor Green
Write-Host "      -> Gon 4 tab, doi Thang/Nam tu luu & tai du lieu sieu muot vao _Database!" -ForegroundColor DarkGray
Write-Host "  [2] Ban EXCEL OFFLINE KHONG MACRO (.xlsx)" -ForegroundColor Cyan
Write-Host "      -> Gon 4 tab sieu nhe, chay moi Excel 2016-365 Win/Mac, 0 canh bao bao mat!" -ForegroundColor DarkGray
Write-Host "  [3] Ban GOOGLE SHEETS (.xlsx + tu dong tai google_sheets_1click_setup.gs)" -ForegroundColor Cyan
Write-Host "      -> Gon 4 tab + Script 1-Click bat Checkbox & tu luu 12 thang tren Cloud!" -ForegroundColor DarkGray
Write-Host "  [0] Thoat" -ForegroundColor DarkGray
Write-Host ""

if ($env:HABIT_EDITION) {
    $edChoice = $env:HABIT_EDITION.Trim()
    Write-Host "  > Chon phien ban (auto): $edChoice" -ForegroundColor DarkYellow
} else {
    $edChoice = (Read-Host "  > Nhap phien ban (1, 2, 3 - mac dinh [1])").Trim()
    if ($edChoice -eq "") { $edChoice = "1" }
}

if ($edChoice -eq "0" -or $edChoice -match '^[Qq]') {
    Write-Host "  Tam biet! Chuc ban xay dung thoi quen thanh cong!" -ForegroundColor Cyan
    return
}
if ($edChoice -notin @("1", "2", "3")) { $edChoice = "1" }

Write-Host ""
Write-Host "  BUOC 2 - CHON MAU THOI QUEN (10 CHU DE THAM MY):" -ForegroundColor White
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
foreach ($t in $Templates) {
    $num = ("[{0}]" -f $t.Id).PadRight(5)
    Write-Host ("  {0} {1,-38} - {2}" -f $num, $t.Stem, $t.Title) -ForegroundColor White
}
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  [A]   Tai TOAN BO 10 mau (Download All)" -ForegroundColor Green
Write-Host "  [0]   Thoat" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Goi y: Nhap 1 so (vd: 1), nhieu so (vd: 1,3,7), dai (vd: 1-5), hoac A" -ForegroundColor Yellow

if ($env:HABIT_CHOICE) {
    $choice = $env:HABIT_CHOICE
    Write-Host "  > Chon mau (auto): $choice" -ForegroundColor DarkYellow
} else {
    $choice = Read-Host "  > Nhap lua chon cua ban"
}

$parsed = Parse-TemplateIds $choice
if ($parsed.Quit -or $parsed.Ids.Count -eq 0) {
    Write-Host "  Khong co mau nao duoc chon. Tam biet!" -ForegroundColor Cyan
    return
}

$queue = New-Object System.Collections.Generic.List[hashtable]
if ($edChoice -eq "1") {
    $subDir = Join-Path $OutDir "pro_macro"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem)_Pro.xlsm"
        $queue.Add(@{ Rel = "templates/pro_macro/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $hint = "Mo file .xlsm -> bam 'Enable Content' 1 lan -> doi Thang/Nam sieu muot!"
} elseif ($edChoice -eq "2") {
    $subDir = Join-Path $OutDir "excel_universal_offline"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem).xlsx"
        $queue.Add(@{ Rel = "templates/excel_universal_offline/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $hint = "Nhan dup file .xlsx -> dung ngay 100% Offline, khong Macro, khong canh bao!"
} else {
    $subDir = Join-Path $OutDir "google_sheets_edition"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem).xlsx"
        $queue.Add(@{ Rel = "templates/google_sheets_edition/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $queue.Add(@{ Rel = "scripts/google_sheets_1click_setup.gs"; Dest = (Join-Path $subDir "google_sheets_1click_setup.gs"); CheckZip = $false })
    $queue.Add(@{ Rel = "docs/GOOGLE_SHEETS_GUIDE.md"; Dest = (Join-Path $subDir "GOOGLE_SHEETS_GUIDE.md"); CheckZip = $false })
    $hint = "Tai file len Google Sheets -> dan google_sheets_1click_setup.gs vao Apps Script -> Run setupHabitTracker()!"
}

Write-Host ""
Write-Host "  Dang tai $($queue.Count) tep ve: $subDir ..." -ForegroundColor Cyan
$okCount = 0
$idx = 0
foreach ($item in $queue) {
    $idx++
    Write-Host ("  [{0}/{1}] " -f $idx, $queue.Count) -NoNewline -ForegroundColor DarkGray
    if (Download-Asset -RelUrl $item.Rel -DestPath $item.Dest -CheckZip $item.CheckZip) {
        $okCount++
    }
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "  HOAN TAT: Da tai thanh cong $okCount / $($queue.Count) tep!" -ForegroundColor Green
Write-Host "  Thu muc:  $subDir" -ForegroundColor White
Write-Host "  Cach dung: $hint" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Magenta

if ($env:HABIT_NO_OPEN -ne "1") {
    $openAns = Read-Host "  Mo thu muc luu file ngay bay gio? (Y/n)"
    if ($openAns -eq "" -or $openAns -match '^[Yy]') {
        Start-Process explorer.exe $subDir
    }
}
