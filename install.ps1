# Habit Tracker Collection v3.9 Installer (PowerShell 5.1+ / 7+)
<#
.SYNOPSIS
    Habit Tracker Collection v3.9 - Interactive Zero-Install Downloader (Windows PowerShell)
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
    @{ Id = 1;  Cat = "NATURE"; Stem = "01_Sunflower_Garden_Blush";           Title = "Vuon Huong Duong Pastel (Sunflower Garden)" }
    @{ Id = 2;  Cat = "NATURE"; Stem = "02_Cactus_Bloom_Pastel_Weeks";        Title = "Xuong Rong No Hoa - 5 Tuan Pastel" }
    @{ Id = 3;  Cat = "STYLE";  Stem = "03_Rainbow_Executive_Donuts";         Title = "Cau Vong Dashboard & 5 Bieu Do Tron" }
    @{ Id = 4;  Cat = "FOCUS";  Stem = "04_Sage_Botanical_Habit_And_Budget";  Title = "La Xanh Thoi Quen & Ngan Sach Ca Nhan" }
    @{ Id = 5;  Cat = "STYLE";  Stem = "05_Lavender_Dream_Wellness_Mood";     Title = "Oai Huong Cham Soc Giac Ngu & Tam Trang" }
    @{ Id = 6;  Cat = "FOCUS";  Stem = "06_Midnight_Navy_Blush_Focus";        Title = "Navy Tap Trung Deep Work & Diem XP" }
    @{ Id = 7;  Cat = "FOCUS";  Stem = "07_Sakura_Zen_Study_Planner";         Title = "Hoa Anh Dao Hoc Tap & Gio Focus" }
    @{ Id = 8;  Cat = "STYLE";  Stem = "08_Ocean_Coral_Fitness_Energy";       Title = "San Ho Dai Duong Tap Luyen & Nang Luong" }
    @{ Id = 9;  Cat = "STYLE";  Stem = "09_Matcha_Cafe_Daily_Routine";        Title = "Matcha Cafe Lich Trinh Sang / Toi" }
    @{ Id = 10; Cat = "STYLE";  Stem = "10_Aurora_Glow_RPG_Quest_Tracker";    Title = "Cuc Quang RPG Thang Cap Thoi Quen" }
    @{ Id = 11; Cat = "NATURE"; Stem = "11_Velvet_Rose_Garden";               Title = "Vuon Hong Nhung Tim Lavender (Velvet Rose)" }
    @{ Id = 12; Cat = "NATURE"; Stem = "12_Blue_Tulip_Mint_Breeze";           Title = "Tulip Xanh Lam - Dai Mau Mint Chanh" }
    @{ Id = 13; Cat = "NATURE"; Stem = "13_Buttercream_Blossom_Bars";         Title = "Kem Bo Bieu Do Cot Caramel & Hoa No" }
    @{ Id = 14; Cat = "NATURE"; Stem = "14_Emerald_Forest_Gold_Stars";        Title = "Rung Ngoc Bich & Sao Vang (Gold Stars)" }
    @{ Id = 15; Cat = "NATURE"; Stem = "15_Mocha_Rose_Terracotta_Sunflower";  Title = "Huong Duong Mocha & Hong Dat Terracotta" }
    @{ Id = 16; Cat = "STYLE";  Stem = "16_Dream_Home_Architect_Builder";     Title = "Xay Ngoi Nha Mo Uoc (6 Cap Do Kien Truc)" }
    @{ Id = 17; Cat = "NATURE"; Stem = "17_Wildflower_Bloom_Daily_Mood";      Title = "Hoa Dai 5 Canh & Tam Trang Moi Ngay" }
    @{ Id = 18; Cat = "NATURE"; Stem = "18_Plum_Oak_Master_Suite";            Title = "Cay Soi Tim Man & Bang Tuan/Thang Toan Dien" }
    @{ Id = 19; Cat = "NATURE"; Stem = "19_Meadow_Emerald_Sunflower";         Title = "Huong Duong Dong Co Xanh Ngoc Luc Bao" }
    @{ Id = 20; Cat = "FOCUS";  Stem = "20_Cream_Alpaca_Cozy_Budget";         Title = "Alpaca Kem Cozy Cafe (Khan Len, Mu Noi & Latte)" }
    @{ Id = 21; Cat = "PETS";   Stem = "21_Blush_Alpaca_Flower_Crown";        Title = "Alpaca Hong Vuon Co Tich (Gio Hoa & Vong Hoa)" }
    @{ Id = 22; Cat = "PETS";   Stem = "22_Matcha_Alpaca_Meadow";             Title = "Alpaca Matcha Picnic (Yen Theu & Mu Coi)" }
    @{ Id = 23; Cat = "PETS";   Stem = "23_Bamboo_Panda_Zen_Garden";          Title = "Gau Truc Mochi Tron Xoe (Onigiri & Khan Do)" }
    @{ Id = 24; Cat = "FOCUS";  Stem = "24_Royal_Cat_Saving_Cash";            Title = "Meo Hoang Gia Tiet Kiem & Vuong Quoc Meo" }
    @{ Id = 25; Cat = "PETS";   Stem = "25_Ginger_Kitten_Basket_Routine";     Title = "Meo Cam Gio May & Bang Xep Hang Thoi Quen" }
    @{ Id = 26; Cat = "PETS";   Stem = "26_Pastel_Purple_Royal_Cat";          Title = "Meo Anh Sao Lavender (Trang Khuyet & Mu Noi Sao)" }
    @{ Id = 27; Cat = "PETS";   Stem = "27_Hatching_Chick_Icon_Studio";       Title = "Ga Con No Trung 6 Giai Doan (Studio)" }
    @{ Id = 28; Cat = "STYLE";  Stem = "28_Cotton_Candy_Jar_Sweet";           Title = "Hu Keo Bong Gon Pastel Hong-Xanh" }
    @{ Id = 29; Cat = "NATURE"; Stem = "29_Watercolor_Rose_Bouquet";          Title = "Bo Hoa Hong Mau Nuoc & Chanh Niem" }
    @{ Id = 30; Cat = "PETS";   Stem = "30_Shiba_Inu_Happy_Bork";             Title = "Cun Shiba Inu Khan Do Karakusa & Xuong Vang" }
    @{ Id = 31; Cat = "PETS";   Stem = "31_Akita_Inu_Snow_Loyal";             Title = "Cun Akita Tuyet Trang & Chuong Shimenawa" }
    @{ Id = 32; Cat = "NATURE"; Stem = "32_Sakura_Blossom_Minimalist";        Title = "Cay Hoa Anh Dao Toi Gian (Minimalist)" }
    @{ Id = 33; Cat = "PETS";   Stem = "33_Peach_Mochi_Cat_Mood_Suite";       Title = "Meo Mochi Quyt Mikan + 6 Cam Xuc & To-Do" }
    @{ Id = 34; Cat = "PETS";   Stem = "34_Fluffy_Bunny_Sticker_Pop";         Title = "Tho Bong Sticker Pop 5 Mau Pastel" }
    @{ Id = 35; Cat = "PETS";   Stem = "35_Milk_Mocha_Bear_Sweet_Love";       Title = "Gau Milk & Mocha + 5+1 Bieu Do Donut" }
    @{ Id = 36; Cat = "DIGIMON"; Stem = "36_Digimon_Veemon_Miracle";          Title = "Digimon Veemon -> Magnamon (7 Cap Tien Hoa)" }
    @{ Id = 37; Cat = "DIGIMON"; Stem = "37_Digimon_Agumon_Courage";          Title = "Digimon Agumon -> WarGreymon (7 Cap Tien Hoa)" }
    @{ Id = 38; Cat = "DIGIMON"; Stem = "38_Digimon_Gatomon_Light";           Title = "Digimon Gatomon -> LovelyAngemon (7 Cap Tien Hoa)" }
    @{ Id = 39; Cat = "DIGIMON"; Stem = "39_Digimon_Gabumon_Friendship";      Title = "Digimon Gabumon -> MetalGarurumon (7 Cap Tien Hoa)" }
    @{ Id = 40; Cat = "DIGIMON"; Stem = "40_Digimon_Piyomon_Love";            Title = "Digimon Piyomon -> Phoenixmon (7 Cap Tien Hoa)" }
    @{ Id = 41; Cat = "DIGIMON"; Stem = "41_Digimon_Patamon_Mythical";        Title = "Digimon Patamon -> Griffomon (7 Cap Than Thoai)" }
    @{ Id = 42; Cat = "DIGIMON"; Stem = "42_Digimon_Palmon_Rose";             Title = "Digimon Palmon -> Rosemon (7 Cap Tien Hoa)" }
    @{ Id = 43; Cat = "DIGIMON"; Stem = "43_Digimon_Gomamon_Arctic";          Title = "Digimon Gomamon -> AncientMegatheriummon (8 Cap)" }
    @{ Id = 44; Cat = "DIGIMON"; Stem = "44_Digimon_Guilmon_Crimson";         Title = "Digimon Guilmon -> Gallantmon Crimson (8 Cap)" }
    @{ Id = 45; Cat = "DIGIMON"; Stem = "45_Digimon_Terriermon_Mint";         Title = "Digimon Terriermon -> MegaGargomon (7 Cap)" }
    @{ Id = 46; Cat = "DIGIMON"; Stem = "46_Digimon_Renamon_Kuzuhamon";       Title = "Digimon Renamon -> Kuzuhamon Miko (8 Cap)" }
    @{ Id = 47; Cat = "DIGIMON";  Stem = "47_Digimon_Tentomon_Electro";        Title = "Digimon Tentomon -> HerakleKabuterimon (7 Cap)" }
    @{ Id = 48; Cat = "CAPYBARA"; Stem = "48_Capybara_Avocado_Zen";            Title = "Capybara Bo Xanh Ve Tay (Nuoc & Bua Bo Zen)" }
    @{ Id = 49; Cat = "CAPYBARA"; Stem = "49_Capybara_Yuzu_Onsen_Spa";         Title = "Capybara Suoi Nong Yuzu (5 Donut & Thu Gian Toi)" }
    @{ Id = 50; Cat = "CAPYBARA"; Stem = "50_Capybara_Pip_Puddle_Besties";     Title = "Doi Ban Pip & Puddle (Hong-Tim Bestie Bond)" }
    @{ Id = 51; Cat = "CAPYBARA"; Stem = "51_Capybara_Boba_Lily_Pond";         Title = "Capybara Ho Sen Tra Sua (Dem Ly Boba Tuan)" }
    @{ Id = 52; Cat = "CAPYBARA"; Stem = "52_Capybara_Bookworm_Study";         Title = "Capy & Chaptered (Gio Hoc & Trang Sach)" }
    @{ Id = 53; Cat = "CAPYBARA"; Stem = "53_Capybara_Lofi_Picnic_Beats";      Title = "Capybara Lofi Picnic (Dem Phut Flow & Playlist)" }
    @{ Id = 54; Cat = "CAPYBARA"; Stem = "54_Capybara_Foodie_Snack_Club";      Title = "Capybara Foodie Club (6 Moc Mo Khoa Mon Ngon)" }
    @{ Id = 55; Cat = "CAPYBARA"; Stem = "55_Capybara_Dino_Hoodie_Play";       Title = "Capybara Ao Dino Xanh (Diem Vui & 5 Thanh Pastel)" }
    @{ Id = 56; Cat = "CAPYBARA"; Stem = "56_Capybara_Apple_Orchard_Sweet";    Title = "Capybara Vuon Tao Do (Dem Tao & Biet On)" }
    @{ Id = 57; Cat = "CAPYBARA"; Stem = "57_Capybara_Pink_Cloud_Chill";       Title = "Capybara May Hong Toi Gian (Minimalist Chill)" }
    @{ Id = 58; Cat = "CAPYBARA"; Stem = "58_Capybara_Fairy_Party_Wish";       Title = "Capybara Tiec Tien (5 Dieu Uoc Sao Tu Thap Sang)" }
    @{ Id = 59; Cat = "CAPYBARA"; Stem = "59_Capybara_SelfCare_GlowUp";        Title = "Capybara Self-Care GlowUp (3 The Sang-Chieu-Toi)" }
    @{ Id = 60; Cat = "CAPYBARA"; Stem = "60_Capybara_Snapshot_Traveler";      Title = "Capybara Lu Hanh (Nhat Ky Anh Polaroid & Dau Ho Chieu)" }
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
                if ($n -ge 1 -and $n -le 60 -and -not $selectedIds.Contains($n)) { $selectedIds.Add($n) }
            }
        } elseif ($u -match '^\d+$') {
            $n = [int]$u
            if ($n -ge 1 -and $n -le 60 -and -not $selectedIds.Contains($n)) { $selectedIds.Add($n) }
        }
    }
    if ($all) {
        $selectedIds.Clear()
        1..60 | ForEach-Object { $selectedIds.Add($_) }
    }
    return @{ Ids = @($selectedIds); Quit = $quit }
}

$OutDir = Resolve-TargetFolder
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "   HABIT TRACKER COLLECTION v3.9 - BY DYU (60 THEMES x 4 EDITIONS)" -ForegroundColor Yellow
Write-Host "   Turbo 6/7/8-Stage Native Sprite Engine | FX Suite | Ctrl+Z Undo" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "  Thu muc luu file: $OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "  BUOC 1 - CHON PHIEN BAN PHU HOP (THEO THU TU UU TIEN):" -ForegroundColor White
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  [1] Pro Interactive (.xlsm)  [* KHUYEN DUNG SO 1 - EXCEL 365 TURBO v3.9 *]" -ForegroundColor Green
Write-Host "      -> Sieu toc ~25-54ms + Full FX Nay/Phao hoa/Toast + Ctrl+Z / Nut Undo" -ForegroundColor DarkGray
Write-Host "         + Khoa bao ve cong thuc + Tu luu Da Ngay/Thang/Nam (100% Offline)!" -ForegroundColor DarkGray
Write-Host "  [2] Excel Universal Offline (.xlsx)  [Excel 2016/2019/2021/365]" -ForegroundColor Cyan
Write-Host "      -> Khong Macro, 0 loi TRUE/FALSE tren Excel cu, du hoat anh offline!" -ForegroundColor DarkGray
Write-Host "  [3] Google Sheets Desktop (.xlsx + .gs)  [Beta - Dang thu nghiem]" -ForegroundColor Yellow
Write-Host "      -> Dung online qua Google Drive (con mot so loi nho / tre 1-2s)!" -ForegroundColor DarkGray
Write-Host "  [4] Mobile Portrait (.xlsx + .gs)  [Early Beta - Con tho so & con loi]" -ForegroundColor Magenta
Write-Host "      -> Kho doc 8 cot dang thu nghiem (chi mo bang App Google Sheets)!" -ForegroundColor DarkGray
Write-Host "  [0] Thoat" -ForegroundColor DarkGray
Write-Host ""

if ($env:HABIT_EDITION) {
    $edChoice = $env:HABIT_EDITION.Trim().ToUpperInvariant()
    Write-Host "  > Chon phien ban (auto): $edChoice" -ForegroundColor DarkYellow
} else {
    $edChoice = (Read-Host "  > Nhap phien ban (1, 2, 3, 4/M - mac dinh [1] Pro #1)").Trim().ToUpperInvariant()
    if ($edChoice -eq "") { $edChoice = "1" }
}

if ($edChoice -eq "0" -or $edChoice -match '^Q') {
    Write-Host "  Tam biet! Chuc ban xay dung thoi quen thanh cong!" -ForegroundColor Cyan
    return
}
if ($edChoice -eq "M" -or $edChoice -eq "MOBILE") { $edChoice = "4" }
if ($edChoice -notin @("1", "2", "3", "4")) { $edChoice = "1" }

Write-Host ""
Write-Host "  BUOC 2 - CHON MAU THOI QUEN (60 CHU DE CAPYBARA, DIGIMON, LINH VAT & HOA LA):" -ForegroundColor White
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
$CatBlocks = @(
    @{ Key = "CAPYBARA"; Label = "--- [MOI v3.9] 13 BO CAPYBARA CHILL COLLECTION DOC BAN (#48-#60) ---"; Color = "Green" }
    @{ Key = "DIGIMON";  Label = "--- 12 BO DIGIMON 7 & 8 CAP TIEN HOA (#36-#47) ---"; Color = "Cyan" }
    @{ Key = "PETS";     Label = "--- THU CUNG SIEU CUTE (Mochi Cat, Bunny, Milk & Mocha, Shiba, Akita, Alpaca...) ---"; Color = "Yellow" }
    @{ Key = "NATURE";   Label = "--- HOA & THIEN NHIEN (Sakura Minimalist, Huong Duong, Xuong Rong, Hong Nhung...) ---"; Color = "Green" }
    @{ Key = "STYLE";    Label = "--- PHONG CACH & MUC TIEU (Dream Home, Candy Jar, Rainbow, Aurora RPG, Matcha...) ---"; Color = "Cyan" }
    @{ Key = "FOCUS";    Label = "--- TAI CHINH & TAP TRUNG (Royal Cat Cash, Alpaca Budget, Sage Budget, Deep Work...) ---"; Color = "Magenta" }
)
foreach ($blk in $CatBlocks) {
    Write-Host ("  " + $blk.Label) -ForegroundColor $blk.Color
    foreach ($t in ($Templates | Where-Object { $_.Cat -eq $blk.Key })) {
        $num = ("[{0}]" -f $t.Id).PadRight(5)
        Write-Host ("  {0} {1,-38} - {2}" -f $num, $t.Stem, $t.Title) -ForegroundColor White
    }
}
Write-Host "  ----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  [A]   Tai TOAN BO 60 mau (Download All 60)" -ForegroundColor Green
Write-Host "  [0]   Thoat" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Goi y: Nhap 1 so (vd: 48), nhieu so (vd: 48,50,52), dai (vd: 48-60), hoac A" -ForegroundColor Yellow

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
    $hint = "Mo file .xlsm -> bam 'Enable Content' 1 lan -> bam 'Thu Hieu Ung Pro' tren tab Huong Dan!"
} elseif ($edChoice -eq "2") {
    $subDir = Join-Path $OutDir "excel_universal_offline"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem).xlsx"
        $queue.Add(@{ Rel = "templates/excel_universal_offline/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $hint = "Nhan dup file .xlsx -> dung ngay 100% Offline, khong Macro, chay moi Excel 2016-365!"
} elseif ($edChoice -eq "3") {
    $subDir = Join-Path $OutDir "google_sheets_edition"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem).xlsx"
        $queue.Add(@{ Rel = "templates/google_sheets_edition/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $queue.Add(@{ Rel = "scripts/google_sheets_1click_setup.gs"; Dest = (Join-Path $subDir "google_sheets_1click_setup.gs"); CheckZip = $false })
    $queue.Add(@{ Rel = "docs/GOOGLE_SHEETS_GUIDE.md"; Dest = (Join-Path $subDir "GOOGLE_SHEETS_GUIDE.md"); CheckZip = $false })
    $hint = "Tai file len Google Sheets -> dan google_sheets_1click_setup.gs vao Apps Script -> Run setupHabitTracker()!"
} else {
    $subDir = Join-Path $OutDir "mobile_portrait_sheets"
    foreach ($id in $parsed.Ids) {
        $t = $Templates | Where-Object { $_.Id -eq $id }
        $fn = "$($t.Stem)_Mobile.xlsx"
        $queue.Add(@{ Rel = "templates/mobile_portrait_sheets/$fn"; Dest = (Join-Path $subDir $fn); CheckZip = $true })
    }
    $queue.Add(@{ Rel = "scripts/google_sheets_1click_setup.gs"; Dest = (Join-Path $subDir "google_sheets_1click_setup.gs"); CheckZip = $false })
    $queue.Add(@{ Rel = "docs/GOOGLE_SHEETS_GUIDE.md"; Dest = (Join-Path $subDir "GOOGLE_SHEETS_GUIDE.md"); CheckZip = $false })
    $hint = "Tai *_Mobile.xlsx len Google Drive -> mo bang App Google Sheets tren dien thoai & dan .gs 1 lan!"
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
