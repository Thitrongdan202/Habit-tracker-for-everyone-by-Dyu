/**
 * ============================================================================
 *  HABIT TRACKER v3.8 TURBO — 1-CLICK GOOGLE SHEETS CHECKBOX + FAST AUTO-SAVE
 *  AUTO-DETECTS BOTH:
 *    - Desktop 5-Tab Google Sheets Edition (`templates/google_sheets_edition/`)
 *    - Mobile Portrait Edition (`templates/mobile_portrait_sheets/`)
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  v3.8 TURBO PERFORMANCE UPGRADES (6, 7 & 8-Stage Digimon Compatible):
 *    - Single-pass O(1) index map (`buildColIndex_`) -> 1 RPC instead of 4-6 scans!
 *    - Batched multi-column `getValues()` / `setValues()` (B17:AI36, B3:B5, D5:F5, B21:I35)
 *    - RangeList bulk checkbox insertion in `convertBooleanCellsInRange_`
 *    - Zero redundant `SpreadsheetApp.flush()` calls
 *
 *  HƯỚNG DẪN CÀI ĐẶT 1 LẦN (10 GIÂY):
 *    1. Tải file `.xlsx` lên Google Drive -> Mở bằng Google Trang tính (Google Sheets)
 *       -> Tệp (File) -> Lưu dưới dạng Google Trang tính (Save as Google Sheets).
 *    2. Mở menu: Tiện ích mở rộng (Extensions) -> Apps Script.
 *    3. Xóa mã mặc định, dán toàn bộ đoạn code này vào và nhấn Lưu (Ctrl+S).
 *    4. Chọn hàm `setupHabitTracker` trên thanh công cụ -> nhấn Run (Chạy) -> cấp quyền 1 lần.
 */

var HT_CALC_SHEET = "_Calc";
var HT_DB_SHEET = "_Database";
var HT_N_HABITS_DESK = 20;
var HT_N_GOALS_DESK = 20;
var HT_N_TASKS_DESK = 20;
var HT_N_HABITS_MOB = 15;
var HT_N_GOALS_MOB = 12;
var HT_N_TASKS_MOB = 15;

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

function applyPastelCheckboxes_(rng, accent, fontSize) {
  var vals = rng.getValues();
  rng.insertCheckboxes()
    .setValues(vals)
    .setFontColor(accent)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
  if (fontSize) rng.setFontSize(fontSize);
}

function setupMobilePortrait_(ss) {
  var wsWk = findSheetContaining_(ss, "Tuần Này");
  var wsDt = findSheetContaining_(ss, "Việc Hôm Nay");
  var wsGo = findSheetContaining_(ss, "Mục Tiêu");
  var converted = 0;

  if (wsWk) {
    applyPastelCheckboxes_(wsWk.getRange("C21:I35"), wsWk.getRange("B2").getBackground() || "#C88E8E", 14);
    converted++;
  }
  if (wsDt) {
    applyPastelCheckboxes_(wsDt.getRange("B16:B30"), wsDt.getRange("B2").getBackground() || "#B57A7A", 14);
    converted++;
  }
  if (wsGo) {
    applyPastelCheckboxes_(wsGo.getRange("B11:B22"), wsGo.getRange("B2").getBackground() || "#B57A7A", 14);
    converted++;
  }

  hideIfExists_(ss, HT_CALC_SHEET);
  hideIfExists_(ss, HT_DB_SHEET);
  SpreadsheetApp.flush();
  ss.toast(
    "Bản Điện Thoại (Mobile Portrait v3.8 Turbo): Đã bật Checkbox Pastel cho " + converted + " bảng & tối ưu tốc độ lưu Tuần/Ngày/Năm!",
    "Habit Tracker Mobile v3.8 — Sẵn sàng 📱⚡",
    8
  );
}

function setupDesktopEdition_(ss) {
  var tracker = findDesktopTrackerSheet_(ss);
  var dt = findSheetContaining_(ss, "Nhiệm Vụ Ngày");
  var yg = findSheetContaining_(ss, "Yearly Goals");
  var converted = 0;

  if (tracker) {
    var accent = tracker.getRange("B14").getBackground() || "#C88E8E";
    applyPastelCheckboxes_(tracker.getRange("C17:AG36"), accent, 0);
    converted++;

    var maxR = tracker.getMaxRows();
    if (maxR >= 54) {
      var probe = String(tracker.getRange("B47").getValue() || "");
      if (probe.toUpperCase().indexOf("WEEKLY") !== -1) {
        convertBooleanCellsInRange_(tracker, "C48:AG54", accent);
      }
    }
    if (maxR >= 46) {
      var probePlum = String(tracker.getRange("B39").getValue() || "");
      if (probePlum.toUpperCase().indexOf("WEEKLY") !== -1) {
        convertBooleanCellsInRange_(tracker, "G41:AC46", accent);
      }
    }
  }

  if (dt) {
    applyPastelCheckboxes_(dt.getRange("B9:B28"), dt.getRange("B2").getBackground() || "#B57A7A", 0);
    converted++;
  }

  if (yg) {
    applyPastelCheckboxes_(yg.getRange("B6:B25"), yg.getRange("B2").getBackground() || "#B57A7A", 0);
    converted++;
  }

  hideIfExists_(ss, HT_CALC_SHEET);
  hideIfExists_(ss, HT_DB_SHEET);
  SpreadsheetApp.flush();
  ss.toast(
    "Bản Desktop v3.8 Turbo: Đã bật Checkbox Pastel cho " + converted + " bảng & kích hoạt bộ máy lưu O(1) siêu tốc!",
    "Habit Tracker v3.8 Turbo — Sẵn sàng ⚡✨",
    8
  );
}

/**
 * Fast Simple Trigger: instant O(1) range-guard exit on normal checkbox ticks (0 extra RPCs!).
 */
function onEdit(e) {
  if (!e || !e.range) return;
  var row = e.range.getRow();
  var col = e.range.getColumn();
  // Fast-path exit: dropdown selectors ONLY live in rows 2, 3, or 5!
  // Any checkbox tick (row >= 6) exits in < 1ms with ZERO Spreadsheet API calls!
  if (row > 5 || row < 2) return;

  var sh = e.range.getSheet();
  var name = sh.getName();
  if (name === HT_CALC_SHEET || name === HT_DB_SHEET ||
      name.indexOf("Hướng Dẫn") !== -1 || name.indexOf("Tổng Kết") !== -1) return;

  var ss = e.source;
  if (name.indexOf("Tuần Này") !== -1) {
    if (row === 5 && (col === 2 || col === 3 || col === 6)) {
      handleMobileWeekSwitch_(ss, sh);
    }
    return;
  }
  if (name.indexOf("Việc Hôm Nay") !== -1) {
    if (row === 5 && (col === 2 || col === 3 || col === 7)) {
      handleMobileDailyTasksSwitch_(ss, sh);
    }
    return;
  }
  if (name.indexOf("Mục Tiêu") !== -1) {
    if (row === 3 && col === 5) {
      handleMobileGoalsSwitch_(ss, sh);
    }
    return;
  }
  if (name.indexOf("Nhiệm Vụ Ngày") !== -1) {
    if (row === 5 && col >= 4 && col <= 6) {
      handleDesktopDailyTasksSwitch_(ss, sh);
    }
    return;
  }
  if (name.indexOf("Yearly Goals") !== -1) {
    if (row === 2 && col === 9) {
      handleDesktopYearlyGoalsSwitch_(ss, sh);
    }
    return;
  }
  // Monthly Tracker dropdowns: B3 (row 3, col 2) or B5 (row 5, col 2)
  if (col === 2 && (row === 3 || row === 5)) {
    handleDesktopMonthlySwitch_(ss, sh);
  }
}

// ============================================================================
//  O(1) SINGLE-PASS `_Database` COLUMN INDEXER (1 RPC PER TABLE!)
// ============================================================================
function buildColIndex_(wsDb, keyCol, blockSize) {
  var maxR = wsDb.getLastRow();
  var map = Object.create(null);
  if (maxR < 2) return { map: map, nextRow: 2 };

  var vals = wsDb.getRange(2, keyCol, maxR - 1, 1).getValues();
  var lastNonEmpty = 1;
  for (var i = 0; i < vals.length; i++) {
    var k = keyStr_(vals[i][0]);
    if (k !== "") {
      lastNonEmpty = i + 2;
      if (i % blockSize === 0 && map[k] === undefined) {
        map[k] = i + 2;
      }
    }
  }
  return { map: map, nextRow: lastNonEmpty + 1 };
}

// ============================================================================
//  MOBILE PORTRAIT PERSISTENCE ENGINE (YYYY-MM-W# & YYYY — BATCHED O(1))
// ============================================================================
function parseWeekNum_(raw) {
  var m = String(raw || "").match(/(\d+)/);
  return m ? parseInt(m[1], 10) : 0;
}

function handleMobileWeekSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  // 1 batched read for Month (B5), Year (C5), Week (F5)
  var sel = ws.getRange("B5:F5").getValues()[0];
  var oldKey = keyStr_(wsCalc.getRange("E14").getValue());
  var newMo = HT_MONTHS[String(sel[0] || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(sel[1], 10) || 0;
  var newWk = parseWeekNum_(sel[4]);
  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100 || newWk < 1 || newWk > 5) return;

  var newKey = pad4_(newYr) + "-" + pad2_(newMo) + "-W" + newWk;
  if (oldKey === newKey) return;

  // Single-pass O(1) index for BOTH save & load!
  var wkIdx = buildColIndex_(wsDb, 1, HT_N_HABITS_MOB);

  // 1) Batch-read B21:I35 (names col 0 + 7-day grid cols 1..7) in ONE RPC!
  var curAll = ws.getRange("B21:I35").getValues();
  if (oldKey.indexOf("-W") !== -1) {
    saveMobileWeekToDb_(ss, wsDb, wkIdx, oldKey, curAll);
  }

  // 2) O(1) load newKey
  var srcRow = wkIdx.map[newKey] || 0;
  var loadGrid = [];
  if (srcRow > 0) {
    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_MOB, 10).getValues();
    var loadNames = [];
    var hasAny = false;
    var namesChanged = false;
    for (var r = 0; r < HT_N_HABITS_MOB; r++) {
      var nm = srcBlock[r][2];
      if (String(nm || "").trim() !== "") hasAny = true;
      if (String(curAll[r][0] || "") !== String(nm || "")) namesChanged = true;
      loadNames.push([nm]);
      var rowOut = [];
      for (var d = 0; d < 7; d++) rowOut.push(isChecked_(srcBlock[r][3 + d]));
      loadGrid.push(rowOut);
    }
    if (hasAny && namesChanged) ws.getRange("B21:B35").setValues(loadNames);
    ws.getRange("C21:I35").setValues(loadGrid);
  } else {
    for (var r2 = 0; r2 < HT_N_HABITS_MOB; r2++) {
      loadGrid.push([false, false, false, false, false, false, false]);
    }
    ws.getRange("C21:I35").setValues(loadGrid);
  }

  wsCalc.getRange("E14").setValue(newKey);
}

function saveMobileWeekToDb_(ss, wsDb, wkIdx, saveKey, curAll) {
  var rawBlock = [];
  for (var r = 0; r < HT_N_HABITS_MOB; r++) {
    var row = [saveKey, r + 1, curAll[r][0]];
    for (var d = 0; d < 7; d++) row.push(isChecked_(curAll[r][1 + d]));
    rawBlock.push(row);
  }
  var dstRow = wkIdx.map[saveKey] || 0;
  if (dstRow === 0) {
    dstRow = wkIdx.nextRow;
    wkIdx.map[saveKey] = dstRow;
    wkIdx.nextRow += HT_N_HABITS_MOB;
  }
  wsDb.getRange(dstRow, 1, HT_N_HABITS_MOB, 10).setValues(rawBlock);

  var parts = saveKey.split("-");
  var yr = parseInt(parts[0], 10);
  var mo = parseInt(parts[1], 10);
  var wk = parseInt(parts[2].replace("W", ""), 10);

  var first = new Date(yr, mo - 1, 1);
  var firstWd = (first.getDay() + 6) % 7;
  var activeCols = [];
  for (var dow = 0; dow < 7; dow++) {
    var dt = new Date(yr, mo - 1, 1 - firstWd + (wk - 1) * 7 + dow);
    if (dt.getMonth() === (mo - 1)) activeCols.push(dow);
  }

  var activeRows = [];
  var completed = 0;
  var bestStreak = 0;
  for (var i = 0; i < HT_N_HABITS_MOB; i++) {
    if (String(curAll[i][0] || "").trim() !== "") {
      activeRows.push(i);
      var run = 0;
      for (var k = 0; k < activeCols.length; k++) {
        if (isChecked_(curAll[i][1 + activeCols[k]])) {
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
        if (isChecked_(curAll[activeRows[a]][1 + colD])) dCnt++;
      }
      var pct = dCnt / activeRows.length;
      if (pct >= thr3 - 1e-6) grown++;
      if (pct >= 0.999) perfect++;
    }
  }

  var sumIdx = buildColIndex_(wsDb, 13, 1);
  var sRow = sumIdx.map[saveKey] || sumIdx.nextRow;
  wsDb.getRange(sRow, 13, 1, 9).setValues([[saveKey, yr, mo, wk, completed, target, grown, perfect, bestStreak]]);
}

function handleMobileGoalsSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldYr = parseInt(wsCalc.getRange("E15").getValue(), 10) || 0;
  var newYr = parseInt(ws.getRange("E3").getValue(), 10) || 0;
  if (newYr < 2000 || newYr > 2100 || oldYr === newYr) return;

  var gIdx = buildColIndex_(wsDb, 23, HT_N_GOALS_MOB);

  if (oldYr >= 2000) {
    // 1 batched read for B11:C22
    var curBC = ws.getRange("B11:C22").getValues();
    var block = [];
    var gDone = 0;
    var gTot = 0;
    for (var r = 0; r < HT_N_GOALS_MOB; r++) {
      var cVal = isChecked_(curBC[r][0]);
      var tVal = curBC[r][1];
      if (String(tVal || "").trim() !== "") {
        gTot++;
        if (cVal) gDone++;
      }
      block.push([oldYr, r + 1, cVal, tVal]);
    }
    var oldKey = String(oldYr);
    var dstR = gIdx.map[oldKey] || gIdx.nextRow;
    wsDb.getRange(dstR, 23, HT_N_GOALS_MOB, 4).setValues(block);

    var sIdx = buildColIndex_(wsDb, 28, 1);
    var sR = sIdx.map[oldKey] || sIdx.nextRow;
    wsDb.getRange(sR, 28, 1, 3).setValues([[oldYr, gDone, gTot]]);
  }

  var srcR = gIdx.map[String(newYr)] || 0;
  var loadBC = [];
  if (srcR > 0) {
    var srcBlock = wsDb.getRange(srcR, 23, HT_N_GOALS_MOB, 4).getValues();
    for (var i = 0; i < HT_N_GOALS_MOB; i++) {
      loadBC.push([isChecked_(srcBlock[i][2]), srcBlock[i][3]]);
    }
  } else {
    for (var j = 0; j < HT_N_GOALS_MOB; j++) loadBC.push([false, ""]);
  }
  ws.getRange("B11:C22").setValues(loadBC);
  wsCalc.getRange("E15").setValue(newYr);
}

// ============================================================================
//  DESKTOP 5-TAB PERSISTENCE ENGINE (YYYY-MM, YYYY, YYYY-MM-DD — BATCHED O(1))
// ============================================================================
function handleDesktopMonthlySwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  // 1 batched read for B3:B5 (Month + Year)
  var sel = ws.getRange("B3:B5").getValues();
  var oldKey = keyStr_(wsCalc.getRange("AN2").getValue());
  var newMo = HT_MONTHS[String(sel[0][0] || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(sel[2][0], 10) || 0;
  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;

  var newKey = pad4_(newYr) + "-" + pad2_(newMo);
  if (oldKey === newKey) return;

  // 1 batched read for B17:AI36 (Col B=0 Name, C..AG=1..31 Grid, AH=32 Spacer, AI=33 Goal)
  var curAll = ws.getRange("B17:AI36").getValues();
  // Single-pass O(1) index for BOTH save & load!
  var mIdx = buildColIndex_(wsDb, 1, HT_N_HABITS_DESK);

  if (oldKey.length === 7 && oldKey.charAt(4) === "-") {
    saveDesktopMonthToDb_(ss, wsDb, mIdx, oldKey, curAll);
  }

  var srcRow = mIdx.map[newKey] || 0;
  var loadGrid = [];
  var gridChanged = false;
  if (srcRow > 0) {
    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_DESK, 35).getValues();
    var loadNames = [];
    var loadGoals = [];
    var hasAnyName = false;
    var namesChanged = false;
    var goalsChanged = false;
    for (var r = 0; r < HT_N_HABITS_DESK; r++) {
      var nm = srcBlock[r][2];
      var gl = srcBlock[r][3];
      if (String(nm || "").trim() !== "") hasAnyName = true;
      if (String(curAll[r][0] || "") !== String(nm || "")) namesChanged = true;
      if (String(curAll[r][33] || "") !== String(gl || "")) goalsChanged = true;
      loadNames.push([nm]);
      loadGoals.push([gl]);
      var rowOut = [];
      for (var d = 0; d < 31; d++) {
        var bVal = isChecked_(srcBlock[r][4 + d]);
        if (isChecked_(curAll[r][1 + d]) !== bVal) gridChanged = true;
        rowOut.push(bVal);
      }
      loadGrid.push(rowOut);
    }
    if (hasAnyName && namesChanged) ws.getRange("B17:B36").setValues(loadNames);
    if (hasAnyName && goalsChanged) ws.getRange("AI17:AI36").setValues(loadGoals);
    if (gridChanged) ws.getRange("C17:AG36").setValues(loadGrid);
  } else {
    for (var r2 = 0; r2 < HT_N_HABITS_DESK; r2++) {
      var blankRow = [];
      for (var d2 = 0; d2 < 31; d2++) {
        if (isChecked_(curAll[r2][1 + d2])) gridChanged = true;
        blankRow.push(false);
      }
      loadGrid.push(blankRow);
    }
    if (gridChanged) ws.getRange("C17:AG36").setValues(loadGrid);
  }

  wsCalc.getRange("AN2").setNumberFormat("@").setValue(newKey);
}

function saveDesktopMonthToDb_(ss, wsDb, mIdx, saveKey, curAll) {
  var rawBlock = [];
  for (var r = 0; r < HT_N_HABITS_DESK; r++) {
    var row = [saveKey, r + 1, curAll[r][0], curAll[r][33]];
    for (var d = 0; d < 31; d++) row.push(isChecked_(curAll[r][1 + d]));
    rawBlock.push(row);
  }
  var dstRow = mIdx.map[saveKey] || 0;
  if (dstRow === 0) {
    dstRow = mIdx.nextRow;
    mIdx.map[saveKey] = dstRow;
    mIdx.nextRow += HT_N_HABITS_DESK;
  }
  wsDb.getRange(dstRow, 1, HT_N_HABITS_DESK, 1).setNumberFormat("@");
  wsDb.getRange(dstRow, 1, HT_N_HABITS_DESK, 35).setValues(rawBlock);

  var yr = parseInt(saveKey.substring(0, 4), 10);
  var mo = parseInt(saveKey.substring(5, 7), 10);
  var dimDays = new Date(yr, mo, 0).getDate();

  var activeRows = [];
  var totalDone = 0;
  var totalGoal = 0;
  var bestStreak = 0;
  for (var i = 0; i < HT_N_HABITS_DESK; i++) {
    if (String(curAll[i][0] || "").trim() !== "") {
      activeRows.push(i);
      var gVal = Number(curAll[i][33]);
      totalGoal += (gVal > 0) ? Math.min(gVal, dimDays) : dimDays;
      var run = 0;
      for (var k = 0; k < dimDays; k++) {
        if (isChecked_(curAll[i][1 + k])) {
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
        if (isChecked_(curAll[activeRows[a]][1 + dayIdx])) doneDay++;
      }
      var pct = doneDay / activeRows.length;
      if (pct >= thr3 - 1e-6) grownDays++;
      if (pct >= 0.999) perfectDays++;
    }
  }

  var overall = totalGoal > 0 ? Math.min(1, totalDone / totalGoal) : 0;
  var sumIdx = buildColIndex_(wsDb, 37, 1);
  var sRow = sumIdx.map[saveKey] || sumIdx.nextRow;
  wsDb.getRange(sRow, 37).setNumberFormat("@");
  wsDb.getRange(sRow, 37, 1, 9).setValues([[saveKey, yr, mo, totalDone, totalGoal, overall, grownDays, perfectDays, bestStreak]]);
}

function handleDesktopYearlyGoalsSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  var oldYr = parseInt(wsCalc.getRange("AN3").getValue(), 10) || 0;
  var newYr = parseInt(ws.getRange("I2").getValue(), 10) || 0;
  if (newYr < 2000 || newYr > 2100 || oldYr === newYr) return;

  var gIdx = buildColIndex_(wsDb, 47, HT_N_GOALS_DESK);

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
    var oldKey = String(oldYr);
    var dstR = gIdx.map[oldKey] || gIdx.nextRow;
    wsDb.getRange(dstR, 47, HT_N_GOALS_DESK, 7).setValues(ygBlock);

    var sIdx = buildColIndex_(wsDb, 55, 1);
    var sR = sIdx.map[oldKey] || sIdx.nextRow;
    wsDb.getRange(sR, 55, 1, 3).setValues([[oldYr, gDone, gTot]]);
  }

  var srcR = gIdx.map[String(newYr)] || 0;
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
}

// ============================================================================
//  DAILY ONE-OFF TASKS PERSISTENCE ENGINE (YYYY-MM-DD — BATCHED O(1))
// ============================================================================
function handleDesktopDailyTasksSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  // 1 batched read for D5:F5 (Day, Month, Year)
  var sel = ws.getRange("D5:F5").getValues()[0];
  var oldKey = keyStr_(wsCalc.getRange("AN12").getValue());
  var newDay = parseInt(sel[0], 10) || 0;
  var newMo = HT_MONTHS[String(sel[1] || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(sel[2], 10) || 0;
  if (newDay < 1 || newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;

  var maxDay = new Date(newYr, newMo, 0).getDate();
  if (newDay > maxDay) {
    newDay = maxDay;
    ws.getRange("D5").setValue(newDay);
  }
  var newKey = pad4_(newYr) + "-" + pad2_(newMo) + "-" + pad2_(newDay);
  if (oldKey === newKey) return;

  var dtIdx = buildColIndex_(wsDb, 59, HT_N_TASKS_DESK);

  if (oldKey.length === 10) {
    var curTasks = ws.getRange("B9:F28").getValues();
    var curNote = ws.getRange("B31").getValue();
    var block = [];
    for (var r = 0; r < HT_N_TASKS_DESK; r++) {
      block.push([
        oldKey, r + 1, isChecked_(curTasks[r][0]), curTasks[r][1], curTasks[r][2],
        curTasks[r][3], curTasks[r][4], (r === 0 ? curNote : "")
      ]);
    }
    var dstR = dtIdx.map[oldKey] || dtIdx.nextRow;
    if (!dtIdx.map[oldKey]) {
      dtIdx.map[oldKey] = dstR;
      dtIdx.nextRow += HT_N_TASKS_DESK;
    }
    wsDb.getRange(dstR, 59, HT_N_TASKS_DESK, 1).setNumberFormat("@");
    wsDb.getRange(dstR, 59, HT_N_TASKS_DESK, 8).setValues(block);
  }

  var srcR = dtIdx.map[newKey] || 0;
  var loadTasks = [];
  var loadNote = "";
  if (srcR > 0) {
    var srcArr = wsDb.getRange(srcR, 59, HT_N_TASKS_DESK, 8).getValues();
    for (var i = 0; i < HT_N_TASKS_DESK; i++) {
      loadTasks.push([isChecked_(srcArr[i][2]), srcArr[i][3], srcArr[i][4], srcArr[i][5], srcArr[i][6]]);
    }
    loadNote = srcArr[0][7];
  } else {
    for (var j = 0; j < HT_N_TASKS_DESK; j++) {
      loadTasks.push([false, "", "", "", ""]);
    }
  }
  ws.getRange("B9:F28").setValues(loadTasks);
  ws.getRange("B31").setValue(loadNote);
  wsCalc.getRange("AN12").setNumberFormat("@").setValue(newKey);
}

function handleMobileDailyTasksSwitch_(ss, ws) {
  var wsCalc = ss.getSheetByName(HT_CALC_SHEET);
  var wsDb = ss.getSheetByName(HT_DB_SHEET);
  if (!wsCalc || !wsDb) return;

  // 1 batched read for B5:G5 (Day=0, Month=1, Year=5)
  var sel = ws.getRange("B5:G5").getValues()[0];
  var oldKey = keyStr_(wsCalc.getRange("E29").getValue());
  var newDay = parseInt(sel[0], 10) || 0;
  var newMo = HT_MONTHS[String(sel[1] || "").trim().toLowerCase()] || 0;
  var newYr = parseInt(sel[5], 10) || 0;
  if (newDay < 1 || newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;

  var maxDay = new Date(newYr, newMo, 0).getDate();
  if (newDay > maxDay) {
    newDay = maxDay;
    ws.getRange("B5").setValue(newDay);
  }
  var newKey = pad4_(newYr) + "-" + pad2_(newMo) + "-" + pad2_(newDay);
  if (oldKey === newKey) return;

  var dtIdx = buildColIndex_(wsDb, 32, HT_N_TASKS_MOB);

  if (oldKey.length === 10) {
    // 1 batched read for B16:G30 (B=0 chk, C=1 name, G=5 prio)
    var curAll = ws.getRange("B16:G30").getValues();
    var curNote = ws.getRange("B33").getValue();
    var block = [];
    for (var r = 0; r < HT_N_TASKS_MOB; r++) {
      block.push([oldKey, r + 1, isChecked_(curAll[r][0]), curAll[r][1], curAll[r][5], (r === 0 ? curNote : "")]);
    }
    var dstR = dtIdx.map[oldKey] || dtIdx.nextRow;
    if (!dtIdx.map[oldKey]) {
      dtIdx.map[oldKey] = dstR;
      dtIdx.nextRow += HT_N_TASKS_MOB;
    }
    wsDb.getRange(dstR, 32, HT_N_TASKS_MOB, 1).setNumberFormat("@");
    wsDb.getRange(dstR, 32, HT_N_TASKS_MOB, 6).setValues(block);
  }

  var srcR = dtIdx.map[newKey] || 0;
  var loadBC = [];
  var loadPr = [];
  var loadNote = "";
  if (srcR > 0) {
    var srcArr = wsDb.getRange(srcR, 32, HT_N_TASKS_MOB, 6).getValues();
    for (var i = 0; i < HT_N_TASKS_MOB; i++) {
      loadBC.push([isChecked_(srcArr[i][2]), srcArr[i][3]]);
      loadPr.push([srcArr[i][4]]);
    }
    loadNote = srcArr[0][5];
  } else {
    for (var j = 0; j < HT_N_TASKS_MOB; j++) {
      loadBC.push([false, ""]);
      loadPr.push([""]);
    }
  }
  ws.getRange("B16:C30").setValues(loadBC);
  ws.getRange("G16:G30").setValues(loadPr);
  ws.getRange("B33").setValue(loadNote);
  wsCalc.getRange("E29").setNumberFormat("@").setValue(newKey);
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
        n.indexOf("Nhiệm Vụ Ngày") === -1 &&
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

function keyStr_(v) {
  if (v instanceof Date) {
    return pad4_(v.getFullYear()) + "-" + pad2_(v.getMonth() + 1) + "-" + pad2_(v.getDate());
  }
  return String(v || "").trim();
}

function pad2_(n) { return (n < 10 ? "0" : "") + n; }
function pad4_(n) { return String(n); }

function colToLetter_(col) {
  var s = "";
  while (col > 0) {
    var rem = (col - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    col = Math.floor((col - 1) / 26);
  }
  return s;
}

function convertBooleanCellsInRange_(sheet, a1Range, accent) {
  var rng = sheet.getRange(a1Range);
  var vals = rng.getValues();
  var r0 = rng.getRow();
  var c0 = rng.getColumn();
  var a1List = [];
  for (var r = 0; r < vals.length; r++) {
    for (var c = 0; c < vals[r].length; c++) {
      if (typeof vals[r][c] === "boolean") {
        a1List.push(colToLetter_(c0 + c) + (r0 + r));
      }
    }
  }
  if (a1List.length === 0) return;
  // Bulk RangeList formatting (1 batched call instead of N cell-by-cell RPCs!)
  var rl = sheet.getRangeList(a1List);
  rl.insertCheckboxes()
    .setFontColor(accent)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
  // Restore original boolean values in ONE bulk call
  rng.setValues(vals);
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("⚡ Habit Tracker v3.8 Turbo")
    .addItem("☑️ Bật Checkbox & Tự Lưu _Database (1-Click)", "setupHabitTracker")
    .addToUi();
}
