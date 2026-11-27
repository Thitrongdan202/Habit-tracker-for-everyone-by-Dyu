/**
 * ============================================================================
 *  HABIT TRACKER v4.1 — STANDALONE DRIVE BATCH CONVERTER TO 1-CLICK `/copy` LINKS
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  MỤC ĐÍCH (ZERO-FRICTION DISTRIBUTION):
 *    Chuyển đổi hàng loạt toàn bộ 80 file `.xlsx` trong thư mục Google Drive
 *    (`templates/google_sheets_edition/`) thành Google Sheets gốc đã sẵn sàng:
 *      - Đã bật sẵn Native Checkboxes (theo đúng màu pastel từng tuần & từng chủ đề)
 *      - Đã ép font tiếng Việt sắc nét `Be Vietnam Pro` trên toàn bộ tab hiển thị
 *      - Đã ẩn đường lưới mặc định (hidden gridlines) & ẩn 3 sheet hệ thống (`_Calc`, `_Database`, `_Assets`)
 *      - Đã nướng sẵn ảnh native `CellImage` vào `_Assets` (loại bỏ hoàn toàn `=IMAGE("https://...")` -> 0 lỗi `#REF!` / không cần bấm "Allow access" trên cả Điện thoại & Máy tính!)
 *      - Đã mở quyền chia sẻ "Anyone with link: Viewer"
 *      - Tự xuất bảng Markdown gồm 80 link `https://docs.google.com/spreadsheets/d/<ID>/copy`
 *        để dán thẳng lên README.md (người dùng chỉ cần bấm 1 click -> "Make a copy" là dùng ngay!)
 *
 *  ★ NÂNG CẤP TẠI CHỖ CHO 80 FILE ĐÃ CONVERT (GIỮ NGUYÊN 100% LINK `/copy` CŨ):
 *    - Nếu bạn đã convert sẵn 80 file trên Drive, chỉ cần chọn hàm `upgradeExistingSheetsToCellImages` -> bấm Run!
 *    - Script sẽ nướng `CellImage` trực tiếp vào `_Assets` của từng file hiện có (không đổi File ID, giữ nguyên toàn bộ link `/copy` cũ & tự bỏ qua file đã nướng khi chạy lại!).
 *
 *  HƯỚNG DẪN CHẠY 1 LẦN TRÊN GOOGLE DRIVE (2 PHÚT):
 *    1. Tải các file `.xlsx` từ `templates/google_sheets_edition/` lên 1 thư mục trên Google Drive của bạn.
 *    2. Lấy Folder ID từ thanh địa chỉ trình duyệt (đoạn sau `/folders/`).
 *    3. Truy cập https://script.google.com -> New Project -> dán toàn bộ code này vào.
 *    4. Bật Advanced Drive Service (1 lần duy nhất):
 *         Sidebar bên trái -> bấm dấu `+` cạnh "Services" -> chọn "Drive API" (v3 hoặc v2 đều được!) -> Add.
 *    5. Dán Folder ID vào biến `SOURCE_FOLDER_ID` bên dưới -> nhấn Lưu (Ctrl+S).
 *    6. Chọn hàm `batchConvertToCopyLinks` -> bấm Run (Chạy) -> cấp quyền 1 lần.
 *       (Nếu chạy đủ 80 file bị quá giới hạn 6 phút của Apps Script, script tự dừng an toàn
 *        ở mốc 4.5 phút; chỉ cần bấm Run thêm 1 lần nữa sẽ tự nối tiếp phần còn lại nhờ `SKIP_EXISTING = true`!)
 *    7. Mở file `COPY_LINKS_TABLE.md` được tạo tự động ngay trong thư mục output trên Drive
 *       (hoặc copy trực tiếp từ Execution Log)!
 */

// ===================== CONFIGURATION (EDIT BEFORE RUN) =====================
var SOURCE_FOLDER_ID = "PASTE_YOUR_XLSX_DRIVE_FOLDER_ID_HERE";
var OUTPUT_FOLDER_ID = ""; // Để trống -> tự tạo thư mục con "Habit_Tracker_Native_Google_Sheets" trong SOURCE_FOLDER_ID
var OUTPUT_SUBFOLDER_NAME = "Habit_Tracker_Native_Google_Sheets";
var SKIP_EXISTING = true;  // true = chạy lại an toàn không tạo trùng file đã chuyển
var SOFT_LIMIT_MS = 270000; // 4.5 phút (dừng êm trước giới hạn 6 phút của Google Apps Script)

var PUB_FONT_FAMILY = "Be Vietnam Pro";
var PUB_HIDDEN_SHEETS = ["_Calc", "_Database", "_Assets"];
var PUB_WEEK_RANGES = ["C17:I36", "J17:P36", "Q17:W36", "X17:AD36", "AE17:AG36"];
var PUB_WEEK_SAMPLES = ["C17", "J17", "Q17", "X17", "AE17"];

/**
 * Main entrypoint: batch-converts `.xlsx` templates in SOURCE_FOLDER_ID into
 * polished, public-viewer native Google Sheets and writes `COPY_LINKS_TABLE.md`.
 */
function batchConvertToCopyLinks() {
  if (!SOURCE_FOLDER_ID || SOURCE_FOLDER_ID === "PASTE_YOUR_XLSX_DRIVE_FOLDER_ID_HERE") {
    throw new Error("Vui lòng điền SOURCE_FOLDER_ID (ID thư mục Drive chứa file .xlsx) trước khi chạy!");
  }
  if (typeof Drive === "undefined" || !Drive.Files) {
    throw new Error("Vui lòng bật Service 'Drive API' (menu bên trái -> Services -> + -> Drive API -> Add)!");
  }

  var tStart = Date.now();
  var srcFolder = DriveApp.getFolderById(SOURCE_FOLDER_ID);
  var outFolder = resolveOutputFolder_(srcFolder);
  var outFolderId = outFolder.getId();

  // Map existing native Google Sheets in output folder so reruns resume cleanly
  var existingMap = indexExistingSheets_(outFolder);

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

  Logger.log("Found " + xlsxFiles.length + " .xlsx file(s) in '" + srcFolder.getName() + "'.");
  var imageCache = {};
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
      var newId = convertXlsxToNativeSheet_(file.getId(), baseName, outFolderId);
      polishConvertedSheet_(newId, imageCache);
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

  var md = buildMarkdownTable_(existingMap);
  saveMarkdownToFolder_(outFolder, "COPY_LINKS_TABLE.md", md);

  Logger.log("============================================================");
  Logger.log("Done batch run: converted=" + convertedNow + ", skipped=" + skipped + ", totalReady=" + Object.keys(existingMap).length);
  if (pausedForTime) {
    Logger.log("NOTICE: Re-run batchConvertToCopyLinks() to finish remaining files.");
  }
  Logger.log("\n" + md);
}

/**
 * Utility entrypoint: re-generates `COPY_LINKS_TABLE.md` from already-converted
 * Google Sheets inside OUTPUT_FOLDER_ID without re-converting anything.
 */
function exportCopyLinksMarkdown() {
  var srcFolder = DriveApp.getFolderById(SOURCE_FOLDER_ID);
  var outFolder = resolveOutputFolder_(srcFolder);
  var existingMap = indexExistingSheets_(outFolder);
  var md = buildMarkdownTable_(existingMap);
  saveMarkdownToFolder_(outFolder, "COPY_LINKS_TABLE.md", md);
  Logger.log("Exported " + Object.keys(existingMap).length + " /copy links to COPY_LINKS_TABLE.md:\n\n" + md);
}

/**
 * In-place Upgrader: bakes native `CellImage` sprites into `_Assets` across ALL
 * already-converted native Google Sheets in OUTPUT_FOLDER_ID without recreating files
 * or changing any `/copy` URL! Skips already-baked sheets instantly & stops safely at 4.5 min.
 */
function upgradeExistingSheetsToCellImages() {
  if (!OUTPUT_FOLDER_ID && (!SOURCE_FOLDER_ID || SOURCE_FOLDER_ID === "PASTE_YOUR_XLSX_DRIVE_FOLDER_ID_HERE")) {
    throw new Error("Vui lòng điền SOURCE_FOLDER_ID hoặc OUTPUT_FOLDER_ID trước khi chạy!");
  }
  var tStart = Date.now();
  var outFolder = OUTPUT_FOLDER_ID
    ? DriveApp.getFolderById(OUTPUT_FOLDER_ID)
    : resolveOutputFolder_(DriveApp.getFolderById(SOURCE_FOLDER_ID));

  var sheetFiles = [];
  var iter = outFolder.getFilesByType(MimeType.GOOGLE_SHEETS);
  while (iter.hasNext()) {
    sheetFiles.push(iter.next());
  }
  sheetFiles.sort(function (a, b) {
    return a.getName().localeCompare(b.getName(), "en", { numeric: true });
  });

  Logger.log("Scanning " + sheetFiles.length + " existing native Google Sheet(s) in '" + outFolder.getName() + "' for CellImage baking...");
  var imageCache = {};
  var upgraded = 0;
  var skipped = 0;
  var pausedForTime = false;

  for (var i = 0; i < sheetFiles.length; i++) {
    if (Date.now() - tStart > SOFT_LIMIT_MS) {
      pausedForTime = true;
      Logger.log("Reached 4.5-minute safe checkpoint (" + i + "/" + sheetFiles.length + "). Run again to resume!");
      break;
    }

    var file = sheetFiles[i];
    var name = file.getName();
    try {
      var ss = SpreadsheetApp.openById(file.getId());
      var baked = bakeAssetsAsCellImages_(ss, imageCache);
      if (baked === 0) {
        skipped++;
        Logger.log("[" + (i + 1) + "/" + sheetFiles.length + "] SKIP (already baked): " + name);
      } else {
        SpreadsheetApp.flush();
        upgraded++;
        Logger.log("[" + (i + 1) + "/" + sheetFiles.length + "] Baked " + baked + " CellImages: " + name);
      }
    } catch (err) {
      Logger.log("[" + (i + 1) + "/" + sheetFiles.length + "] ERROR on " + name + ": " + err);
    }
  }

  Logger.log("============================================================");
  Logger.log("CellImage upgrade complete: upgraded=" + upgraded + ", skipped=" + skipped + ", total=" + sheetFiles.length);
  if (pausedForTime) {
    Logger.log("NOTICE: Re-run upgradeExistingSheetsToCellImages() to finish remaining sheets.");
  }
}

// ============================================================================
//  DRIVE API v3 / v2 AUTO-DETECT CONVERSION
// ============================================================================
function convertXlsxToNativeSheet_(fileId, baseName, parentFolderId) {
  // Drive API v3 uses `{ name, parents: [id], mimeType }`
  // Drive API v2 uses `{ title, parents: [{ id }] }` + `{ convert: true }`
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
//  NATIVE CELLIMAGE BAKER (ELIMINATES `=IMAGE("https://...")` & `#REF!` FOREVER)
// ============================================================================
function buildBakedCellImage_(url, altTitle, imageCache) {
  if (!imageCache[url]) {
    try {
      var res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
      if (res.getResponseCode() === 200) {
        var blob = res.getBlob();
        var ct = blob.getContentType() || "image/png";
        var b64 = Utilities.base64Encode(blob.getBytes());
        imageCache[url] = "data:" + ct + ";base64," + b64;
      } else {
        Logger.log("  WARN: HTTP " + res.getResponseCode() + " fetching " + url + " (falling back to direct URL)");
        imageCache[url] = url;
      }
    } catch (errFetch) {
      Logger.log("  WARN: UrlFetchApp failed for " + url + ": " + errFetch);
      imageCache[url] = url;
    }
  }

  var src = imageCache[url] || url;
  try {
    return SpreadsheetApp.newCellImage()
      .setSourceUrl(src)
      .setAltTextTitle(altTitle || "Habit Sprite")
      .build();
  } catch (errBuild) {
    return SpreadsheetApp.newCellImage()
      .setSourceUrl(url)
      .setAltTextTitle(altTitle || "Habit Sprite")
      .build();
  }
}

/**
 * Replaces all `=IMAGE("https://...", ...)` formulas in hidden `_Assets!B2:B20`
 * (and any stray `=IMAGE()` formulas on `Hướng Dẫn`) with baked native `CellImage` values.
 * Returns count of baked/patched cells (returns 0 immediately if already baked — idempotent!).
 */
function bakeAssetsAsCellImages_(ss, imageCache) {
  imageCache = imageCache || {};
  var imgRe = /^=\s*(?:_xlfn\.)?IMAGE\(\s*"([^"]+)"/i;
  var bakedCount = 0;
  var urlToAssetRef = {};

  var wsAssets = ss.getSheetByName("_Assets");
  if (wsAssets) {
    var labels = wsAssets.getRange("A2:A20").getValues();
    var formulas = wsAssets.getRange("B2:B20").getFormulas();
    for (var i = 0; i < formulas.length; i++) {
      var f = formulas[i][0];
      if (!f) continue;
      var m = f.match(imgRe);
      if (!m) continue;
      var url = m[1];
      var rowNum = 2 + i;
      var stageLabel = String(labels[i][0] || "").trim() || ("Habit Sprite " + i);
      var cellImg = buildBakedCellImage_(url, stageLabel, imageCache);
      wsAssets.getRange(rowNum, 2).setValue(cellImg);
      urlToAssetRef[url] = "_Assets!$B$" + rowNum;
      bakedCount++;
    }
  }

  // Also scan `Hướng Dẫn` (Guide) in case any cell still contains a direct `=IMAGE("https://...")` formula
  var sheets = ss.getSheets();
  for (var s = 0; s < sheets.length; s++) {
    var sh = sheets[s];
    if (sh.getName().indexOf("Hướng Dẫn") === -1) continue;
    var dr = sh.getDataRange();
    if (dr.getNumRows() === 0 || dr.getNumColumns() === 0) continue;
    var gFormulas = dr.getFormulas();
    var r0 = dr.getRow();
    var c0 = dr.getColumn();
    for (var r = 0; r < gFormulas.length; r++) {
      for (var c = 0; c < gFormulas[r].length; c++) {
        var gf = gFormulas[r][c];
        if (!gf) continue;
        var gm = gf.match(imgRe);
        if (!gm) continue;
        var gUrl = gm[1];
        if (urlToAssetRef[gUrl]) {
          sh.getRange(r0 + r, c0 + c).setFormula("=" + urlToAssetRef[gUrl]);
        } else {
          sh.getRange(r0 + r, c0 + c).setValue(buildBakedCellImage_(gUrl, "Guide Sprite", imageCache));
        }
        bakedCount++;
      }
    }
  }

  return bakedCount;
}

// ============================================================================
//  NATIVE SHEET POLISH (BE VIETNAM PRO + HIDDEN GRIDLINES + PASTEL CHECKBOXES)
// ============================================================================
function polishConvertedSheet_(spreadsheetId, imageCache) {
  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheets = ss.getSheets();

  var tracker = null;
  var dt = null;
  var yg = null;

  for (var i = 0; i < sheets.length; i++) {
    var sh = sheets[i];
    var nm = sh.getName();

    if (PUB_HIDDEN_SHEETS.indexOf(nm) !== -1) {
      if (!sh.isSheetHidden()) sh.hideSheet();
      continue;
    }

    // Hide default grey gridlines & enforce crisp Vietnamese font on every visible tab
    sh.setHiddenGridlines(true);
    var dr = sh.getDataRange();
    if (dr.getNumRows() > 0 && dr.getNumColumns() > 0) {
      dr.setFontFamily(PUB_FONT_FAMILY);
    }

    if (nm.indexOf("Nhiệm Vụ Ngày") !== -1) {
      dt = sh;
    } else if (nm.indexOf("Yearly Goals") !== -1) {
      yg = sh;
    } else if (nm.indexOf("Hướng Dẫn") === -1 && nm.indexOf("Tổng Kết") === -1) {
      if (!tracker) tracker = sh;
    }
  }

  // 1) Monthly Tracker Checkboxes (C17:AG36 with per-week pastel colors + optional weekly addons)
  if (tracker) {
    var fallbackAccent = tracker.getRange("B14").getBackground() || "#C88E8E";
    var gridRng = tracker.getRange("C17:AG36");
    var gridVals = gridRng.getValues();
    gridRng.insertCheckboxes()
      .setHorizontalAlignment("center")
      .setVerticalAlignment("middle")
      .setFontSize(10);

    for (var w = 0; w < PUB_WEEK_RANGES.length; w++) {
      var col = tracker.getRange(PUB_WEEK_SAMPLES[w]).getFontColor();
      if (!col || col === "#000000" || col.toLowerCase() === "#ffffff") {
        col = fallbackAccent;
      }
      tracker.getRange(PUB_WEEK_RANGES[w]).setFontColor(col);
    }
    gridRng.setValues(gridVals);

    var maxR = tracker.getMaxRows();
    if (maxR >= 54 && String(tracker.getRange("B47").getValue() || "").toUpperCase().indexOf("WEEKLY") !== -1) {
      pubConvertBoolRange_(tracker, "C48:AG54", fallbackAccent);
    }
    if (maxR >= 46 && String(tracker.getRange("B39").getValue() || "").toUpperCase().indexOf("WEEKLY") !== -1) {
      pubConvertBoolRange_(tracker, "G41:AC46", fallbackAccent);
    }
  }

  // 2) Daily One-Off Tasks Checkboxes (B9:B28)
  if (dt) {
    pubApplyCheckboxes_(dt.getRange("B9:B28"), dt.getRange("B2").getBackground() || "#B57A7A");
  }

  // 3) Yearly Goals Checkboxes (B6:B25)
  if (yg) {
    pubApplyCheckboxes_(yg.getRange("B6:B25"), yg.getRange("B2").getBackground() || "#B57A7A");
  }

  // 4) Bake native CellImages into `_Assets` so fresh /copy sheets have ZERO `#REF!`
  bakeAssetsAsCellImages_(ss, imageCache);

  SpreadsheetApp.flush();
}

function pubApplyCheckboxes_(rng, accent) {
  var vals = rng.getValues();
  rng.insertCheckboxes()
    .setValues(vals)
    .setFontColor(accent)
    .setFontSize(10)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
}

function pubConvertBoolRange_(sheet, a1Range, accent) {
  var rng = sheet.getRange(a1Range);
  var vals = rng.getValues();
  var r0 = rng.getRow();
  var c0 = rng.getColumn();
  var a1s = [];
  for (var r = 0; r < vals.length; r++) {
    for (var c = 0; c < vals[r].length; c++) {
      if (typeof vals[r][c] === "boolean") {
        a1s.push(pubColToLetter_(c0 + c) + (r0 + r));
      }
    }
  }
  if (a1s.length === 0) return;
  sheet.getRangeList(a1s)
    .insertCheckboxes()
    .setFontColor(accent)
    .setFontSize(10)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
  rng.setValues(vals);
}

// ============================================================================
//  FOLDER & MARKDOWN EXPORT HELPERS
// ============================================================================
function resolveOutputFolder_(srcFolder) {
  if (OUTPUT_FOLDER_ID) {
    return DriveApp.getFolderById(OUTPUT_FOLDER_ID);
  }
  var subs = srcFolder.getFoldersByName(OUTPUT_SUBFOLDER_NAME);
  if (subs.hasNext()) return subs.next();
  return srcFolder.createFolder(OUTPUT_SUBFOLDER_NAME);
}

function indexExistingSheets_(folder) {
  var map = {};
  var files = folder.getFilesByType(MimeType.GOOGLE_SHEETS);
  while (files.hasNext()) {
    var f = files.next();
    map[f.getName()] = f.getId();
  }
  return map;
}

function buildMarkdownTable_(sheetMap) {
  var names = Object.keys(sheetMap).sort(function (a, b) {
    return a.localeCompare(b, "en", { numeric: true });
  });
  var lines = [
    "| # | Template Name | 1-Click Google Sheets Copy Link |",
    "|---|---|---|"
  ];
  for (var i = 0; i < names.length; i++) {
    var nm = names[i];
    var id = sheetMap[nm];
    var m = nm.match(/^(\d+)_(.+)$/);
    var num = m ? "**" + m[1] + "**" : String(i + 1);
    var pretty = m ? m[2].replace(/_/g, " ") : nm;
    var url = "https://docs.google.com/spreadsheets/d/" + id + "/copy";
    lines.push("| " + num + " | **" + pretty + "** | [☁️ Make a Copy](" + url + ") |");
  }
  return lines.join("\n") + "\n";
}

function saveMarkdownToFolder_(folder, fileName, content) {
  var existing = folder.getFilesByName(fileName);
  if (existing.hasNext()) {
    existing.next().setContent(content);
  } else {
    folder.createFile(fileName, content, MimeType.PLAIN_TEXT);
  }
}

function pubColToLetter_(col) {
  var s = "";
  while (col > 0) {
    var rem = (col - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    col = Math.floor((col - 1) / 26);
  }
  return s;
}
