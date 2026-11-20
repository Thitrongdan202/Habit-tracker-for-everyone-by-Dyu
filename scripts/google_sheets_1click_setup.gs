/**
 * ============================================================================
 *  HABIT TRACKER v2.3 — 1-CLICK GOOGLE SHEETS CHECKBOX + AUTO-SAVE ENGINE
 *  AUTO-DETECTS BOTH:
 *    - Desktop 4-Tab Google Sheets Edition (`templates/google_sheets_edition/`)
 *    - Mobile Portrait Edition (`templates/mobile_portrait_sheets/`)
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  HƯỚNG DẪN CÀI ĐẶT 1 LẦN (10 GIÂY):
 *    1. Tải file `.xlsx` lên Google Drive -> Mở bằng Google Trang tính (Google Sheets)
 *       -> Tệp (File) -> Lưu dưới dạng Google Trang tính (Save as Google Sheets).
 *    2. Mở menu: Tiện ích mở rộng (Extensions) -> Apps Script.
 *    3. Xóa mã mặc định, dán toàn bộ đoạn code này vào và nhấn Lưu (Ctrl+S).
 *    4. Chọn hàm `setupHabitTracker` trên thanh công cụ -> nhấn Run (Chạy) -> cấp quyền 1 lần.
 *
 *  KẾT QUẢ:
 *    ✅ Tự nhận diện bản Desktop (4 tab) hoặc bản Mobile Portrait (3 tab)!
 *    ✅ Biến toàn bộ vùng tick `TRUE/FALSE` thành Checkbox gốc màu Pastel trong 1 giây!
 *    ✅ Tự kích hoạt `onEdit(e)`:
 *       - Desktop: đổi Tháng (B3) / Năm (B5) hoặc Năm Mục Tiêu (I2) tự lưu/nạp `_Database` theo `YYYY-MM` / `YYYY`!
 *       - Mobile Portrait: đổi Tháng (B5) / Năm (C5) / Tuần (F5) hoặc Năm Mục Tiêu (E3) tự lưu/nạp `_Database` theo `YYYY-MM-W#` / `YYYY`!
 */

var HT_CALC_SHEET = "_Calc";
var HT_DB_SHEET = "_Database";
var HT_N_HABITS_DESK = 20;
var HT_N_GOALS_DESK = 20;
var HT_N_HABITS_MOB = 15;
var HT_N_GOALS_MOB = 12;

var HT_MONTHS = {
  january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,
  july: 7, august: 8, september: 9, october: 10, november: 11, december: 12
};

function isMobilePortraitWorkbook_(ss) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName().indexOf("Tuần Này") !== -1) return true;
  }
  return false;
}

function setupHabitTracker() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (isMobilePortraitWorkbook_(ss)) {
    setupMobilePortrait_(ss);
  } else {
    setupDesktopEdition_(ss);
  }
}

function setupMobilePortrait_(ss) {
  var wsWk = findSheetContaining_(ss, "Tuần Này");
  var wsGo = findSheetContaining_(ss, "Mục Tiêu");
  var converted = 0;

  if (wsWk) {
    var accent = wsWk.getRange("B2").getBackground() || "#C88E8E";
    var grid = wsWk.getRange("C21:I35");
    var vals = grid.getValues();
    grid.insertCheckboxes();
    grid.setValues(vals);
    grid.setFontColor(accent);
    grid.setFontSize(14);
    grid.setHorizontalAlignment("center");
    grid.setVerticalAlignment("middle");
    converted++;
  }

  if (wsGo) {
    var gAccent = wsGo.getRange("B2").getBackground() || "#B57A7A";
    var gRange = wsGo.getRange("B11:B22");
    var gVals = gRange.getValues();
    gRange.insertCheckboxes();
    gRange.setValues(gVals);
    gRange.setFontColor(gAccent);
    gRange.setFontSize(14);
    gRange.setHorizontalAlignment("center");
    gRange.setVerticalAlignment("middle");
    converted++;
  }

  hideIfExists_(ss, HT_CALC_SHEET);
  hideIfExists_(ss, HT_DB_SHEET);
  SpreadsheetApp.flush();
  ss.toast(
    "Bản Điện Thoại (Mobile Portrait): Đã bật Checkbox Pastel cho " + converted + " bảng & kích hoạt tự lưu Tuần/Tháng vào _Database!",
    "Habit Tracker Mobile v2.3 — Sẵn sàng 📱✨",
    8
  );
}

function setupDesktopEdition_(ss) {
  var tracker = findDesktopTrackerSheet_(ss);
  var yg = findSheetContaining_(ss, "Yearly Goals");
  var converted = 0;

  if (tracker) {
    var accent = tracker.getRange("B14").getBackground() || "#C88E8E";
    var grid = tracker.getRange("C17:AG36");
    var vals = grid.getValues();
    grid.insertCheckboxes();
    grid.setValues(vals);
    grid.setFontColor(accent);
    grid.setHorizontalAlignment("center");
    grid.setVerticalAlignment("middle");
    converted++;

    if (tracker.getMaxRows() >= 54) {
      var probe = String(tracker.getRange("B47").getValue() || "");
      if (probe.toUpperCase().indexOf("WEEKLY") !== -1) {
        convertBooleanCellsInRange_(tracker, "C48:AG54", accent);
      }
    }
  }

  if (yg) {
    var ygAccent = yg.getRange("B2").getBackground() || "#B57A7A";
    var ygRange = yg.getRange("B6:B25");
    var ygVals = ygRange.getValues();
    ygRange.insertCheckboxes();
    ygRange.setValues(ygVals);
    ygRange.setFontColor(ygAccent);
    ygRange.setHorizontalAlignment("center");
    ygRange.setVerticalAlignment("middle");
    converted++;
  }

  hideIfExists_(ss, HT_CALC_SHEET);
  hideIfExists_(ss, HT_DB_SHEET);
  SpreadsheetApp.flush();
  ss.toast(
    "Bản Desktop: Đã bật Checkbox Pastel cho " + converted + " bảng & kích hoạt tự lưu 12 tháng vào _Database!",
    "Habit Tracker v2.3 — Sẵn sàng ✨",
    8
  );
}

/**
 * Simple Trigger: automatically routes Desktop vs. Mobile Portrait dropdown switches!
 */
function onEdit(e) {
  if (!e || !e.range) return;
  var ss = e.source;
  var sh = e.range.getSheet();
  var a1 = e.range.getA1Notation();
  var name = sh.getName();

  if (name === HT_CALC_SHEET || name === HT_DB_SHEET || name.indexOf("Hướng Dẫn") !== -1) return;

  if (isMobilePortraitWorkbook_(ss)) {
    if (name.indexOf("Tuần Này") !== -1) {
      if (a1 === "B5" || a1 === "C5" || a1 === "C5:E5" || a1 === "F5" || a1 === "F5:I5") {
        handleMobileWeekSwitch_(ss, sh);
      }
    } else if (name.indexOf("Mục Tiêu") !== -1) {
      if (a1 === "E3" || a1 === "E3:I3") {
        handleMobileGoalsSwitch_(ss, sh);
      }
    }
    return;
  }

  // Desktop 4-tab edition
  if (name.indexOf("Tổng Kết") !== -1) return;
  if (name.indexOf("Yearly Goals") !== -1) {
    if (a1 === "I2") handleDesktopYearlyGoalsSwitch_(ss, sh);
    return;
  }
  if (a1 === "B3" || a1 === "B5") {
    handleDesktopMonthlySwitch_(ss, sh);
  }
}

// ============================================================================
//  MOBILE PORTRAIT PERSISTENCE ENGINE (YYYY-MM-W# & YYYY)
// ============================================================================
function parseWeekNum_(raw) {
  var m = String(raw || "").match(/(\d+)/);
  return m ? parseInt(m[1], 10) : 0;
}

function handleMobileWeekSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldKey = String(wsCalc.getRange("E14").getValue() || "").trim();
  var newMo = HT_MONTHS[String(ws.getRange("B5").getValue() || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(ws.getRange("C5").getValue(), 10) || 0;
  var newWk = parseWeekNum_(ws.getRange("F5").getValue());
  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100 || newWk < 1 || newWk > 5) return;

  var newKey = pad4_(newYr) + "-" + pad2_(newMo) + "-W" + newWk;
  if (oldKey === newKey) return;

  // 1) Save current week (B21:B35 names + C21:I35 ticks) under oldKey
  if (oldKey.indexOf("-W") !== -1) {
    var curNames = ws.getRange("B21:B35").getValues();
    var curGrid = ws.getRange("C21:I35").getValues();
    saveMobileWeekToDb_(ss, wsDb, oldKey, curNames, curGrid);
  }

  // 2) Load newKey from _Database (or open 100% clean blank FALSE grid!)
  var srcRow = findBlockRow_(wsDb, 1, newKey, HT_N_HABITS_MOB);
  var loadGrid = [];
  if (srcRow > 0) {
    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_MOB, 10).getValues();
    var loadNames = [];
    var hasAny = false;
    for (var r = 0; r < HT_N_HABITS_MOB; r++) {
      var nm = srcBlock[r][2];
      if (String(nm || "").trim() !== "") hasAny = true;
      loadNames.push([nm]);
      var rowOut = [];
      for (var d = 0; d < 7; d++) rowOut.push(isChecked_(srcBlock[r][3 + d]));
      loadGrid.push(rowOut);
    }
    if (hasAny) ws.getRange("B21:B35").setValues(loadNames);
    ws.getRange("C21:I35").setValues(loadGrid);
  } else {
    for (var r2 = 0; r2 < HT_N_HABITS_MOB; r2++) {
      loadGrid.push([false, false, false, false, false, false, false]);
    }
    ws.getRange("C21:I35").setValues(loadGrid);
  }

  wsCalc.getRange("E14").setValue(newKey);
  SpreadsheetApp.flush();
}

function saveMobileWeekToDb_(ss, wsDb, saveKey, namesArr, gridArr) {
  var rawBlock = [];
  for (var r = 0; r < HT_N_HABITS_MOB; r++) {
    var row = [saveKey, r + 1, namesArr[r][0]];
    for (var d = 0; d < 7; d++) row.push(isChecked_(gridArr[r][d]));
    rawBlock.push(row);
  }
  var dstRow = findBlockRow_(wsDb, 1, saveKey, HT_N_HABITS_MOB);
  if (dstRow === 0) dstRow = getLastRowInCol_(wsDb, 1) + 1;
  wsDb.getRange(dstRow, 1, HT_N_HABITS_MOB, 10).setValues(rawBlock);

  // Compute WeeklySummary (Cols M:U = 13..21)
  var parts = saveKey.split("-");
  var yr = parseInt(parts[0], 10);
  var mo = parseInt(parts[1], 10);
  var wk = parseInt(parts[2].replace("W", ""), 10);

  var first = new Date(yr, mo - 1, 1);
  var firstWd = (first.getDay() + 6) % 7; // 0=Mon..6=Sun
  var activeCols = [];
  for (var dow = 0; dow < 7; dow++) {
    var dt = new Date(yr, mo - 1, 1 - firstWd + (wk - 1) * 7 + dow);
    if (dt.getMonth() === (mo - 1)) activeCols.push(dow);
  }

  var activeRows = [];
  var completed = 0;
  var bestStreak = 0;
  for (var i = 0; i < HT_N_HABITS_MOB; i++) {
    if (String(namesArr[i][0] || "").trim() !== "") {
      activeRows.push(i);
      var run = 0;
      for (var k = 0; k < activeCols.length; k++) {
        if (isChecked_(gridArr[i][activeCols[k]])) {
          completed++;
          run++;
          if (run > bestStreak) bestStreak = run;
        } else {
          run = 0;
        }
      }
    }
  }

  var target = activeRows.length * activeCols.length;
  var grown = 0;
  var perfect = 0;
  var thr3 = getGrownThreshold_(ss);
  if (activeRows.length > 0) {
    for (var cIdx = 0; cIdx < activeCols.length; cIdx++) {
      var colD = activeCols[cIdx];
      var dCnt = 0;
      for (var a = 0; a < activeRows.length; a++) {
        if (isChecked_(gridArr[activeRows[a]][colD])) dCnt++;
      }
      var pct = dCnt / activeRows.length;
      if (pct >= thr3 - 1e-6) grown++;
      if (pct >= 0.999) perfect++;
    }
  }

  var sumRow = [[saveKey, yr, mo, wk, completed, target, grown, perfect, bestStreak]];
  var sRow = findSummaryRow_(wsDb, 13, saveKey);
  if (sRow === 0) sRow = getLastRowInCol_(wsDb, 13) + 1;
  wsDb.getRange(sRow, 13, 1, 9).setValues(sumRow);
}

function handleMobileGoalsSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldYr = parseInt(wsCalc.getRange("E15").getValue(), 10) || 0;
  var newYr = parseInt(ws.getRange("E3").getValue(), 10) || 0;
  if (newYr < 2000 || newYr > 2100 || oldYr === newYr) return;

  if (oldYr >= 2000) {
    var curChk = ws.getRange("B11:B22").getValues();
    var curTxt = ws.getRange("C11:C22").getValues();
    var block = [];
    var gDone = 0;
    var gTot = 0;
    for (var r = 0; r < HT_N_GOALS_MOB; r++) {
      var cVal = isChecked_(curChk[r][0]);
      var tVal = curTxt[r][0];
      if (String(tVal || "").trim() !== "") {
        gTot++;
        if (cVal) gDone++;
      }
      block.push([oldYr, r + 1, cVal, tVal]);
    }
    var dstR = findBlockRow_(wsDb, 23, String(oldYr), HT_N_GOALS_MOB);
    if (dstR === 0) dstR = getLastRowInCol_(wsDb, 23) + 1;
    wsDb.getRange(dstR, 23, HT_N_GOALS_MOB, 4).setValues(block);

    var sR = findSummaryRow_(wsDb, 28, String(oldYr));
    if (sR === 0) sR = getLastRowInCol_(wsDb, 28) + 1;
    wsDb.getRange(sR, 28, 1, 3).setValues([[oldYr, gDone, gTot]]);
  }

  var srcR = findBlockRow_(wsDb, 23, String(newYr), HT_N_GOALS_MOB);
  var loadChk = [];
  var loadTxt = [];
  if (srcR > 0) {
    var srcBlock = wsDb.getRange(srcR, 23, HT_N_GOALS_MOB, 4).getValues();
    for (var i = 0; i < HT_N_GOALS_MOB; i++) {
      loadChk.push([isChecked_(srcBlock[i][2])]);
      loadTxt.push([srcBlock[i][3]]);
    }
  } else {
    for (var j = 0; j < HT_N_GOALS_MOB; j++) {
      loadChk.push([false]);
      loadTxt.push([""]);
    }
  }
  ws.getRange("B11:B22").setValues(loadChk);
  ws.getRange("C11:C22").setValues(loadTxt);
  wsCalc.getRange("E15").setValue(newYr);
  SpreadsheetApp.flush();
}

// ============================================================================
//  DESKTOP 4-TAB PERSISTENCE ENGINE (YYYY-MM & YYYY)
// ============================================================================
function handleDesktopMonthlySwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldKey = String(wsCalc.getRange("AN2").getValue() || "").trim();
  var newMo = HT_MONTHS[String(ws.getRange("B3").getValue() || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(ws.getRange("B5").getValue(), 10) || 0;
  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;

  var newKey = pad4_(newYr) + "-" + pad2_(newMo);
  if (oldKey === newKey) return;

  if (oldKey.length === 7 && oldKey.charAt(4) === "-") {
    var curNames = ws.getRange("B17:B36").getValues();
    var curGoals = ws.getRange("AI17:AI36").getValues();
    var curGrid = ws.getRange("C17:AG36").getValues();
    saveDesktopMonthToDb_(ss, wsDb, oldKey, curNames, curGoals, curGrid);
  }

  var srcRow = findBlockRow_(wsDb, 1, newKey, HT_N_HABITS_DESK);
  var loadGrid = [];
  if (srcRow > 0) {
    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_DESK, 35).getValues();
    var loadNames = [];
    var loadGoals = [];
    var hasAnyName = false;
    for (var r = 0; r < HT_N_HABITS_DESK; r++) {
      var nm = srcBlock[r][2];
      if (String(nm || "").trim() !== "") hasAnyName = true;
      loadNames.push([nm]);
      loadGoals.push([srcBlock[r][3]]);
      var rowOut = [];
      for (var d = 0; d < 31; d++) rowOut.push(isChecked_(srcBlock[r][4 + d]));
      loadGrid.push(rowOut);
    }
    if (hasAnyName) {
      ws.getRange("B17:B36").setValues(loadNames);
      ws.getRange("AI17:AI36").setValues(loadGoals);
    }
    ws.getRange("C17:AG36").setValues(loadGrid);
  } else {
    for (var r2 = 0; r2 < HT_N_HABITS_DESK; r2++) {
      var blankRow = [];
      for (var d2 = 0; d2 < 31; d2++) blankRow.push(false);
      loadGrid.push(blankRow);
    }
    ws.getRange("C17:AG36").setValues(loadGrid);
  }

  wsCalc.getRange("AN2").setValue(newKey);
  SpreadsheetApp.flush();
}

function saveDesktopMonthToDb_(ss, wsDb, saveKey, namesArr, goalsArr, gridArr) {
  var rawBlock = [];
  for (var r = 0; r < HT_N_HABITS_DESK; r++) {
    var row = [saveKey, r + 1, namesArr[r][0], goalsArr[r][0]];
    for (var d = 0; d < 31; d++) row.push(isChecked_(gridArr[r][d]));
    rawBlock.push(row);
  }
  var dstRow = findBlockRow_(wsDb, 1, saveKey, HT_N_HABITS_DESK);
  if (dstRow === 0) dstRow = getLastRowInCol_(wsDb, 1) + 1;
  wsDb.getRange(dstRow, 1, HT_N_HABITS_DESK, 35).setValues(rawBlock);

  var yr = parseInt(saveKey.substring(0, 4), 10);
  var mo = parseInt(saveKey.substring(5, 7), 10);
  var dimDays = new Date(yr, mo, 0).getDate();

  var activeRows = [];
  var totalDone = 0;
  var totalGoal = 0;
  var bestStreak = 0;
  for (var i = 0; i < HT_N_HABITS_DESK; i++) {
    if (String(namesArr[i][0] || "").trim() !== "") {
      activeRows.push(i);
      var gVal = Number(goalsArr[i][0]);
      totalGoal += (gVal > 0) ? Math.min(gVal, dimDays) : dimDays;
      var run = 0;
      for (var k = 0; k < dimDays; k++) {
        if (isChecked_(gridArr[i][k])) {
          totalDone++;
          run++;
          if (run > bestStreak) bestStreak = run;
        } else {
          run = 0;
        }
      }
    }
  }

  var grownDays = 0;
  var perfectDays = 0;
  var thr3 = getGrownThreshold_(ss);
  if (activeRows.length > 0) {
    for (var dayIdx = 0; dayIdx < dimDays; dayIdx++) {
      var doneDay = 0;
      for (var a = 0; a < activeRows.length; a++) {
        if (isChecked_(gridArr[activeRows[a]][dayIdx])) doneDay++;
      }
      var pct = doneDay / activeRows.length;
      if (pct >= thr3 - 1e-6) grownDays++;
      if (pct >= 0.999) perfectDays++;
    }
  }

  var overall = totalGoal > 0 ? Math.min(1, totalDone / totalGoal) : 0;
  var sumRow = [[saveKey, yr, mo, totalDone, totalGoal, overall, grownDays, perfectDays, bestStreak]];
  var sRow = findSummaryRow_(wsDb, 37, saveKey);
  if (sRow === 0) sRow = getLastRowInCol_(wsDb, 37) + 1;
  wsDb.getRange(sRow, 37, 1, 9).setValues(sumRow);
}

function handleDesktopYearlyGoalsSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldYr = parseInt(wsCalc.getRange("AN3").getValue(), 10) || 0;
  var newYr = parseInt(ws.getRange("I2").getValue(), 10) || 0;
  if (newYr < 2000 || newYr > 2100 || oldYr === newYr) return;

  if (oldYr >= 2000) {
    var curYG = ws.getRange("B6:F25").getValues();
    var ygBlock = [];
    var gDone = 0;
    var gTot = 0;
    for (var r = 0; r < HT_N_GOALS_DESK; r++) {
      var chk = isChecked_(curYG[r][0]);
      var gTxt = curYG[r][1];
      if (String(gTxt || "").trim() !== "") {
        gTot++;
        if (chk) gDone++;
      }
      ygBlock.push([oldYr, r + 1, chk, gTxt, curYG[r][2], curYG[r][3], curYG[r][4]]);
    }
    var dstR = findBlockRow_(wsDb, 47, String(oldYr), HT_N_GOALS_DESK);
    if (dstR === 0) dstR = getLastRowInCol_(wsDb, 47) + 1;
    wsDb.getRange(dstR, 47, HT_N_GOALS_DESK, 7).setValues(ygBlock);

    var sR = findSummaryRow_(wsDb, 55, String(oldYr));
    if (sR === 0) sR = getLastRowInCol_(wsDb, 55) + 1;
    wsDb.getRange(sR, 55, 1, 3).setValues([[oldYr, gDone, gTot]]);
  }

  var srcR = findBlockRow_(wsDb, 47, String(newYr), HT_N_GOALS_DESK);
  var loadYG = [];
  if (srcR > 0) {
    var srcBlock = wsDb.getRange(srcR, 47, HT_N_GOALS_DESK, 7).getValues();
    for (var i = 0; i < HT_N_GOALS_DESK; i++) {
      loadYG.push([isChecked_(srcBlock[i][2]), srcBlock[i][3], srcBlock[i][4], srcBlock[i][5], srcBlock[i][6]]);
    }
  } else {
    for (var j = 0; j < HT_N_GOALS_DESK; j++) loadYG.push([false, "", "", "", ""]);
  }
  ws.getRange("B6:F25").setValues(loadYG);
  wsCalc.getRange("AN3").setValue(newYr);
  SpreadsheetApp.flush();
}

// ============================================================================
//  SHARED HELPERS
// ============================================================================
function findSheetContaining_(ss, substr) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName().indexOf(substr) !== -1) return sheets[i];
  }
  return null;
}

function findDesktopTrackerSheet_(ss) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    var n = sheets[i].getName();
    if (n !== HT_CALC_SHEET && n !== HT_DB_SHEET &&
        n.indexOf("Hướng Dẫn") === -1 &&
        n.indexOf("Yearly Goals") === -1 &&
        n.indexOf("Tổng Kết") === -1) {
      return sheets[i];
    }
  }
  return null;
}

function getGrownThreshold_(ss) {
  try {
    var nr = ss.getRangeByName("CFG_THR_3");
    if (nr) {
      var tv = Number(nr.getValue());
      if (tv > 0 && tv <= 1) return tv;
    }
  } catch (err) {}
  return 0.75;
}

function hideIfExists_(ss, name) {
  var s = ss.getSheetByName(name);
  if (s && !s.isSheetHidden()) s.hideSheet();
}

function isChecked_(v) {
  return v === true || String(v).toUpperCase() === "TRUE" || String(v).trim() === "✓";
}

function pad2_(n) { return (n < 10 ? "0" : "") + n; }
function pad4_(n) { return String(n); }

function getLastRowInCol_(ws, col) {
  var maxR = ws.getLastRow();
  if (maxR < 1) return 1;
  var vals = ws.getRange(1, col, maxR, 1).getValues();
  for (var i = vals.length - 1; i >= 0; i--) {
    if (String(vals[i][0] || "").trim() !== "") return i + 1;
  }
  return 1;
}

function findBlockRow_(wsDb, keyCol, targetKey, blockSize) {
  var lastR = getLastRowInCol_(wsDb, keyCol);
  if (lastR < 2) return 0;
  var vals = wsDb.getRange(2, keyCol, lastR - 1, 1).getValues();
  for (var i = 0; i < vals.length; i += blockSize) {
    if (String(vals[i][0]).trim() === targetKey) return i + 2;
  }
  return 0;
}

function findSummaryRow_(wsDb, keyCol, targetKey) {
  var lastR = getLastRowInCol_(wsDb, keyCol);
  if (lastR < 2) return 0;
  var vals = wsDb.getRange(2, keyCol, lastR - 1, 1).getValues();
  for (var i = 0; i < vals.length; i++) {
    if (String(vals[i][0]).trim() === targetKey) return i + 2;
  }
  return 0;
}

function convertBooleanCellsInRange_(sheet, a1Range, accent) {
  var rng = sheet.getRange(a1Range);
  var vals = rng.getValues();
  var r0 = rng.getRow();
  var c0 = rng.getColumn();
  for (var r = 0; r < vals.length; r++) {
    for (var c = 0; c < vals[r].length; c++) {
      if (typeof vals[r][c] === "boolean") {
        var cell = sheet.getRange(r0 + r, c0 + c);
        cell.insertCheckboxes();
        cell.setValue(vals[r][c]);
        cell.setFontColor(accent);
        cell.setHorizontalAlignment("center");
        cell.setVerticalAlignment("middle");
      }
    }
  }
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("✨ Habit Tracker v2.3")
    .addItem("☑️ Bật Checkbox & Tự Lưu _Database (1-Click)", "setupHabitTracker")
    .addToUi();
}
