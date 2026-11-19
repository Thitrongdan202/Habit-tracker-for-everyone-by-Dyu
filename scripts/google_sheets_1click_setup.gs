/**
 * ============================================================================
 *  HABIT TRACKER v2.1 — 1-CLICK GOOGLE SHEETS CHECKBOX + 12-MONTH AUTO-SAVE
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  HƯỚNG DẪN CÀI ĐẶT 1 LẦN (10 GIÂY):
 *    1. Tải file `.xlsx` trong `templates/google_sheets_edition/` lên Google Drive
 *       -> Mở bằng Google Trang tính (Google Sheets) -> Tệp -> Lưu dưới dạng Google Trang tính.
 *    2. Mở menu: Tiện ích mở rộng (Extensions) -> Apps Script.
 *    3. Xóa mã mặc định, dán toàn bộ đoạn code này vào và nhấn Lưu (Ctrl+S).
 *    4. Chọn hàm `setupHabitTracker` trên thanh công cụ -> nhấn Run (Chạy) -> cấp quyền 1 lần.
 *
 *  KẾT QUẢ:
 *    ✅ Gọn đúng 4 tab hiển thị (`📖 Hướng Dẫn`, `Monthly Tracker`, `🎯 Yearly Goals`, `🏆 Tổng Kết Năm`)!
 *    ✅ Biến toàn bộ vùng tick `TRUE/FALSE` thành Checkbox gốc màu Pastel trong 1 giây!
 *    ✅ Tự động kích hoạt `onEdit(e)`: mỗi khi đổi dropdown Tháng (B3) / Năm (B5) hoặc Năm Mục Tiêu (I2),
 *       dữ liệu tháng cũ TỰ ĐỘNG lưu vào `_Database` và nạp tháng mới (tháng chưa dùng mở trắng tinh!).
 */

var HT_CALC_SHEET = "_Calc";
var HT_DB_SHEET = "_Database";
var HT_N_HABITS = 20;
var HT_N_GOALS = 20;

var HT_MONTHS = {
  january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,
  july: 7, august: 8, september: 9, october: 10, november: 11, december: 12
};

function setupHabitTracker() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tracker = findTrackerSheet_(ss);
  var yg = findYearlyGoalsSheet_(ss);
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

    // Optional Rainbow Weekly Habits checkboxes (rows 48..54) if present
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

  // Ensure helper sheets remain cleanly hidden
  hideIfExists_(ss, HT_CALC_SHEET);
  hideIfExists_(ss, HT_DB_SHEET);

  SpreadsheetApp.flush();
  ss.toast(
    "Đã bật Checkbox gốc cho " + converted + " bảng + kích hoạt tự động lưu/nạp 12 tháng vào _Database!",
    "Habit Tracker v2.1 — Sẵn sàng ✨",
    8
  );
}

/**
 * Simple Trigger: automatically runs whenever the user changes Month (B3) / Year (B5)
 * on the Monthly Tracker sheet OR Year (I2) on `🎯 Yearly Goals & Habits`!
 */
function onEdit(e) {
  if (!e || !e.range) return;
  var sh = e.range.getSheet();
  var a1 = e.range.getA1Notation();
  var name = sh.getName();

  if (name === HT_CALC_SHEET || name === HT_DB_SHEET || name.indexOf("Hướng Dẫn") !== -1 || name.indexOf("Tổng Kết") !== -1) {
    return;
  }

  if (name.indexOf("Yearly Goals") !== -1) {
    if (a1 === "I2") {
      handleYearlyGoalsSwitch_(e.source, sh);
    }
    return;
  }

  // Monthly Tracker sheet (B3 = Month dropdown, B5 = Year dropdown)
  if (a1 === "B3" || a1 === "B5") {
    handleMonthlySwitch_(e.source, sh);
  }
}

function handleMonthlySwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldKey = String(wsCalc.getRange("AN2").getValue() || "").trim();
  var newMoName = String(ws.getRange("B3").getValue() || "").trim().toLowerCase();
  var newMo = HT_MONTHS[newMoName] || 0;
  var newYr = parseInt(ws.getRange("B5").getValue(), 10) || 0;
  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;

  var newKey = pad4_(newYr) + "-" + pad2_(newMo);
  if (oldKey === newKey) return;

  // 1) Save current month grid + habit names + goals into _Database under oldKey
  if (oldKey.length === 7 && oldKey.charAt(4) === "-") {
    var curNames = ws.getRange("B17:B36").getValues();
    var curGoals = ws.getRange("AI17:AI36").getValues();
    var curGrid = ws.getRange("C17:AG36").getValues();
    saveMonthToDb_(ss, wsDb, oldKey, curNames, curGoals, curGrid);
  }

  // 2) Load newKey from _Database (or reset grid cleanly to all FALSE!)
  var srcRow = findBlockRow_(wsDb, 1, newKey);
  var loadGrid = [];
  if (srcRow > 0) {
    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS, 35).getValues();
    var loadNames = [];
    var loadGoals = [];
    var hasAnyName = false;
    for (var r = 0; r < HT_N_HABITS; r++) {
      var nm = srcBlock[r][2];
      if (String(nm || "").trim() !== "") hasAnyName = true;
      loadNames.push([nm]);
      loadGoals.push([srcBlock[r][3]]);
      var rowOut = [];
      for (var d = 0; d < 31; d++) {
        rowOut.push(isChecked_(srcBlock[r][4 + d]));
      }
      loadGrid.push(rowOut);
    }
    if (hasAnyName) {
      ws.getRange("B17:B36").setValues(loadNames);
      ws.getRange("AI17:AI36").setValues(loadGoals);
    }
    ws.getRange("C17:AG36").setValues(loadGrid);
  } else {
    for (var r2 = 0; r2 < HT_N_HABITS; r2++) {
      var blankRow = [];
      for (var d2 = 0; d2 < 31; d2++) blankRow.push(false);
      loadGrid.push(blankRow);
    }
    ws.getRange("C17:AG36").setValues(loadGrid);
  }

  wsCalc.getRange("AN2").setValue(newKey);
  SpreadsheetApp.flush();
}

function saveMonthToDb_(ss, wsDb, saveKey, namesArr, goalsArr, gridArr) {
  var rawBlock = [];
  for (var r = 0; r < HT_N_HABITS; r++) {
    var row = [saveKey, r + 1, namesArr[r][0], goalsArr[r][0]];
    for (var d = 0; d < 31; d++) {
      row.push(isChecked_(gridArr[r][d]));
    }
    rawBlock.push(row);
  }

  var dstRow = findBlockRow_(wsDb, 1, saveKey);
  if (dstRow === 0) {
    dstRow = getLastRowInCol_(wsDb, 1) + 1;
  }
  wsDb.getRange(dstRow, 1, HT_N_HABITS, 35).setValues(rawBlock);

  // Compute MonthlySummary in-memory (Cols AK:AS = 37..45)
  var yr = parseInt(saveKey.substring(0, 4), 10);
  var mo = parseInt(saveKey.substring(5, 7), 10);
  var dimDays = new Date(yr, mo, 0).getDate();

  var activeRows = [];
  var totalDone = 0;
  var totalGoal = 0;
  var bestStreak = 0;

  for (var i = 0; i < HT_N_HABITS; i++) {
    var nm = String(namesArr[i][0] || "").trim();
    if (nm !== "") {
      activeRows.push(i);
      var gVal = Number(goalsArr[i][0]);
      var effGoal = (gVal > 0) ? Math.min(gVal, dimDays) : dimDays;
      totalGoal += effGoal;
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
  var thr3 = 0.75;
  try {
    var nr = ss.getRangeByName("CFG_THR_3");
    if (nr) {
      var tv = Number(nr.getValue());
      if (tv > 0 && tv <= 1) thr3 = tv;
    }
  } catch (err) {}

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

function handleYearlyGoalsSwitch_(ss, ws) {
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
    for (var r = 0; r < HT_N_GOALS; r++) {
      var chk = isChecked_(curYG[r][0]);
      var gTxt = curYG[r][1];
      if (String(gTxt || "").trim() !== "") {
        gTot++;
        if (chk) gDone++;
      }
      ygBlock.push([oldYr, r + 1, chk, gTxt, curYG[r][2], curYG[r][3], curYG[r][4]]);
    }
    var dstR = findBlockRow_(wsDb, 47, String(oldYr));
    if (dstR === 0) dstR = getLastRowInCol_(wsDb, 47) + 1;
    wsDb.getRange(dstR, 47, HT_N_GOALS, 7).setValues(ygBlock);

    var sR = findSummaryRow_(wsDb, 55, String(oldYr));
    if (sR === 0) sR = getLastRowInCol_(wsDb, 55) + 1;
    wsDb.getRange(sR, 55, 1, 3).setValues([[oldYr, gDone, gTot]]);
  }

  var srcR = findBlockRow_(wsDb, 47, String(newYr));
  var loadYG = [];
  if (srcR > 0) {
    var srcBlock = wsDb.getRange(srcR, 47, HT_N_GOALS, 7).getValues();
    for (var i = 0; i < HT_N_GOALS; i++) {
      loadYG.push([isChecked_(srcBlock[i][2]), srcBlock[i][3], srcBlock[i][4], srcBlock[i][5], srcBlock[i][6]]);
    }
  } else {
    for (var j = 0; j < HT_N_GOALS; j++) {
      loadYG.push([false, "", "", "", ""]);
    }
  }
  ws.getRange("B6:F25").setValues(loadYG);
  wsCalc.getRange("AN3").setValue(newYr);
  SpreadsheetApp.flush();
}

// ---- Helpers ---------------------------------------------------------------
function findTrackerSheet_(ss) {
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

function findYearlyGoalsSheet_(ss) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName().indexOf("Yearly Goals") !== -1) return sheets[i];
  }
  return null;
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

function findBlockRow_(wsDb, keyCol, targetKey) {
  var lastR = getLastRowInCol_(wsDb, keyCol);
  if (lastR < 2) return 0;
  var vals = wsDb.getRange(2, keyCol, lastR - 1, 1).getValues();
  for (var i = 0; i < vals.length; i += HT_N_HABITS) {
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
    .createMenu("✨ Habit Tracker v2.1")
    .addItem("☑️ Bật Checkbox & Lưu 12 Tháng (1-Click)", "setupHabitTracker")
    .addToUi();
}
