/**
 * ============================================================================
 *  HABIT TRACKER — BOUND SIMPLE-TRIGGER `onEdit(e)` AUTO-SAVE INJECTOR
 *  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
 * ============================================================================
 *
 *  MỤC ĐÍCH:
 *    Tự động gắn trực tiếp một đoạn mã Container-Bound Simple Trigger `onEdit(e)`
 *    vào TỪNG file Google Sheets gốc trong thư mục Drive của bạn
 *    (`Habit_Tracker_Native_Google_Sheets` hoặc `Habit_Tracker_Native_Mobile_Sheets`)
 *    thông qua Apps Script REST API (`https://script.googleapis.com/v1/projects`).
 *
 *    ★ LỢI ÍCH CHO NGƯỜI DÙNG CUỐI (100% ZERO-FRICTION):
 *      - Khi người dùng bấm link `/copy`, Google Drive tự sao chép luôn `onEdit(e)`
 *        bên trong bản copy của họ!
 *      - `onEdit(e)` là Simple Trigger thuần túy (CHỈ dùng `e.source`, `e.range`,
 *        `e.value`, `e.oldValue`, `getValues()`, `setValues()`, `toast()`) ->
 *        KHÔNG cần cấp quyền OAuth, KHÔNG hiện cảnh báo "Ứng dụng chưa xác minh"!
 *      - Tick checkbox hàng ngày thoát ngay trong 0ms (0 lần ghi `_Database`).
 *      - Đổi Tháng / Năm / Ngày / Tuần tự động lưu & nạp dữ liệu từ `_Database`!
 *      - Tự nhận diện cả bản Desktop 5-Tab lẫn bản Mobile Portrait!
 *
 *  ============================================================================
 *  HƯỚNG DẪN CÀI ĐẶT 1 LẦN DUY NHẤT (CHỈ DÀNH CHO TÁC GIẢ / NGƯỜI PUBLISH)
 *  ============================================================================
 *  Bước 1 — Bật Google Apps Script API trên tài khoản Google của bạn:
 *    Truy cập: https://script.google.com/home/usersettings
 *    -> Bật (ON) mục "Google Apps Script API".
 *
 *  Bước 2 — Tạo/gắn Standard Google Cloud Platform (GCP) Project Number:
 *    1) Mở https://console.cloud.google.com/ -> Tạo 1 Project mới (vd: "HabitTrackerPublisher")
 *       -> Vào "APIs & Services" -> "Library" -> tìm "Apps Script API" -> bấm ENABLE.
 *       -> Vào "APIs & Services" -> "OAuth consent screen" -> chọn External -> điền tên app ->
 *          thêm chính email Gmail của bạn vào mục "Test users" -> Save.
 *       -> Copy **Project Number** (dãy số ở trang Dashboard của GCP).
 *    2) Trong dự án Apps Script này (https://script.google.com):
 *       Vào bánh răng "Project Settings" (Cài đặt dự án) bên trái:
 *       - Tick chọn: [x] Show "appsscript.json" manifest file in editor
 *       - Kéo xuống mục "Google Cloud Platform (GCP) Project" -> bấm "Change project"
 *         -> dán Project Number vừa copy -> bấm "Set project".
 *
 *  Bước 3 — Dán quyền (OAuth Scopes) vào file `appsscript.json` trong Editor:
 *    Mở file `appsscript.json` ở cột bên trái và thay toàn bộ bằng đoạn JSON sau:
 *    {
 *      "timeZone": "Asia/Ho_Chi_Minh",
 *      "dependencies": {},
 *      "exceptionLogging": "STACKDRIVER",
 *      "runtimeVersion": "V8",
 *      "oauthScopes": [
 *        "https://www.googleapis.com/auth/script.projects",
 *        "https://www.googleapis.com/auth/drive",
 *        "https://www.googleapis.com/auth/spreadsheets",
 *        "https://www.googleapis.com/auth/script.external_request"
 *      ]
 *    }
 *
 *  Bước 4 — Điền Folder ID & Chạy:
 *    1) Dán ID thư mục chứa các file Google Sheets đã convert vào `TARGET_FOLDER_ID` bên dưới
 *       (thư mục `Habit_Tracker_Native_Google_Sheets` hoặc `Habit_Tracker_Native_Mobile_Sheets`).
 *    2) Nhấn Lưu (Ctrl+S) -> chọn hàm `injectAutoSaveToFolder` -> bấm Run (Chạy) -> cấp quyền 1 lần.
 *    3) Script tự bỏ qua các file đã gắn (nhờ `PropertiesService` + `INJECTED_SCRIPTS_LOG.json`)
 *       và tự dừng êm ở 4.5 phút (`SOFT_LIMIT_MS = 270000`) — nếu nhiều hơn 1 đợt chỉ cần bấm Run lại!
 */

// ===================== CONFIGURATION (EDIT BEFORE RUN) =====================
var TARGET_FOLDER_ID = "PASTE_YOUR_NATIVE_SHEETS_FOLDER_ID_HERE";
var SKIP_ALREADY_INJECTED = true;
var SOFT_LIMIT_MS = 270000; // 4.5 phút (dừng an toàn trước giới hạn 6 phút của Apps Script)

var BOUND_PROJECT_TITLE = "Habit Tracker Auto-Save";
var LOG_FILE_NAME = "INJECTED_SCRIPTS_LOG.json";
var PROP_PREFIX = "INJ_SCRIPT_";

var CLEAN_HINT_TEXT = "☁️ Tự động lưu lịch sử trên Google Drive của bạn khi đổi Ngày / Tháng / Năm!";

var INJ_MONTHS = {
  january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,
  july: 7, august: 8, september: 9, october: 10, november: 11, december: 12
};

// ============================================================================
//  CONTAINER-BOUND PURE SIMPLE TRIGGER SOURCE (INJECTED AS `Code.gs`)
//  - ZERO OAuth scopes required (NO DriveApp, UrlFetchApp, ScriptApp,
//    SpreadsheetApp.openById, LockService, or PropertiesService!)
//  - 0ms fast-exit on every normal checkbox tick
//  - Auto-detects BOTH Desktop 5-Tab & Mobile Portrait layouts
//  - Smart `e.oldValue` fallback on first switch if `_Calc` key is blank
// ============================================================================
var BOUND_CODE = [
  "/**",
  " * Habit Tracker Pure Simple Trigger `onEdit(e)` — Auto-Save & Auto-Load",
  " * ZERO OAuth required: uses ONLY e.source, e.range, e.value, e.oldValue.",
  " * Supports BOTH Desktop 5-Tab & Mobile Portrait Google Sheets editions.",
  " */",
  "",
  "var HT_CALC = '_Calc';",
  "var HT_DB = '_Database';",
  "var HT_ASSETS = '_Assets';",
  "var HT_N_HABITS_DESK = 20;",
  "var HT_N_GOALS_DESK = 20;",
  "var HT_N_TASKS_DESK = 20;",
  "var HT_N_HABITS_MOB = 15;",
  "var HT_N_GOALS_MOB = 12;",
  "var HT_N_TASKS_MOB = 15;",
  "",
  "var HT_MONTHS = {",
  "  january: 1, february: 2, march: 3, april: 4, may: 5, june: 6,",
  "  july: 7, august: 8, september: 9, october: 10, november: 11, december: 12",
  "};",
  "",
  "function onEdit(e) {",
  "  if (!e || !e.range || !e.source) return;",
  "  var row = e.range.getRow();",
  "  var col = e.range.getColumn();",
  "",
  "  // 0ms fast-exit guard: normal checkbox ticks (row >= 6) exit IMMEDIATELY!",
  "  if (row < 2 || row > 5) return;",
  "  var isDropdown =",
  "    (col === 2 && (row === 3 || row === 5)) ||",
  "    (row === 5 && col >= 3 && col <= 7) ||",
  "    (row === 2 && col === 9) ||",
  "    (row === 3 && col === 5);",
  "  if (!isDropdown) return;",
  "",
  "  var sh = e.range.getSheet();",
  "  var name = sh.getName();",
  "  if (name === HT_CALC || name === HT_DB || name === HT_ASSETS ||",
  "      name.indexOf('Hướng Dẫn') !== -1 || name.indexOf('Tổng Kết') !== -1) {",
  "    return;",
  "  }",
  "",
  "  var ss = e.source;",
  "  var oldVal = (e.oldValue !== undefined && e.oldValue !== null) ? String(e.oldValue).trim() : '';",
  "",
  "  // Mobile Portrait Edition tabs",
  "  if (name.indexOf('Tuần Này') !== -1) {",
  "    if (row === 5 && (col === 2 || col === 3 || col === 6)) {",
  "      htMobileWeekSwitch_(ss, sh, col, oldVal);",
  "    }",
  "    return;",
  "  }",
  "  if (name.indexOf('Việc Hôm Nay') !== -1) {",
  "    if (row === 5 && (col === 2 || col === 3 || col === 7)) {",
  "      htMobileDailySwitch_(ss, sh, col, oldVal);",
  "    }",
  "    return;",
  "  }",
  "  if (name.indexOf('Mục Tiêu') !== -1) {",
  "    if (row === 3 && col === 5) {",
  "      htMobileGoalsSwitch_(ss, sh, oldVal);",
  "    }",
  "    return;",
  "  }",
  "",
  "  // Desktop 5-Tab Edition tabs",
  "  if (name.indexOf('Nhiệm Vụ Ngày') !== -1) {",
  "    if (row === 5 && col >= 4 && col <= 6) {",
  "      htDeskDailySwitch_(ss, sh, col, oldVal);",
  "    }",
  "    return;",
  "  }",
  "  if (name.indexOf('Yearly Goals') !== -1) {",
  "    if (row === 2 && col === 9) {",
  "      htDeskGoalsSwitch_(ss, sh, oldVal);",
  "    }",
  "    return;",
  "  }",
  "  // Desktop Monthly Tracker dropdowns: B3 (Month) or B5 (Year)",
  "  if (col === 2 && (row === 3 || row === 5)) {",
  "    htDeskMonthlySwitch_(ss, sh, row, oldVal);",
  "  }",
  "}",
  "",
  "// ---------------- O(1) Single-Pass _Database Indexer ----------------",
  "function htBuildIndex_(wsDb, keyCol, blockSize) {",
  "  var maxR = wsDb.getLastRow();",
  "  var map = Object.create(null);",
  "  if (maxR < 2) return { map: map, nextRow: 2 };",
  "  var vals = wsDb.getRange(2, keyCol, maxR - 1, 1).getValues();",
  "  var lastNonEmpty = 1;",
  "  for (var i = 0; i < vals.length; i++) {",
  "    var k = htKeyStr_(vals[i][0]);",
  "    if (k !== '') {",
  "      lastNonEmpty = i + 2;",
  "      if (i % blockSize === 0 && map[k] === undefined) {",
  "        map[k] = i + 2;",
  "      }",
  "    }",
  "  }",
  "  return { map: map, nextRow: lastNonEmpty + 1 };",
  "}",
  "",
  "// ---------------- DESKTOP: Monthly Tracker (B3 / B5) ----------------",
  "function htDeskMonthlySwitch_(ss, ws, editedRow, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var sel = ws.getRange('B3:B5').getValues();",
  "  var newMo = HT_MONTHS[String(sel[0][0] || '').trim().toLowerCase()] || 0;",
  "  var newYr = parseInt(sel[2][0], 10) || 0;",
  "  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;",
  "  var newKey = htPad4_(newYr) + '-' + htPad2_(newMo);",
  "",
  "  var oldKey = htKeyStr_(wsCalc.getRange('AN2').getValue());",
  "  if (oldKey.length !== 7 || oldKey.charAt(4) !== '-') {",
  "    // Fallback to e.oldValue on first switch so sample data is never lost",
  "    if (editedRow === 3 && oldVal) {",
  "      var oMo = HT_MONTHS[oldVal.toLowerCase()] || 0;",
  "      if (oMo >= 1 && oMo <= 12) oldKey = htPad4_(newYr) + '-' + htPad2_(oMo);",
  "    } else if (editedRow === 5 && oldVal) {",
  "      var oYr = parseInt(oldVal, 10) || 0;",
  "      if (oYr >= 2000 && oYr <= 2100) oldKey = htPad4_(oYr) + '-' + htPad2_(newMo);",
  "    }",
  "  }",
  "  if (oldKey === newKey) return;",
  "",
  "  var curAll = ws.getRange('B17:AI36').getValues();",
  "  var mIdx = htBuildIndex_(wsDb, 1, HT_N_HABITS_DESK);",
  "",
  "  if (oldKey.length === 7 && oldKey.charAt(4) === '-') {",
  "    htSaveDeskMonth_(ss, wsDb, mIdx, oldKey, curAll);",
  "  }",
  "",
  "  var srcRow = mIdx.map[newKey] || 0;",
  "  var loadGrid = [];",
  "  var gridChanged = false;",
  "  if (srcRow > 0) {",
  "    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_DESK, 35).getValues();",
  "    var loadNames = [];",
  "    var loadGoals = [];",
  "    var hasAnyName = false;",
  "    var namesChanged = false;",
  "    var goalsChanged = false;",
  "    for (var r = 0; r < HT_N_HABITS_DESK; r++) {",
  "      var nm = srcBlock[r][2];",
  "      var gl = srcBlock[r][3];",
  "      if (String(nm || '').trim() !== '') hasAnyName = true;",
  "      if (String(curAll[r][0] || '') !== String(nm || '')) namesChanged = true;",
  "      if (String(curAll[r][33] || '') !== String(gl || '')) goalsChanged = true;",
  "      loadNames.push([nm]);",
  "      loadGoals.push([gl]);",
  "      var rowOut = [];",
  "      for (var d = 0; d < 31; d++) {",
  "        var bv = htIsChecked_(srcBlock[r][4 + d]);",
  "        if (htIsChecked_(curAll[r][1 + d]) !== bv) gridChanged = true;",
  "        rowOut.push(bv);",
  "      }",
  "      loadGrid.push(rowOut);",
  "    }",
  "    if (hasAnyName && namesChanged) ws.getRange('B17:B36').setValues(loadNames);",
  "    if (hasAnyName && goalsChanged) ws.getRange('AI17:AI36').setValues(loadGoals);",
  "    if (gridChanged) ws.getRange('C17:AG36').setValues(loadGrid);",
  "  } else {",
  "    for (var r2 = 0; r2 < HT_N_HABITS_DESK; r2++) {",
  "      var blankRow = [];",
  "      for (var d2 = 0; d2 < 31; d2++) {",
  "        if (htIsChecked_(curAll[r2][1 + d2])) gridChanged = true;",
  "        blankRow.push(false);",
  "      }",
  "      loadGrid.push(blankRow);",
  "    }",
  "    if (gridChanged) ws.getRange('C17:AG36').setValues(loadGrid);",
  "  }",
  "",
  "  wsCalc.getRange('AN2').setNumberFormat('@').setValue(newKey);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "function htSaveDeskMonth_(ss, wsDb, mIdx, saveKey, curAll) {",
  "  var rawBlock = [];",
  "  for (var r = 0; r < HT_N_HABITS_DESK; r++) {",
  "    var row = [saveKey, r + 1, curAll[r][0], curAll[r][33]];",
  "    for (var d = 0; d < 31; d++) row.push(htIsChecked_(curAll[r][1 + d]));",
  "    rawBlock.push(row);",
  "  }",
  "  var dstRow = mIdx.map[saveKey] || 0;",
  "  if (dstRow === 0) {",
  "    dstRow = mIdx.nextRow;",
  "    mIdx.map[saveKey] = dstRow;",
  "    mIdx.nextRow += HT_N_HABITS_DESK;",
  "  }",
  "  wsDb.getRange(dstRow, 1, HT_N_HABITS_DESK, 1).setNumberFormat('@');",
  "  wsDb.getRange(dstRow, 1, HT_N_HABITS_DESK, 35).setValues(rawBlock);",
  "",
  "  var yr = parseInt(saveKey.substring(0, 4), 10);",
  "  var mo = parseInt(saveKey.substring(5, 7), 10);",
  "  var dimDays = new Date(yr, mo, 0).getDate();",
  "  var activeRows = [];",
  "  var totalDone = 0;",
  "  var totalGoal = 0;",
  "  var bestStreak = 0;",
  "  for (var i = 0; i < HT_N_HABITS_DESK; i++) {",
  "    if (String(curAll[i][0] || '').trim() !== '') {",
  "      activeRows.push(i);",
  "      var gVal = Number(curAll[i][33]);",
  "      totalGoal += (gVal > 0) ? Math.min(gVal, dimDays) : dimDays;",
  "      var run = 0;",
  "      for (var k = 0; k < dimDays; k++) {",
  "        if (htIsChecked_(curAll[i][1 + k])) {",
  "          totalDone++;",
  "          run++;",
  "          if (run > bestStreak) bestStreak = run;",
  "        } else {",
  "          run = 0;",
  "        }",
  "      }",
  "    }",
  "  }",
  "  var grownDays = 0;",
  "  var perfectDays = 0;",
  "  var thr3 = htGetThr3_(ss);",
  "  if (activeRows.length > 0) {",
  "    for (var dayIdx = 0; dayIdx < dimDays; dayIdx++) {",
  "      var doneDay = 0;",
  "      for (var a = 0; a < activeRows.length; a++) {",
  "        if (htIsChecked_(curAll[activeRows[a]][1 + dayIdx])) doneDay++;",
  "      }",
  "      var pct = doneDay / activeRows.length;",
  "      if (pct >= thr3 - 1e-6) grownDays++;",
  "      if (pct >= 0.999) perfectDays++;",
  "    }",
  "  }",
  "  var overall = totalGoal > 0 ? Math.min(1, totalDone / totalGoal) : 0;",
  "  var sumIdx = htBuildIndex_(wsDb, 37, 1);",
  "  var sRow = sumIdx.map[saveKey] || sumIdx.nextRow;",
  "  wsDb.getRange(sRow, 37).setNumberFormat('@');",
  "  wsDb.getRange(sRow, 37, 1, 9).setValues([[saveKey, yr, mo, totalDone, totalGoal, overall, grownDays, perfectDays, bestStreak]]);",
  "}",
  "",
  "// ---------------- DESKTOP: Daily Tasks (D5 / E5 / F5) ----------------",
  "function htDeskDailySwitch_(ss, ws, editedCol, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var sel = ws.getRange('D5:F5').getValues()[0];",
  "  var newDay = parseInt(sel[0], 10) || 0;",
  "  var newMo = HT_MONTHS[String(sel[1] || '').trim().toLowerCase()] || 0;",
  "  var newYr = parseInt(sel[2], 10) || 0;",
  "  if (newDay < 1 || newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;",
  "",
  "  var maxDay = new Date(newYr, newMo, 0).getDate();",
  "  if (newDay > maxDay) {",
  "    newDay = maxDay;",
  "    ws.getRange('D5').setValue(newDay);",
  "  }",
  "  var newKey = htPad4_(newYr) + '-' + htPad2_(newMo) + '-' + htPad2_(newDay);",
  "",
  "  var oldKey = htKeyStr_(wsCalc.getRange('AN12').getValue());",
  "  if (oldKey.length !== 10 && oldVal) {",
  "    var oD = (editedCol === 4) ? (parseInt(oldVal, 10) || newDay) : newDay;",
  "    var oM = (editedCol === 5) ? (HT_MONTHS[oldVal.toLowerCase()] || newMo) : newMo;",
  "    var oY = (editedCol === 6) ? (parseInt(oldVal, 10) || newYr) : newYr;",
  "    if (oD >= 1 && oM >= 1 && oM <= 12 && oY >= 2000) {",
  "      oldKey = htPad4_(oY) + '-' + htPad2_(oM) + '-' + htPad2_(oD);",
  "    }",
  "  }",
  "  if (oldKey === newKey) return;",
  "",
  "  var dtIdx = htBuildIndex_(wsDb, 59, HT_N_TASKS_DESK);",
  "  if (oldKey.length === 10) {",
  "    var curTasks = ws.getRange('B9:F28').getValues();",
  "    var curNote = ws.getRange('B31').getValue();",
  "    var block = [];",
  "    for (var r = 0; r < HT_N_TASKS_DESK; r++) {",
  "      block.push([",
  "        oldKey, r + 1, htIsChecked_(curTasks[r][0]), curTasks[r][1], curTasks[r][2],",
  "        curTasks[r][3], curTasks[r][4], (r === 0 ? curNote : '')",
  "      ]);",
  "    }",
  "    var dstR = dtIdx.map[oldKey] || dtIdx.nextRow;",
  "    if (!dtIdx.map[oldKey]) {",
  "      dtIdx.map[oldKey] = dstR;",
  "      dtIdx.nextRow += HT_N_TASKS_DESK;",
  "    }",
  "    wsDb.getRange(dstR, 59, HT_N_TASKS_DESK, 1).setNumberFormat('@');",
  "    wsDb.getRange(dstR, 59, HT_N_TASKS_DESK, 8).setValues(block);",
  "  }",
  "",
  "  var srcR = dtIdx.map[newKey] || 0;",
  "  var loadTasks = [];",
  "  var loadNote = '';",
  "  if (srcR > 0) {",
  "    var srcArr = wsDb.getRange(srcR, 59, HT_N_TASKS_DESK, 8).getValues();",
  "    for (var i = 0; i < HT_N_TASKS_DESK; i++) {",
  "      loadTasks.push([htIsChecked_(srcArr[i][2]), srcArr[i][3], srcArr[i][4], srcArr[i][5], srcArr[i][6]]);",
  "    }",
  "    loadNote = srcArr[0][7];",
  "  } else {",
  "    for (var j = 0; j < HT_N_TASKS_DESK; j++) loadTasks.push([false, '', '', '', '']);",
  "  }",
  "  ws.getRange('B9:F28').setValues(loadTasks);",
  "  ws.getRange('B31').setValue(loadNote);",
  "  wsCalc.getRange('AN12').setNumberFormat('@').setValue(newKey);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "// ---------------- DESKTOP: Yearly Goals (I2) ----------------",
  "function htDeskGoalsSwitch_(ss, ws, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var newYr = parseInt(ws.getRange('I2').getValue(), 10) || 0;",
  "  if (newYr < 2000 || newYr > 2100) return;",
  "  var oldYr = parseInt(wsCalc.getRange('AN3').getValue(), 10) || 0;",
  "  if (oldYr < 2000 && oldVal) oldYr = parseInt(oldVal, 10) || 0;",
  "  if (oldYr === newYr) return;",
  "",
  "  var gIdx = htBuildIndex_(wsDb, 47, HT_N_GOALS_DESK);",
  "  if (oldYr >= 2000) {",
  "    var curYG = ws.getRange('B6:F25').getValues();",
  "    var ygBlock = [];",
  "    var gDone = 0;",
  "    var gTot = 0;",
  "    for (var r = 0; r < HT_N_GOALS_DESK; r++) {",
  "      var chk = htIsChecked_(curYG[r][0]);",
  "      var gTxt = curYG[r][1];",
  "      if (String(gTxt || '').trim() !== '') {",
  "        gTot++;",
  "        if (chk) gDone++;",
  "      }",
  "      ygBlock.push([oldYr, r + 1, chk, gTxt, curYG[r][2], curYG[r][3], curYG[r][4]]);",
  "    }",
  "    var oldKey = String(oldYr);",
  "    var dstR = gIdx.map[oldKey] || gIdx.nextRow;",
  "    if (!gIdx.map[oldKey]) {",
  "      gIdx.map[oldKey] = dstR;",
  "      gIdx.nextRow += HT_N_GOALS_DESK;",
  "    }",
  "    wsDb.getRange(dstR, 47, HT_N_GOALS_DESK, 7).setValues(ygBlock);",
  "    var sIdx = htBuildIndex_(wsDb, 55, 1);",
  "    var sR = sIdx.map[oldKey] || sIdx.nextRow;",
  "    wsDb.getRange(sR, 55, 1, 3).setValues([[oldYr, gDone, gTot]]);",
  "  }",
  "",
  "  var srcR = gIdx.map[String(newYr)] || 0;",
  "  var loadYG = [];",
  "  if (srcR > 0) {",
  "    var srcBlock = wsDb.getRange(srcR, 47, HT_N_GOALS_DESK, 7).getValues();",
  "    for (var i = 0; i < HT_N_GOALS_DESK; i++) {",
  "      loadYG.push([htIsChecked_(srcBlock[i][2]), srcBlock[i][3], srcBlock[i][4], srcBlock[i][5], srcBlock[i][6]]);",
  "    }",
  "  } else {",
  "    for (var j = 0; j < HT_N_GOALS_DESK; j++) loadYG.push([false, '', '', '', '']);",
  "  }",
  "  ws.getRange('B6:F25').setValues(loadYG);",
  "  wsCalc.getRange('AN3').setValue(newYr);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "// ---------------- MOBILE: Weekly Tracker (B5 / C5 / F5) ----------------",
  "function htParseWeek_(raw) {",
  "  var m = String(raw || '').match(/(\\d+)/);",
  "  return m ? parseInt(m[1], 10) : 0;",
  "}",
  "",
  "function htMobileWeekSwitch_(ss, ws, editedCol, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var sel = ws.getRange('B5:F5').getValues()[0];",
  "  var newMo = HT_MONTHS[String(sel[0] || '').trim().toLowerCase()] || 0;",
  "  var newYr = parseInt(sel[1], 10) || 0;",
  "  var newWk = htParseWeek_(sel[4]);",
  "  if (newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100 || newWk < 1 || newWk > 5) return;",
  "  var newKey = htPad4_(newYr) + '-' + htPad2_(newMo) + '-W' + newWk;",
  "",
  "  var oldKey = htKeyStr_(wsCalc.getRange('E14').getValue());",
  "  if (oldKey.indexOf('-W') === -1 && oldVal) {",
  "    var oM = (editedCol === 2) ? (HT_MONTHS[oldVal.toLowerCase()] || newMo) : newMo;",
  "    var oY = (editedCol === 3) ? (parseInt(oldVal, 10) || newYr) : newYr;",
  "    var oW = (editedCol === 6) ? (htParseWeek_(oldVal) || newWk) : newWk;",
  "    if (oM >= 1 && oM <= 12 && oY >= 2000 && oW >= 1 && oW <= 5) {",
  "      oldKey = htPad4_(oY) + '-' + htPad2_(oM) + '-W' + oW;",
  "    }",
  "  }",
  "  if (oldKey === newKey) return;",
  "",
  "  var wkIdx = htBuildIndex_(wsDb, 1, HT_N_HABITS_MOB);",
  "  var curAll = ws.getRange('B21:I35').getValues();",
  "  if (oldKey.indexOf('-W') !== -1) {",
  "    htSaveMobileWeek_(ss, wsDb, wkIdx, oldKey, curAll);",
  "  }",
  "",
  "  var srcRow = wkIdx.map[newKey] || 0;",
  "  var loadGrid = [];",
  "  if (srcRow > 0) {",
  "    var srcBlock = wsDb.getRange(srcRow, 1, HT_N_HABITS_MOB, 10).getValues();",
  "    var loadNames = [];",
  "    var hasAny = false;",
  "    var namesChanged = false;",
  "    for (var r = 0; r < HT_N_HABITS_MOB; r++) {",
  "      var nm = srcBlock[r][2];",
  "      if (String(nm || '').trim() !== '') hasAny = true;",
  "      if (String(curAll[r][0] || '') !== String(nm || '')) namesChanged = true;",
  "      loadNames.push([nm]);",
  "      var rowOut = [];",
  "      for (var d = 0; d < 7; d++) rowOut.push(htIsChecked_(srcBlock[r][3 + d]));",
  "      loadGrid.push(rowOut);",
  "    }",
  "    if (hasAny && namesChanged) ws.getRange('B21:B35').setValues(loadNames);",
  "    ws.getRange('C21:I35').setValues(loadGrid);",
  "  } else {",
  "    for (var r2 = 0; r2 < HT_N_HABITS_MOB; r2++) {",
  "      loadGrid.push([false, false, false, false, false, false, false]);",
  "    }",
  "    ws.getRange('C21:I35').setValues(loadGrid);",
  "  }",
  "",
  "  wsCalc.getRange('E14').setNumberFormat('@').setValue(newKey);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "function htSaveMobileWeek_(ss, wsDb, wkIdx, saveKey, curAll) {",
  "  var rawBlock = [];",
  "  for (var r = 0; r < HT_N_HABITS_MOB; r++) {",
  "    var row = [saveKey, r + 1, curAll[r][0]];",
  "    for (var d = 0; d < 7; d++) row.push(htIsChecked_(curAll[r][1 + d]));",
  "    rawBlock.push(row);",
  "  }",
  "  var dstRow = wkIdx.map[saveKey] || 0;",
  "  if (dstRow === 0) {",
  "    dstRow = wkIdx.nextRow;",
  "    wkIdx.map[saveKey] = dstRow;",
  "    wkIdx.nextRow += HT_N_HABITS_MOB;",
  "  }",
  "  wsDb.getRange(dstRow, 1, HT_N_HABITS_MOB, 1).setNumberFormat('@');",
  "  wsDb.getRange(dstRow, 1, HT_N_HABITS_MOB, 10).setValues(rawBlock);",
  "",
  "  var parts = saveKey.split('-');",
  "  var yr = parseInt(parts[0], 10);",
  "  var mo = parseInt(parts[1], 10);",
  "  var wk = parseInt(parts[2].replace('W', ''), 10);",
  "  var first = new Date(yr, mo - 1, 1);",
  "  var firstWd = (first.getDay() + 6) % 7;",
  "  var activeCols = [];",
  "  for (var dow = 0; dow < 7; dow++) {",
  "    var dt = new Date(yr, mo - 1, 1 - firstWd + (wk - 1) * 7 + dow);",
  "    if (dt.getMonth() === (mo - 1)) activeCols.push(dow);",
  "  }",
  "  var activeRows = [];",
  "  var completed = 0;",
  "  var bestStreak = 0;",
  "  for (var i = 0; i < HT_N_HABITS_MOB; i++) {",
  "    if (String(curAll[i][0] || '').trim() !== '') {",
  "      activeRows.push(i);",
  "      var run = 0;",
  "      for (var k = 0; k < activeCols.length; k++) {",
  "        if (htIsChecked_(curAll[i][1 + activeCols[k]])) {",
  "          completed++;",
  "          run++;",
  "          if (run > bestStreak) bestStreak = run;",
  "        } else {",
  "          run = 0;",
  "        }",
  "      }",
  "    }",
  "  }",
  "  var target = activeRows.length * activeCols.length;",
  "  var grown = 0;",
  "  var perfect = 0;",
  "  var thr3 = htGetThr3_(ss);",
  "  if (activeRows.length > 0) {",
  "    for (var cIdx = 0; cIdx < activeCols.length; cIdx++) {",
  "      var colD = activeCols[cIdx];",
  "      var dCnt = 0;",
  "      for (var a = 0; a < activeRows.length; a++) {",
  "        if (htIsChecked_(curAll[activeRows[a]][1 + colD])) dCnt++;",
  "      }",
  "      var pct = dCnt / activeRows.length;",
  "      if (pct >= thr3 - 1e-6) grown++;",
  "      if (pct >= 0.999) perfect++;",
  "    }",
  "  }",
  "  var sumIdx = htBuildIndex_(wsDb, 13, 1);",
  "  var sRow = sumIdx.map[saveKey] || sumIdx.nextRow;",
  "  wsDb.getRange(sRow, 13).setNumberFormat('@');",
  "  wsDb.getRange(sRow, 13, 1, 9).setValues([[saveKey, yr, mo, wk, completed, target, grown, perfect, bestStreak]]);",
  "}",
  "",
  "// ---------------- MOBILE: Daily Tasks (B5 / C5 / G5) ----------------",
  "function htMobileDailySwitch_(ss, ws, editedCol, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var sel = ws.getRange('B5:G5').getValues()[0];",
  "  var newDay = parseInt(sel[0], 10) || 0;",
  "  var newMo = HT_MONTHS[String(sel[1] || '').trim().toLowerCase()] || 0;",
  "  var newYr = parseInt(sel[5], 10) || 0;",
  "  if (newDay < 1 || newMo < 1 || newMo > 12 || newYr < 2000 || newYr > 2100) return;",
  "",
  "  var maxDay = new Date(newYr, newMo, 0).getDate();",
  "  if (newDay > maxDay) {",
  "    newDay = maxDay;",
  "    ws.getRange('B5').setValue(newDay);",
  "  }",
  "  var newKey = htPad4_(newYr) + '-' + htPad2_(newMo) + '-' + htPad2_(newDay);",
  "",
  "  var oldKey = htKeyStr_(wsCalc.getRange('E29').getValue());",
  "  if (oldKey.length !== 10 && oldVal) {",
  "    var oD = (editedCol === 2) ? (parseInt(oldVal, 10) || newDay) : newDay;",
  "    var oM = (editedCol === 3) ? (HT_MONTHS[oldVal.toLowerCase()] || newMo) : newMo;",
  "    var oY = (editedCol === 7) ? (parseInt(oldVal, 10) || newYr) : newYr;",
  "    if (oD >= 1 && oM >= 1 && oM <= 12 && oY >= 2000) {",
  "      oldKey = htPad4_(oY) + '-' + htPad2_(oM) + '-' + htPad2_(oD);",
  "    }",
  "  }",
  "  if (oldKey === newKey) return;",
  "",
  "  var dtIdx = htBuildIndex_(wsDb, 32, HT_N_TASKS_MOB);",
  "  if (oldKey.length === 10) {",
  "    var curAll = ws.getRange('B16:G30').getValues();",
  "    var curNote = ws.getRange('B33').getValue();",
  "    var block = [];",
  "    for (var r = 0; r < HT_N_TASKS_MOB; r++) {",
  "      block.push([oldKey, r + 1, htIsChecked_(curAll[r][0]), curAll[r][1], curAll[r][5], (r === 0 ? curNote : '')]);",
  "    }",
  "    var dstR = dtIdx.map[oldKey] || dtIdx.nextRow;",
  "    if (!dtIdx.map[oldKey]) {",
  "      dtIdx.map[oldKey] = dstR;",
  "      dtIdx.nextRow += HT_N_TASKS_MOB;",
  "    }",
  "    wsDb.getRange(dstR, 32, HT_N_TASKS_MOB, 1).setNumberFormat('@');",
  "    wsDb.getRange(dstR, 32, HT_N_TASKS_MOB, 6).setValues(block);",
  "  }",
  "",
  "  var srcR = dtIdx.map[newKey] || 0;",
  "  var loadBC = [];",
  "  var loadPr = [];",
  "  var loadNote = '';",
  "  if (srcR > 0) {",
  "    var srcArr = wsDb.getRange(srcR, 32, HT_N_TASKS_MOB, 6).getValues();",
  "    for (var i = 0; i < HT_N_TASKS_MOB; i++) {",
  "      loadBC.push([htIsChecked_(srcArr[i][2]), srcArr[i][3]]);",
  "      loadPr.push([srcArr[i][4]]);",
  "    }",
  "    loadNote = srcArr[0][5];",
  "  } else {",
  "    for (var j = 0; j < HT_N_TASKS_MOB; j++) {",
  "      loadBC.push([false, '']);",
  "      loadPr.push(['']);",
  "    }",
  "  }",
  "  ws.getRange('B16:C30').setValues(loadBC);",
  "  ws.getRange('G16:G30').setValues(loadPr);",
  "  ws.getRange('B33').setValue(loadNote);",
  "  wsCalc.getRange('E29').setNumberFormat('@').setValue(newKey);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "// ---------------- MOBILE: Yearly Goals (E3) ----------------",
  "function htMobileGoalsSwitch_(ss, ws, oldVal) {",
  "  var wsCalc = ss.getSheetByName(HT_CALC);",
  "  var wsDb = ss.getSheetByName(HT_DB);",
  "  if (!wsCalc || !wsDb) return;",
  "",
  "  var newYr = parseInt(ws.getRange('E3').getValue(), 10) || 0;",
  "  if (newYr < 2000 || newYr > 2100) return;",
  "  var oldYr = parseInt(wsCalc.getRange('E15').getValue(), 10) || 0;",
  "  if (oldYr < 2000 && oldVal) oldYr = parseInt(oldVal, 10) || 0;",
  "  if (oldYr === newYr) return;",
  "",
  "  var gIdx = htBuildIndex_(wsDb, 23, HT_N_GOALS_MOB);",
  "  if (oldYr >= 2000) {",
  "    var curBC = ws.getRange('B11:C22').getValues();",
  "    var block = [];",
  "    var gDone = 0;",
  "    var gTot = 0;",
  "    for (var r = 0; r < HT_N_GOALS_MOB; r++) {",
  "      var cv = htIsChecked_(curBC[r][0]);",
  "      var tv = curBC[r][1];",
  "      if (String(tv || '').trim() !== '') {",
  "        gTot++;",
  "        if (cv) gDone++;",
  "      }",
  "      block.push([oldYr, r + 1, cv, tv]);",
  "    }",
  "    var oldKey = String(oldYr);",
  "    var dstR = gIdx.map[oldKey] || gIdx.nextRow;",
  "    if (!gIdx.map[oldKey]) {",
  "      gIdx.map[oldKey] = dstR;",
  "      gIdx.nextRow += HT_N_GOALS_MOB;",
  "    }",
  "    wsDb.getRange(dstR, 23, HT_N_GOALS_MOB, 4).setValues(block);",
  "    var sIdx = htBuildIndex_(wsDb, 28, 1);",
  "    var sR = sIdx.map[oldKey] || sIdx.nextRow;",
  "    wsDb.getRange(sR, 28, 1, 3).setValues([[oldYr, gDone, gTot]]);",
  "  }",
  "",
  "  var srcR = gIdx.map[String(newYr)] || 0;",
  "  var loadBC = [];",
  "  if (srcR > 0) {",
  "    var srcBlock = wsDb.getRange(srcR, 23, HT_N_GOALS_MOB, 4).getValues();",
  "    for (var i = 0; i < HT_N_GOALS_MOB; i++) {",
  "      loadBC.push([htIsChecked_(srcBlock[i][2]), srcBlock[i][3]]);",
  "    }",
  "  } else {",
  "    for (var j = 0; j < HT_N_GOALS_MOB; j++) loadBC.push([false, '']);",
  "  }",
  "  ws.getRange('B11:C22').setValues(loadBC);",
  "  wsCalc.getRange('E15').setValue(newYr);",
  "  ss.toast('Đã lưu & chuyển lịch ✓', 'Habit Tracker', 2);",
  "}",
  "",
  "// ---------------- Pure Helpers ----------------",
  "function htGetThr3_(ss) {",
  "  try {",
  "    var nr = ss.getRangeByName('CFG_THR_3');",
  "    if (nr) {",
  "      var v = Number(nr.getValue());",
  "      if (v > 0 && v <= 1) return v;",
  "    }",
  "  } catch (err) {}",
  "  return 0.75;",
  "}",
  "function htIsChecked_(v) {",
  "  return v === true || String(v).toUpperCase() === 'TRUE' || String(v).trim() === '✓';",
  "}",
  "function htKeyStr_(v) {",
  "  if (v instanceof Date) {",
  "    return htPad4_(v.getFullYear()) + '-' + htPad2_(v.getMonth() + 1) + '-' + htPad2_(v.getDate());",
  "  }",
  "  return String(v || '').trim();",
  "}",
  "function htPad2_(n) { return (n < 10 ? '0' : '') + n; }",
  "function htPad4_(n) { return String(n); }"
].join("\n");

var BOUND_MANIFEST = JSON.stringify({
  timeZone: "Asia/Ho_Chi_Minh",
  dependencies: {},
  exceptionLogging: "STACKDRIVER",
  runtimeVersion: "V8"
}, null, 2);

// ============================================================================
//  MAIN INJECTOR ENTRYPOINT
// ============================================================================
function injectAutoSaveToFolder() {
  if (!TARGET_FOLDER_ID || TARGET_FOLDER_ID === "PASTE_YOUR_NATIVE_SHEETS_FOLDER_ID_HERE") {
    throw new Error("Vui lòng điền TARGET_FOLDER_ID trước khi chạy!");
  }

  var tStart = Date.now();
  var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
  var token = ScriptApp.getOAuthToken();
  var props = PropertiesService.getScriptProperties();

  // Merge injected map from ScriptProperties + folder JSON log for rock-solid idempotency
  var injectedMap = loadInjectedManifest_(folder, props);

  var sheetsList = [];
  var iter = folder.getFilesByType(MimeType.GOOGLE_SHEETS);
  while (iter.hasNext()) {
    sheetsList.push(iter.next());
  }
  sheetsList.sort(function (a, b) {
    return a.getName().localeCompare(b.getName(), "en", { numeric: true });
  });

  Logger.log("Found " + sheetsList.length + " native Google Sheet(s) in '" + folder.getName() + "'.");
  var injectedNow = 0;
  var skipped = 0;
  var pausedForTime = false;

  for (var i = 0; i < sheetsList.length; i++) {
    if (Date.now() - tStart > SOFT_LIMIT_MS) {
      pausedForTime = true;
      Logger.log("Reached 4.5-minute safe checkpoint (" + i + "/" + sheetsList.length + "). Run again to resume!");
      break;
    }

    var file = sheetsList[i];
    var fileId = file.getId();
    var fileName = file.getName();

    if (SKIP_ALREADY_INJECTED && injectedMap[fileId]) {
      skipped++;
      continue;
    }

    try {
      // 1) Prepare spreadsheet: clean old setup hints + seed _Calc keys & initial _Database snapshot
      prepareSpreadsheetForAutoSave_(fileId);

      // 2) Attach container-bound script project via Apps Script REST API
      var scriptId = createBoundScriptProject_(fileId, token);
      uploadBoundScriptContent_(scriptId, token);

      injectedMap[fileId] = { scriptId: scriptId, name: fileName, updatedAt: new Date().toISOString() };
      props.setProperty(PROP_PREFIX + fileId, scriptId);
      injectedNow++;
      Logger.log("[" + (i + 1) + "/" + sheetsList.length + "] INJECTED: " + fileName + " -> scriptId=" + scriptId);
    } catch (err) {
      Logger.log("[" + (i + 1) + "/" + sheetsList.length + "] ERROR on " + fileName + ": " + err);
    }
  }

  saveInjectedManifest_(folder, injectedMap);
  Logger.log("============================================================");
  Logger.log("Done injection run: injected=" + injectedNow + ", skipped=" + skipped + ", totalBound=" + Object.keys(injectedMap).length);
  if (pausedForTime) {
    Logger.log("NOTICE: Re-run injectAutoSaveToFolder() to finish remaining sheets.");
  }
}

/**
 * Utility: push updated `BOUND_CODE` to all already-injected spreadsheets in TARGET_FOLDER_ID
 * WITHOUT creating duplicate bound script projects!
 */
function updateAlreadyInjectedScripts() {
  if (!TARGET_FOLDER_ID || TARGET_FOLDER_ID === "PASTE_YOUR_NATIVE_SHEETS_FOLDER_ID_HERE") {
    throw new Error("Vui lòng điền TARGET_FOLDER_ID trước khi chạy!");
  }
  var tStart = Date.now();
  var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
  var token = ScriptApp.getOAuthToken();
  var props = PropertiesService.getScriptProperties();
  var injectedMap = loadInjectedManifest_(folder, props);
  var ids = Object.keys(injectedMap);
  var updated = 0;

  for (var i = 0; i < ids.length; i++) {
    if (Date.now() - tStart > SOFT_LIMIT_MS) {
      Logger.log("Reached 4.5-minute checkpoint at " + i + "/" + ids.length + ".");
      break;
    }
    var entry = injectedMap[ids[i]];
    var scriptId = (typeof entry === "string") ? entry : entry.scriptId;
    if (!scriptId) continue;
    try {
      uploadBoundScriptContent_(scriptId, token);
      updated++;
      Logger.log("[" + (i + 1) + "/" + ids.length + "] UPDATED scriptId=" + scriptId + " (" + (entry.name || ids[i]) + ")");
    } catch (err) {
      Logger.log("[" + (i + 1) + "/" + ids.length + "] ERROR updating " + scriptId + ": " + err);
    }
  }
  Logger.log("Finished updating " + updated + "/" + ids.length + " bound script(s).");
}

/**
 * Utility: clears only ScriptProperties cache for this project (does NOT delete JSON log in Drive).
 */
function resetInjectionCache() {
  var props = PropertiesService.getScriptProperties();
  var all = props.getProperties();
  var removed = 0;
  for (var k in all) {
    if (k.indexOf(PROP_PREFIX) === 0) {
      props.deleteProperty(k);
      removed++;
    }
  }
  Logger.log("Cleared " + removed + " cached script property entries.");
}

// ============================================================================
//  APPS SCRIPT REST API HELPERS (v1/projects)
// ============================================================================
function createBoundScriptProject_(spreadsheetId, token) {
  var url = "https://script.googleapis.com/v1/projects";
  var res = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + token },
    payload: JSON.stringify({
      title: BOUND_PROJECT_TITLE,
      parentId: spreadsheetId
    }),
    muteHttpExceptions: true
  });
  var code = res.getResponseCode();
  var body = res.getContentText();
  if (code < 200 || code >= 300) {
    throw new Error("POST /v1/projects failed (" + code + "): " + body);
  }
  var parsed = JSON.parse(body);
  if (!parsed.scriptId) {
    throw new Error("POST /v1/projects returned no scriptId: " + body);
  }
  return parsed.scriptId;
}

function uploadBoundScriptContent_(scriptId, token) {
  var url = "https://script.googleapis.com/v1/projects/" + encodeURIComponent(scriptId) + "/content";
  var res = UrlFetchApp.fetch(url, {
    method: "put",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + token },
    payload: JSON.stringify({
      files: [
        { name: "appsscript", type: "JSON", source: BOUND_MANIFEST },
        { name: "Code", type: "SERVER_JS", source: BOUND_CODE }
      ]
    }),
    muteHttpExceptions: true
  });
  var code = res.getResponseCode();
  if (code < 200 || code >= 300) {
    throw new Error("PUT /v1/projects/" + scriptId + "/content failed (" + code + "): " + res.getContentText());
  }
}

// ============================================================================
//  SPREADSHEET PREP: CLEAN HINT TEXT + SEED INITIAL _Calc & _Database KEYS
// ============================================================================
function prepareSpreadsheetForAutoSave_(spreadsheetId) {
  var ss = SpreadsheetApp.openById(spreadsheetId);
  var wsCalc = ss.getSheetByName("_Calc");
  var wsDb = ss.getSheetByName("_Database");
  if (!wsCalc || !wsDb) return;

  var isMobile = false;
  var sheets = ss.getSheets();
  var wsTracker = null;
  var wsDt = null;
  var wsYg = null;

  for (var i = 0; i < sheets.length; i++) {
    var sh = sheets[i];
    var nm = sh.getName();
    if (nm.indexOf("Tuần Này") !== -1) {
      isMobile = true;
      wsTracker = sh;
    } else if (nm.indexOf("Việc Hôm Nay") !== -1 || nm.indexOf("Nhiệm Vụ Ngày") !== -1) {
      wsDt = sh;
    } else if (nm.indexOf("Mục Tiêu") !== -1 || nm.indexOf("Yearly Goals") !== -1) {
      wsYg = sh;
    } else if (nm !== "_Calc" && nm !== "_Database" && nm !== "_Assets" &&
               nm.indexOf("Hướng Dẫn") === -1 && nm.indexOf("Tổng Kết") === -1) {
      if (!wsTracker) wsTracker = sh;
    }
  }

  if (isMobile) {
    seedMobileSnapshot_(ss, wsCalc, wsDb, wsTracker, wsDt, wsYg);
  } else {
    // Clean old row-6/7 setup hints (formula-safe: NEVER overwrites formulas!)
    if (wsTracker) {
      replaceSetupHintIfPlainText_(wsTracker, "B7");
      replaceSetupHintIfPlainText_(wsTracker, "B6");
    }
    if (wsDt) {
      replaceSetupHintIfPlainText_(wsDt, "B6");
    }
    if (wsYg) {
      replaceSetupHintIfPlainText_(wsYg, "H13");
    }
    seedDesktopSnapshot_(ss, wsCalc, wsDb, wsTracker, wsDt, wsYg);
  }

  // Keep helper sheets cleanly hidden
  ["_Calc", "_Database", "_Assets"].forEach(function (hName) {
    var hSh = ss.getSheetByName(hName);
    if (hSh && !hSh.isSheetHidden()) hSh.hideSheet();
  });
  SpreadsheetApp.flush();
}

function replaceSetupHintIfPlainText_(sheet, a1) {
  var cell = sheet.getRange(a1);
  if (cell.getFormula()) return; // Never touch formula cells (e.g., B6 live motivation pill)
  var txt = String(cell.getValue() || "");
  if (/(setupHabitTracker|Script 1-Click|Chạy Script)/i.test(txt)) {
    cell.setValue(CLEAN_HINT_TEXT);
  }
}

function seedDesktopSnapshot_(ss, wsCalc, wsDb, tracker, dt, yg) {
  if (tracker) {
    var sel = tracker.getRange("B3:B5").getValues();
    var mo = INJ_MONTHS[String(sel[0][0] || "").trim().toLowerCase()] || 0;
    var yr = parseInt(sel[2][0], 10) || 0;
    if (mo >= 1 && mo <= 12 && yr >= 2000 && yr <= 2100) {
      var mKey = injPad4_(yr) + "-" + injPad2_(mo);
      wsCalc.getRange("AN2").setNumberFormat("@").setValue(mKey);
      var mIdx = injBuildIndex_(wsDb, 1, 20);
      if (!mIdx.map[mKey]) {
        var curAll = tracker.getRange("B17:AI36").getValues();
        var rawBlock = [];
        for (var r = 0; r < 20; r++) {
          var row = [mKey, r + 1, curAll[r][0], curAll[r][33]];
          for (var d = 0; d < 31; d++) row.push(injIsChecked_(curAll[r][1 + d]));
          rawBlock.push(row);
        }
        wsDb.getRange(mIdx.nextRow, 1, 20, 1).setNumberFormat("@");
        wsDb.getRange(mIdx.nextRow, 1, 20, 35).setValues(rawBlock);
      }
    }
  }

  if (dt) {
    var dSel = dt.getRange("D5:F5").getValues()[0];
    var dDay = parseInt(dSel[0], 10) || 0;
    var dMo = INJ_MONTHS[String(dSel[1] || "").trim().toLowerCase()] || 0;
    var dYr = parseInt(dSel[2], 10) || 0;
    if (dDay >= 1 && dMo >= 1 && dMo <= 12 && dYr >= 2000 && dYr <= 2100) {
      var dKey = injPad4_(dYr) + "-" + injPad2_(dMo) + "-" + injPad2_(dDay);
      wsCalc.getRange("AN12").setNumberFormat("@").setValue(dKey);
      var dtIdx = injBuildIndex_(wsDb, 59, 20);
      if (!dtIdx.map[dKey]) {
        var curTasks = dt.getRange("B9:F28").getValues();
        var curNote = dt.getRange("B31").getValue();
        var dBlock = [];
        for (var t = 0; t < 20; t++) {
          dBlock.push([dKey, t + 1, injIsChecked_(curTasks[t][0]), curTasks[t][1], curTasks[t][2], curTasks[t][3], curTasks[t][4], (t === 0 ? curNote : "")]);
        }
        wsDb.getRange(dtIdx.nextRow, 59, 20, 1).setNumberFormat("@");
        wsDb.getRange(dtIdx.nextRow, 59, 20, 8).setValues(dBlock);
      }
    }
  }

  if (yg) {
    var yYr = parseInt(yg.getRange("I2").getValue(), 10) || 0;
    if (yYr >= 2000 && yYr <= 2100) {
      wsCalc.getRange("AN3").setValue(yYr);
      var gIdx = injBuildIndex_(wsDb, 47, 20);
      if (!gIdx.map[String(yYr)]) {
        var curYG = yg.getRange("B6:F25").getValues();
        var yBlock = [];
        var gDone = 0;
        var gTot = 0;
        for (var g = 0; g < 20; g++) {
          var chk = injIsChecked_(curYG[g][0]);
          if (String(curYG[g][1] || "").trim() !== "") {
            gTot++;
            if (chk) gDone++;
          }
          yBlock.push([yYr, g + 1, chk, curYG[g][1], curYG[g][2], curYG[g][3], curYG[g][4]]);
        }
        wsDb.getRange(gIdx.nextRow, 47, 20, 7).setValues(yBlock);
        var sIdx = injBuildIndex_(wsDb, 55, 1);
        wsDb.getRange(sIdx.map[String(yYr)] || sIdx.nextRow, 55, 1, 3).setValues([[yYr, gDone, gTot]]);
      }
    }
  }
}

function seedMobileSnapshot_(ss, wsCalc, wsDb, wsWk, wsDt, wsGo) {
  if (wsWk) {
    var sel = wsWk.getRange("B5:F5").getValues()[0];
    var mo = INJ_MONTHS[String(sel[0] || "").trim().toLowerCase()] || 0;
    var yr = parseInt(sel[1], 10) || 0;
    var wkM = String(sel[4] || "").match(/(\d+)/);
    var wk = wkM ? parseInt(wkM[1], 10) : 0;
    if (mo >= 1 && mo <= 12 && yr >= 2000 && yr <= 2100 && wk >= 1 && wk <= 5) {
      var wKey = injPad4_(yr) + "-" + injPad2_(mo) + "-W" + wk;
      wsCalc.getRange("E14").setNumberFormat("@").setValue(wKey);
      var wIdx = injBuildIndex_(wsDb, 1, 15);
      if (!wIdx.map[wKey]) {
        var curAll = wsWk.getRange("B21:I35").getValues();
        var wBlock = [];
        for (var r = 0; r < 15; r++) {
          var row = [wKey, r + 1, curAll[r][0]];
          for (var d = 0; d < 7; d++) row.push(injIsChecked_(curAll[r][1 + d]));
          wBlock.push(row);
        }
        wsDb.getRange(wIdx.nextRow, 1, 15, 1).setNumberFormat("@");
        wsDb.getRange(wIdx.nextRow, 1, 15, 10).setValues(wBlock);
      }
    }
  }

  if (wsDt) {
    var dSel = wsDt.getRange("B5:G5").getValues()[0];
    var dDay = parseInt(dSel[0], 10) || 0;
    var dMo = INJ_MONTHS[String(dSel[1] || "").trim().toLowerCase()] || 0;
    var dYr = parseInt(dSel[5], 10) || 0;
    if (dDay >= 1 && dMo >= 1 && dMo <= 12 && dYr >= 2000 && dYr <= 2100) {
      var dKey = injPad4_(dYr) + "-" + injPad2_(dMo) + "-" + injPad2_(dDay);
      wsCalc.getRange("E29").setNumberFormat("@").setValue(dKey);
      var dIdx = injBuildIndex_(wsDb, 32, 15);
      if (!dIdx.map[dKey]) {
        var curTasks = wsDt.getRange("B16:G30").getValues();
        var curNote = wsDt.getRange("B33").getValue();
        var dBlock = [];
        for (var t = 0; t < 15; t++) {
          dBlock.push([dKey, t + 1, injIsChecked_(curTasks[t][0]), curTasks[t][1], curTasks[t][5], (t === 0 ? curNote : "")]);
        }
        wsDb.getRange(dIdx.nextRow, 32, 15, 1).setNumberFormat("@");
        wsDb.getRange(dIdx.nextRow, 32, 15, 6).setValues(dBlock);
      }
    }
  }

  if (wsGo) {
    var gYr = parseInt(wsGo.getRange("E3").getValue(), 10) || 0;
    if (gYr >= 2000 && gYr <= 2100) {
      wsCalc.getRange("E15").setValue(gYr);
      var gIdx = injBuildIndex_(wsDb, 23, 12);
      if (!gIdx.map[String(gYr)]) {
        var curBC = wsGo.getRange("B11:C22").getValues();
        var gBlock = [];
        var gDone = 0;
        var gTot = 0;
        for (var g = 0; g < 12; g++) {
          var chk = injIsChecked_(curBC[g][0]);
          if (String(curBC[g][1] || "").trim() !== "") {
            gTot++;
            if (chk) gDone++;
          }
          gBlock.push([gYr, g + 1, chk, curBC[g][1]]);
        }
        wsDb.getRange(gIdx.nextRow, 23, 12, 4).setValues(gBlock);
        var sIdx = injBuildIndex_(wsDb, 28, 1);
        wsDb.getRange(sIdx.map[String(gYr)] || sIdx.nextRow, 28, 1, 3).setValues([[gYr, gDone, gTot]]);
      }
    }
  }
}

// ============================================================================
//  MANIFEST & SHARED HELPERS
// ============================================================================
function loadInjectedManifest_(folder, props) {
  var map = {};
  var files = folder.getFilesByName(LOG_FILE_NAME);
  if (files.hasNext()) {
    try {
      var parsed = JSON.parse(files.next().getBlob().getDataAsString() || "{}");
      for (var id in parsed) map[id] = parsed[id];
    } catch (err) {}
  }
  var allProps = props.getProperties();
  for (var k in allProps) {
    if (k.indexOf(PROP_PREFIX) === 0) {
      var fid = k.substring(PROP_PREFIX.length);
      if (!map[fid]) map[fid] = { scriptId: allProps[k] };
    }
  }
  return map;
}

function saveInjectedManifest_(folder, map) {
  var txt = JSON.stringify(map, null, 2);
  var files = folder.getFilesByName(LOG_FILE_NAME);
  if (files.hasNext()) {
    files.next().setContent(txt);
  } else {
    folder.createFile(LOG_FILE_NAME, txt, MimeType.PLAIN_TEXT);
  }
}

function injBuildIndex_(wsDb, keyCol, blockSize) {
  var maxR = wsDb.getLastRow();
  var map = Object.create(null);
  if (maxR < 2) return { map: map, nextRow: 2 };
  var vals = wsDb.getRange(2, keyCol, maxR - 1, 1).getValues();
  var lastNonEmpty = 1;
  for (var i = 0; i < vals.length; i++) {
    var k = String(vals[i][0] || "").trim();
    if (k !== "") {
      lastNonEmpty = i + 2;
      if (i % blockSize === 0 && map[k] === undefined) map[k] = i + 2;
    }
  }
  return { map: map, nextRow: lastNonEmpty + 1 };
}

function injIsChecked_(v) {
  return v === true || String(v).toUpperCase() === "TRUE" || String(v).trim() === "✓";
}
function injPad2_(n) { return (n < 10 ? "0" : "") + n; }
function injPad4_(n) { return String(n); }
