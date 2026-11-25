/**
 * ============================================================================
 *  HABIT TRACKER MOBILE PORTRAIT — BATCH CONVERTER TO 1-CLICK `/copy` LINKS
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  MỤC ĐÍCH (ZERO-FRICTION MOBILE DISTRIBUTION):
 *    Chuyển đổi hàng loạt toàn bộ 60 file `*_Mobile.xlsx` trong thư mục Google Drive
 *    (`templates/mobile_portrait_sheets/`) thành Google Sheets khổ dọc gốc đã sẵn sàng
 *    mở 1 chạm trên ứng dụng Google Trang tính điện thoại (iOS / Android):
 *      - Đã bật sẵn Native Checkboxes đúng tọa độ Mobile (`C21:I35`, `B16:B30`, `B11:B22`)
 *        với bộ lọc boolean an toàn (tuyệt đối không chạm tiêu đề / ngày / dòng tổng!)
 *      - Đã giữ nguyên màu pastel từng ngày T2–CN & màu chủ đề từng template
 *      - Đã ép font tiếng Việt sắc nét `Be Vietnam Pro` trên toàn bộ 4 tab hiển thị
 *      - Đã ẩn đường lưới mặc định (`setHiddenGridlines(true)`) & ẩn `_Calc`, `_Database`, `_Assets`
 *      - Đã mở quyền chia sẻ RIÊNG TỪNG FILE ("Anyone with link: Viewer") — KHÔNG chia sẻ thư mục gốc
 *      - Tự xuất bảng Markdown gồm 60 link `https://docs.google.com/spreadsheets/d/<ID>/copy`
 *        vào file `MOBILE_COPY_LINKS_TABLE.md` trong thư mục output!
 *
 *  HƯỚNG DẪN CHẠY 1 LẦN TRÊN GOOGLE DRIVE (2 PHÚT):
 *    1. Tải các file `*_Mobile.xlsx` từ `templates/mobile_portrait_sheets/` lên 1 thư mục Drive.
 *    2. Lấy Folder ID từ thanh địa chỉ trình duyệt (đoạn sau `/folders/`).
 *    3. Truy cập https://script.google.com -> New Project -> dán toàn bộ code này vào.
 *    4. Bật Advanced Drive Service (1 lần duy nhất):
 *         Sidebar bên trái -> bấm dấu `+` cạnh "Services" -> chọn "Drive API" (v3 hoặc v2 đều được!) -> Add.
 *    5. Dán Folder ID vào biến `SOURCE_FOLDER_ID` bên dưới -> nhấn Lưu (Ctrl+S).
 *    6. Chọn hàm `batchConvertMobileToCopyLinks` -> bấm Run (Chạy) -> cấp quyền 1 lần.
 *       (Nếu chạy đủ 60 file chạm mốc 4.5 phút, script tự dừng an toàn; chỉ cần bấm Run thêm 1 lần
 *        sẽ tự động nối tiếp phần còn lại nhờ `SKIP_EXISTING = true`!)
 *    7. Mở file `MOBILE_COPY_LINKS_TABLE.md` trong thư mục output (hoặc copy từ Execution Log)!
 */

// ===================== CONFIGURATION (EDIT BEFORE RUN) =====================
var SOURCE_FOLDER_ID = "PASTE_YOUR_MOBILE_XLSX_DRIVE_FOLDER_ID_HERE";
var OUTPUT_FOLDER_ID = ""; // Để trống -> tự tạo thư mục con "Habit_Tracker_Native_Mobile_Sheets" trong SOURCE_FOLDER_ID
var OUTPUT_SUBFOLDER_NAME = "Habit_Tracker_Native_Mobile_Sheets";
var SKIP_EXISTING = true;   // true = chạy lại an toàn không tạo trùng file đã chuyển
var SOFT_LIMIT_MS = 270000; // 4.5 phút (dừng êm trước giới hạn 6 phút của Google Apps Script)

var MOB_FONT_FAMILY = "Be Vietnam Pro";
var MOB_HIDDEN_SHEETS = ["_Calc", "_Database", "_Assets"];
var MOB_CHECKBOX_SIZE = 12; // Cỡ checkbox thoải mái cho ngón tay trên điện thoại

// Verified Mobile Portrait interactive boolean ranges (from scripts/hx/mobile.py):
//   - Tab 1 (`📱 Tuần Này`):              C21:I35 (15 habits x 7 days T2..CN = 105 booleans)
//   - Tab 2 (`📝 Việc Hôm Nay`):          B16:B30 (15 daily tasks = 15 booleans)
//   - Tab 3 (`🎯 Mục Tiêu & Thành Tựu`):  B11:B22 (12 yearly goals = 12 booleans)
var MOB_WEEK_RANGE = "C21:I35";
var MOB_WEEK_DAY_COLS = ["C", "D", "E", "F", "G", "H", "I"];
var MOB_TASKS_RANGE = "B16:B30";
var MOB_GOALS_RANGE = "B11:B22";

/**
 * Main entrypoint: batch-converts `*_Mobile.xlsx` templates in SOURCE_FOLDER_ID into
 * polished, public-viewer native Google Sheets and writes `MOBILE_COPY_LINKS_TABLE.md`.
 */
function batchConvertMobileToCopyLinks() {
  if (!SOURCE_FOLDER_ID || SOURCE_FOLDER_ID === "PASTE_YOUR_MOBILE_XLSX_DRIVE_FOLDER_ID_HERE") {
    throw new Error("Vui lòng điền SOURCE_FOLDER_ID (ID thư mục Drive chứa file *_Mobile.xlsx) trước khi chạy!");
  }
  if (typeof Drive === "undefined" || !Drive.Files) {
    throw new Error("Vui lòng bật Service 'Drive API' (menu bên trái -> Services -> + -> Drive API -> Add)!");
  }

  var tStart = Date.now();
  var srcFolder = DriveApp.getFolderById(SOURCE_FOLDER_ID);
  var outFolder = mobResolveOutputFolder_(srcFolder);
  var outFolderId = outFolder.getId();

  // Map existing native Google Sheets in output folder so reruns resume cleanly
  var existingMap = mobIndexExistingSheets_(outFolder);

  // Gather and numerically sort all `.xlsx` source files (01..60)
  var xlsxFiles = [];
  var iter = srcFolder.getFiles();
  while (iter.hasNext()) {
    var f = iter.next();
    if (/\.xlsx$/i.test(f.getName())) {
      xlsxFiles.push(f);
    }
  }
  xlsxFiles.sort(function (a, b) {
    return a.getName().localeCompare(b.getName(), "en", { numeric: true });
  });

  Logger.log("Found " + xlsxFiles.length + " mobile .xlsx file(s) in '" + srcFolder.getName() + "'.");
  var convertedNow = 0;
  var skipped = 0;
  var pausedForTime = false;

  for (var i = 0; i < xlsxFiles.length; i++) {
    if (Date.now() - tStart > SOFT_LIMIT_MS) {
      pausedForTime = true;
      Logger.log("Reached 4.5-minute safe checkpoint (" + i + "/" + xlsxFiles.length + "). Run again to resume!");
      break;
    }

    var file = xlsxFiles[i];
    var baseName = file.getName().replace(/\.xlsx$/i, "");

    if (SKIP_EXISTING && existingMap[baseName]) {
      skipped++;
      continue;
    }

    try {
      var newId = mobConvertXlsxToNativeSheet_(file.getId(), baseName, outFolderId);
      mobPolishConvertedSheet_(newId);
      // Safe privacy: set sharing ONLY on the individual converted file (never on parent folder!)
      DriveApp.getFileById(newId).setSharing(
        DriveApp.Access.ANYONE_WITH_LINK,
        DriveApp.Permission.VIEW
      );
      existingMap[baseName] = newId;
      convertedNow++;
      Logger.log("[" + (i + 1) + "/" + xlsxFiles.length + "] OK: " + baseName + " -> /copy ID=" + newId);
    } catch (err) {
      Logger.log("[" + (i + 1) + "/" + xlsxFiles.length + "] ERROR on " + baseName + ": " + err);
    }
  }

  var md = mobBuildMarkdownTable_(existingMap);
  mobSaveMarkdownToFolder_(outFolder, "MOBILE_COPY_LINKS_TABLE.md", md);

  Logger.log("============================================================");
  Logger.log("Done mobile batch run: converted=" + convertedNow + ", skipped=" + skipped + ", totalReady=" + Object.keys(existingMap).length);
  if (pausedForTime) {
    Logger.log("NOTICE: Re-run batchConvertMobileToCopyLinks() to finish remaining files.");
  }
  Logger.log("\n" + md);
}

/**
 * Utility entrypoint: re-generates `MOBILE_COPY_LINKS_TABLE.md` from already-converted
 * Mobile Google Sheets inside OUTPUT_FOLDER_ID without re-converting anything.
 */
function exportMobileCopyLinksMarkdown() {
  var srcFolder = DriveApp.getFolderById(SOURCE_FOLDER_ID);
  var outFolder = mobResolveOutputFolder_(srcFolder);
  var existingMap = mobIndexExistingSheets_(outFolder);
  var md = mobBuildMarkdownTable_(existingMap);
  mobSaveMarkdownToFolder_(outFolder, "MOBILE_COPY_LINKS_TABLE.md", md);
  Logger.log("Exported " + Object.keys(existingMap).length + " Mobile /copy links to MOBILE_COPY_LINKS_TABLE.md:\n\n" + md);
}

// ============================================================================
//  DRIVE API v3 / v2 AUTO-DETECT CONVERSION
// ============================================================================
function mobConvertXlsxToNativeSheet_(fileId, baseName, parentFolderId) {
  try {
    var createdV3 = Drive.Files.copy(
      {
        name: baseName,
        parents: [parentFolderId],
        mimeType: MimeType.GOOGLE_SHEETS
      },
      fileId
    );
    if (createdV3 && createdV3.id) return createdV3.id;
  } catch (errV3) {
    var createdV2 = Drive.Files.copy(
      {
        title: baseName,
        parents: [{ id: parentFolderId }]
      },
      fileId,
      { convert: true }
    );
    if (createdV2 && createdV2.id) return createdV2.id;
    throw errV3;
  }
  throw new Error("Drive.Files.copy returned no file ID for " + baseName);
}

// ============================================================================
//  PRECISION MOBILE SHEET POLISH (BE VIETNAM PRO + HIDDEN GRIDLINES + BOOLEAN-SAFE CHECKBOXES)
// ============================================================================
function mobPolishConvertedSheet_(spreadsheetId) {
  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheets = ss.getSheets();

  var wsWeek = null;
  var wsTasks = null;
  var wsGoals = null;

  for (var i = 0; i < sheets.length; i++) {
    var sh = sheets[i];
    var nm = sh.getName();

    if (MOB_HIDDEN_SHEETS.indexOf(nm) !== -1) {
      if (!sh.isSheetHidden()) sh.hideSheet();
      continue;
    }

    // Hide default grey gridlines & enforce crisp Vietnamese font on all 4 visible mobile tabs
    sh.setHiddenGridlines(true);
    var dr = sh.getDataRange();
    if (dr.getNumRows() > 0 && dr.getNumColumns() > 0) {
      dr.setFontFamily(MOB_FONT_FAMILY);
    }

    if (nm.indexOf("Tuần Này") !== -1) {
      wsWeek = sh;
    } else if (nm.indexOf("Việc Hôm Nay") !== -1) {
      wsTasks = sh;
    } else if (nm.indexOf("Mục Tiêu") !== -1) {
      wsGoals = sh;
    }
  }

  // 1) Tab 1 (`📱 Tuần Này`): Boolean-safe Checkboxes on C21:I35 preserving each day column's pastel color!
  if (wsWeek) {
    var weekFallback = wsWeek.getRange("B2").getBackground() || "#C88E8E";
    mobConvertBoolRangePerCol_(wsWeek, MOB_WEEK_RANGE, MOB_WEEK_DAY_COLS, 21, weekFallback);
  }

  // 2) Tab 2 (`📝 Việc Hôm Nay`): Boolean-safe Checkboxes on B16:B30
  if (wsTasks) {
    var taskAccent = mobPickAccentColor_(wsTasks, "B16", "B2", "#B57A7A");
    mobConvertBoolRange_(wsTasks, MOB_TASKS_RANGE, taskAccent);
  }

  // 3) Tab 3 (`🎯 Mục Tiêu & Thành Tựu`): Boolean-safe Checkboxes on B11:B22
  if (wsGoals) {
    var goalAccent = mobPickAccentColor_(wsGoals, "B11", "B2", "#B57A7A");
    mobConvertBoolRange_(wsGoals, MOB_GOALS_RANGE, goalAccent);
  }

  SpreadsheetApp.flush();
}

function mobPickAccentColor_(sheet, sampleCellA1, bannerCellA1, defaultHex) {
  var fg = sheet.getRange(sampleCellA1).getFontColor();
  if (fg && fg !== "#000000" && fg.toLowerCase() !== "#ffffff") {
    return fg;
  }
  var bg = sheet.getRange(bannerCellA1).getBackground();
  if (bg && bg !== "#000000" && bg.toLowerCase() !== "#ffffff") {
    return bg;
  }
  return defaultHex;
}

/**
 * Boolean-safe checkbox conversion inside a verified multi-column range (e.g. C21:I35),
 * preserving each column's themed pastel foreground color and original boolean values.
 */
function mobConvertBoolRangePerCol_(sheet, a1Range, colLetters, sampleRow, fallbackColor) {
  var rng = sheet.getRange(a1Range);
  var vals = rng.getValues();
  var r0 = rng.getRow();
  var c0 = rng.getColumn();

  var colColors = [];
  for (var idx = 0; idx < colLetters.length; idx++) {
    var cHex = sheet.getRange(colLetters[idx] + sampleRow).getFontColor();
    if (!cHex || cHex === "#000000" || cHex.toLowerCase() === "#ffffff") {
      cHex = fallbackColor;
    }
    colColors.push(cHex);
  }

  var byColor = {};
  for (var r = 0; r < vals.length; r++) {
    for (var c = 0; c < vals[r].length; c++) {
      if (typeof vals[r][c] === "boolean") {
        var hex = colColors[c] || fallbackColor;
        if (!byColor[hex]) byColor[hex] = [];
        byColor[hex].push(mobColToLetter_(c0 + c) + (r0 + r));
      }
    }
  }

  var colorKeys = Object.keys(byColor);
  if (colorKeys.length === 0) return;

  for (var k = 0; k < colorKeys.length; k++) {
    var colorHex = colorKeys[k];
    sheet.getRangeList(byColor[colorHex])
      .insertCheckboxes()
      .setFontColor(colorHex)
      .setFontSize(MOB_CHECKBOX_SIZE)
      .setHorizontalAlignment("center")
      .setVerticalAlignment("middle");
  }
  // Restore exact boolean values in ONE bulk write
  rng.setValues(vals);
}

/**
 * Boolean-safe checkbox conversion inside a verified single-column range (e.g. B16:B30, B11:B22).
 * Only cells whose value is strictly `boolean` are converted — headers/totals are untouched!
 */
function mobConvertBoolRange_(sheet, a1Range, accent) {
  var rng = sheet.getRange(a1Range);
  var vals = rng.getValues();
  var r0 = rng.getRow();
  var c0 = rng.getColumn();
  var a1s = [];
  for (var r = 0; r < vals.length; r++) {
    for (var c = 0; c < vals[r].length; c++) {
      if (typeof vals[r][c] === "boolean") {
        a1s.push(mobColToLetter_(c0 + c) + (r0 + r));
      }
    }
  }
  if (a1s.length === 0) return;
  sheet.getRangeList(a1s)
    .insertCheckboxes()
    .setFontColor(accent)
    .setFontSize(MOB_CHECKBOX_SIZE)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
  rng.setValues(vals);
}

// ============================================================================
//  FOLDER & MARKDOWN EXPORT HELPERS
// ============================================================================
function mobResolveOutputFolder_(srcFolder) {
  if (OUTPUT_FOLDER_ID) {
    return DriveApp.getFolderById(OUTPUT_FOLDER_ID);
  }
  var subs = srcFolder.getFoldersByName(OUTPUT_SUBFOLDER_NAME);
  if (subs.hasNext()) return subs.next();
  return srcFolder.createFolder(OUTPUT_SUBFOLDER_NAME);
}

function mobIndexExistingSheets_(folder) {
  var map = {};
  var files = folder.getFilesByType(MimeType.GOOGLE_SHEETS);
  while (files.hasNext()) {
    var f = files.next();
    map[f.getName()] = f.getId();
  }
  return map;
}

function mobBuildMarkdownTable_(sheetMap) {
  var names = Object.keys(sheetMap).sort(function (a, b) {
    return a.localeCompare(b, "en", { numeric: true });
  });
  var lines = [
    "| # | Mobile Portrait Template | 1-Click Mobile Google Sheets Copy Link |",
    "|---|---|---|"
  ];
  for (var i = 0; i < names.length; i++) {
    var nm = names[i];
    var id = sheetMap[nm];
    var m = nm.match(/^(\d+)_(.+?)(?:_Mobile)?$/);
    var num = m ? "**" + m[1] + "**" : String(i + 1);
    var pretty = m ? m[2].replace(/_/g, " ") : nm;
    var url = "https://docs.google.com/spreadsheets/d/" + id + "/copy";
    lines.push("| " + num + " | **" + pretty + "** *(Mobile Portrait)* | [📱 Make a Copy](" + url + ") |");
  }
  return lines.join("\n") + "\n";
}

function mobSaveMarkdownToFolder_(folder, fileName, content) {
  var existing = folder.getFilesByName(fileName);
  if (existing.hasNext()) {
    existing.next().setContent(content);
  } else {
    folder.createFile(fileName, content, MimeType.PLAIN_TEXT);
  }
}

function mobColToLetter_(col) {
  var s = "";
  while (col > 0) {
    var rem = (col - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    col = Math.floor((col - 1) / 26);
  }
  return s;
}
