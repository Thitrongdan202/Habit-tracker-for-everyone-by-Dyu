Attribute VB_Name = "modHabitState"
Option Explicit

' =============================================================================
'  modHabitState -- Habit Tracker v3.6 TURBO PERFORMANCE + RICH FX ENGINE
'  ---------------------------------------------------------------------------
'  - 100% PURE ASCII VBA (ZERO Vietnamese/Emoji string literals in VBA code!)
'    All Vietnamese Toast/Button texts live in hidden `_Calc!BA8:BA23`.
'  - Native Pre-Placed Sprite Stacks (`SPR_*_S0..S5`) + Stage-Diff Cache:
'    ZERO slow Camera-Tool Linked Pictures! Only changed slots flip `.Visible`!
'  - O(1) In-Memory `_Database` Index using cross-platform Pure-VBA Collection
'    (100% compatible with BOTH Windows Excel & macOS Excel -- NO ActiveX!)
'  - Bulk `.Value2` 2D Variant array transfers + Lazy-Flush Dirty Flags:
'    ZERO `_Database` writes on single checkbox ticks!
'  - Surgical Calculation + `EnableAnimations = False` during data swaps
'  - Full v3.5 FX Suite intact (Hero Bounce, Sparkle Burst, Non-Blocking Toast,
'    Quick-Action Pastel Pill Buttons, Annual Hall Spotlight) + 1-Click
'    `SyncSpritesFromAssets` custom sprite refresh!
' =============================================================================

Private Const CALC_SHEET As String = "_Calc"
Private Const DB_SHEET As String = "_Database"
Private Const ASSETS_SHEET As String = "_Assets"
Private Const N_HABITS As Long = 20
Private Const N_FORM_ROWS As Long = 20
Private Const N_GOALS As Long = 20
Private Const N_TASKS As Long = 20

Private Const MSO_ROUNDED_RECT As Long = 5
Private Const MSO_HEART As Long = 21
Private Const MSO_STAR_5 As Long = 92
Private Const MSO_STAR_4 As Long = 187
Private Const MSO_FALSE As Long = 0
Private Const MSO_TRUE As Long = -1

' ---- O(1) In-Memory _Database Indexes (Pure-VBA Collection -> Win & Mac!) ----
Private gDbIndexed As Boolean
Private gMonthIndex As Collection
Private gMonthSumIndex As Collection
Private gGoalsIndex As Collection
Private gGoalsSumIndex As Collection
Private gDailyIndex As Collection
Private gMonthNextRow As Long
Private gMonthSumNextRow As Long
Private gGoalsNextRow As Long
Private gGoalsSumNextRow As Long
Private gDailyNextRow As Long

' ---- Lazy-Flush Dirty Flags (ZERO _Database writes on single ticks!) ----
Private gDirtyMonthly As Boolean
Private gDirtyDaily As Boolean
Private gDirtyGoals As Boolean

' ---- Native Sprite Stack Stage-Diff Caches (0=uninit, 1..6=S0..S5, 7=hidden) ----
Private gLastDayStage(1 To 31) As Long
Private gLastMHero As Long
Private gLastDHero As Long
Private gLastGHero As Long
Private gLastAHero As Long
Private gLastBHero As Long
Private gLastAMonth(1 To 12) As Long

' ---- O(1) Direct Shape Object Reference Caches (ZERO ws.Shapes(name) linear scans!) ----
Private gShpCachedM As Boolean
Private gDayShp(1 To 31, 0 To 5) As Shape
Private gMHeroShp(0 To 5) As Shape
Private gShpCachedA As Boolean
Private gAMonthShp(1 To 12, 0 To 5) As Shape
Private gAHeroShp(0 To 5) As Shape
Private gBHeroShp(0 To 5) As Shape
Private gShpCachedD As Boolean
Private gDHeroShp(0 To 5) As Shape
Private gShpCachedG As Boolean
Private gGHeroShp(0 To 5) As Shape

' ---- Non-Blocking Toast State (O(1) reuse + guaranteed zero-orphan delete on close!) ----
Private gToastDueTime As Double
Private gToastScheduled As Boolean
Private gToastSheetName As String
Private gToastShp As Shape
Private gWsCalc As Worksheet
Private gWsDb As Worksheet
Private gFXCached As Boolean
Private gFXVal As Boolean

' =============================================================================
'  INTERNAL HELPERS (100% PURE ASCII)
' =============================================================================
Private Function MonthNameToNum(ByVal mName As String) As Long
    Select Case LCase$(Trim$(mName))
        Case "january":   MonthNameToNum = 1
        Case "february":  MonthNameToNum = 2
        Case "march":     MonthNameToNum = 3
        Case "april":     MonthNameToNum = 4
        Case "may":       MonthNameToNum = 5
        Case "june":      MonthNameToNum = 6
        Case "july":      MonthNameToNum = 7
        Case "august":    MonthNameToNum = 8
        Case "september": MonthNameToNum = 9
        Case "october":   MonthNameToNum = 10
        Case "november":  MonthNameToNum = 11
        Case "december":  MonthNameToNum = 12
        Case Else:        MonthNameToNum = 0
    End Select
End Function

Private Function NumToMonthName(ByVal mNum As Long) As String
    Select Case mNum
        Case 1:  NumToMonthName = "January"
        Case 2:  NumToMonthName = "February"
        Case 3:  NumToMonthName = "March"
        Case 4:  NumToMonthName = "April"
        Case 5:  NumToMonthName = "May"
        Case 6:  NumToMonthName = "June"
        Case 7:  NumToMonthName = "July"
        Case 8:  NumToMonthName = "August"
        Case 9:  NumToMonthName = "September"
        Case 10: NumToMonthName = "October"
        Case 11: NumToMonthName = "November"
        Case 12: NumToMonthName = "December"
        Case Else: NumToMonthName = "October"
    End Select
End Function

Private Function IsCellChecked(ByVal v As Variant) As Boolean
    If IsError(v) Or IsEmpty(v) Then
        IsCellChecked = False
    ElseIf VarType(v) = vbBoolean Then
        IsCellChecked = CBool(v)
    Else
        Dim s As String
        s = Trim$(CStr(v))
        IsCellChecked = (s = ChrW$(10003) Or UCase$(s) = "TRUE")
    End If
End Function

Private Function KeyToString(ByVal v As Variant) As String
    If IsEmpty(v) Or IsError(v) Then
        KeyToString = ""
    ElseIf VarType(v) = vbDate Then
        KeyToString = Format$(CDate(v), "yyyy-mm-dd")
    Else
        KeyToString = Trim$(CStr(v))
    End If
End Function

Private Function StageVal(ByVal v As Variant, ByVal allowSeven As Boolean) As Long
    Dim n As Long
    If IsError(v) Or IsEmpty(v) Or Not IsNumeric(v) Then
        n = 1
    Else
        n = CLng(v)
    End If
    If n < 1 Then n = 1
    If allowSeven Then
        If n > 7 Then n = 7
    Else
        If n > 6 Then n = 6
    End If
    StageVal = n
End Function

Private Function GetAnchorSheet(ByVal anchorName As String) As Worksheet
    On Error Resume Next
    Set GetAnchorSheet = ThisWorkbook.Names(anchorName).RefersToRange.Worksheet
    On Error GoTo 0
End Function

Private Function GetGrownThreshold() As Double
    On Error Resume Next
    Dim v As Variant
    v = ThisWorkbook.Names("CFG_THR_3").RefersToRange.Value2
    If IsNumeric(v) And CDbl(v) > 0 And CDbl(v) <= 1 Then
        GetGrownThreshold = CDbl(v)
    Else
        GetGrownThreshold = 0.75
    End If
    On Error GoTo 0
End Function

Public Function IsFXEnabled() As Boolean
    If gFXCached Then
        IsFXEnabled = gFXVal
        Exit Function
    End If
    On Error Resume Next
    Dim v As Variant
    v = GetCalcSheet().Range("BA1").Value2
    If VarType(v) = vbBoolean Then
        gFXVal = CBool(v)
    Else
        gFXVal = True
    End If
    gFXCached = True
    IsFXEnabled = gFXVal
    On Error GoTo 0
End Function

Public Sub RefreshFXCache()
    gFXCached = False
    Dim dummy As Boolean
    dummy = IsFXEnabled()
End Sub

Private Function GetFxMsg(ByVal rowIdx As Long) As String
    On Error Resume Next
    GetFxMsg = CStr(ThisWorkbook.Worksheets(CALC_SHEET).Cells(rowIdx, 53).Value2)
    On Error GoTo 0
End Function

Private Function HexToRgbLong(ByVal hexStr As String, ByVal fallbackRgb As Long) As Long
    On Error GoTo UseFallback
    Dim s As String
    s = Replace$(Trim$(hexStr), "#", "")
    If Len(s) <> 6 Then GoTo UseFallback
    Dim r As Long, g As Long, b As Long
    r = CLng("&H" & Mid$(s, 1, 2))
    g = CLng("&H" & Mid$(s, 3, 2))
    b = CLng("&H" & Mid$(s, 5, 2))
    HexToRgbLong = RGB(r, g, b)
    Exit Function
UseFallback:
    HexToRgbLong = fallbackRgb
End Function

Private Function GetThemeRgb(ByVal calcRow As Long, ByVal fallbackRgb As Long) As Long
    On Error Resume Next
    Dim s As String
    s = CStr(ThisWorkbook.Worksheets(CALC_SHEET).Cells(calcRow, 53).Value2)
    GetThemeRgb = HexToRgbLong(s, fallbackRgb)
    On Error GoTo 0
End Function

Private Sub WaitSec(ByVal secs As Double)
    Dim t0 As Double
    t0 = Timer
    Do While (Timer - t0) < secs
        DoEvents
        If Timer < t0 Then Exit Do
    Loop
End Sub

' =============================================================================
'  O(1) PURE-VBA COLLECTION INDEX ENGINE FOR `_Database` (WIN & MAC SAFE!)
' =============================================================================
Private Function ColLookup(ByVal col As Collection, ByVal k As String) As Long
    If col Is Nothing Or Len(k) = 0 Then
        ColLookup = 0
        Exit Function
    End If
    On Error Resume Next
    ColLookup = CLng(col(k))
    If Err.Number <> 0 Then
        ColLookup = 0
        Err.Clear
    End If
    On Error GoTo 0
End Function

Private Sub ColPut(ByVal col As Collection, ByVal k As String, ByVal rowNum As Long)
    If col Is Nothing Or Len(k) = 0 Then Exit Sub
    On Error Resume Next
    col.Remove k
    Err.Clear
    col.Add rowNum, k
    On Error GoTo 0
End Sub

Private Sub IndexColumn(ByVal wsDb As Worksheet, ByVal keyCol As Long, ByVal stepSize As Long, _
                        ByRef outCol As Collection, ByRef outNextRow As Long)
    Set outCol = New Collection
    Dim lastRow As Long
    lastRow = wsDb.Cells(wsDb.Rows.Count, keyCol).End(xlUp).Row
    If lastRow < 2 Then
        outNextRow = 2
        Exit Sub
    End If
    outNextRow = lastRow + 1
    Dim arr As Variant
    arr = wsDb.Cells(2, keyCol).Resize(lastRow - 1, 1).Value2
    Dim k As String
    If lastRow = 2 Then
        k = KeyToString(arr)
        If Len(k) > 0 Then ColPut outCol, k, 2
        Exit Sub
    End If
    Dim i As Long
    For i = 1 To UBound(arr, 1) Step stepSize
        k = KeyToString(arr(i, 1))
        If Len(k) > 0 Then
            ColPut outCol, k, i + 1
        End If
    Next i
End Sub

Private Sub EnsureDbIndexes(ByVal wsDb As Worksheet)
    If gDbIndexed And Not (gMonthIndex Is Nothing) And Not (gDailyIndex Is Nothing) And Not (gGoalsIndex Is Nothing) Then
        Exit Sub
    End If
    IndexColumn wsDb, 1, N_HABITS, gMonthIndex, gMonthNextRow
    IndexColumn wsDb, 37, 1, gMonthSumIndex, gMonthSumNextRow
    IndexColumn wsDb, 47, N_GOALS, gGoalsIndex, gGoalsNextRow
    IndexColumn wsDb, 55, 1, gGoalsSumIndex, gGoalsSumNextRow
    IndexColumn wsDb, 59, N_TASKS, gDailyIndex, gDailyNextRow
    gDbIndexed = True
End Sub

' =============================================================================
'  NATIVE PRE-PLACED SPRITE STACK DIFF ENGINE (ZERO CAMERA LINKED PICTURES!)
' =============================================================================
Private Function GetSlotShapeName(ByVal prefix As String, ByVal stage1to6 As Long) As String
    Dim s As Long
    s = stage1to6
    If s < 1 Then s = 1
    If s > 6 Then s = 6
    GetSlotShapeName = prefix & CStr(s - 1)
End Function

Private Sub EnsureMonthlyShapeCache(ByVal ws As Worksheet)
    If gShpCachedM Then Exit Sub
    On Error Resume Next
    Dim shp As Shape, nm As String, dNum As Long, sNum As Long
    For Each shp In ws.Shapes
        nm = shp.Name
        If Left$(nm, 5) = "SPR_D" And Len(nm) = 10 Then
            dNum = CLng(Mid$(nm, 6, 2))
            sNum = CLng(Right$(nm, 1))
            If dNum >= 1 And dNum <= 31 And sNum >= 0 And sNum <= 5 Then
                Set gDayShp(dNum, sNum) = shp
            End If
        ElseIf Left$(nm, 11) = "SPR_MHERO_S" And Len(nm) = 12 Then
            sNum = CLng(Right$(nm, 1))
            If sNum >= 0 And sNum <= 5 Then Set gMHeroShp(sNum) = shp
        End If
    Next shp
    gShpCachedM = True
    On Error GoTo 0
End Sub

Private Sub EnsureAnnualShapeCache(ByVal ws As Worksheet)
    If gShpCachedA Then Exit Sub
    On Error Resume Next
    Dim shp As Shape, nm As String, mNum As Long, sNum As Long
    For Each shp In ws.Shapes
        nm = shp.Name
        If Left$(nm, 6) = "SPR_AM" And Len(nm) = 11 Then
            mNum = CLng(Mid$(nm, 7, 2))
            sNum = CLng(Right$(nm, 1))
            If mNum >= 1 And mNum <= 12 And sNum >= 0 And sNum <= 5 Then
                Set gAMonthShp(mNum, sNum) = shp
            End If
        ElseIf Left$(nm, 11) = "SPR_AHERO_S" And Len(nm) = 12 Then
            sNum = CLng(Right$(nm, 1))
            If sNum >= 0 And sNum <= 5 Then Set gAHeroShp(sNum) = shp
        ElseIf Left$(nm, 11) = "SPR_BHERO_S" And Len(nm) = 12 Then
            sNum = CLng(Right$(nm, 1))
            If sNum >= 0 And sNum <= 5 Then Set gBHeroShp(sNum) = shp
        End If
    Next shp
    gShpCachedA = True
    On Error GoTo 0
End Sub

Private Sub EnsureDailyShapeCache(ByVal ws As Worksheet)
    If gShpCachedD Then Exit Sub
    On Error Resume Next
    Dim shp As Shape, nm As String, sNum As Long
    For Each shp In ws.Shapes
        nm = shp.Name
        If Left$(nm, 11) = "SPR_DHERO_S" And Len(nm) = 12 Then
            sNum = CLng(Right$(nm, 1))
            If sNum >= 0 And sNum <= 5 Then Set gDHeroShp(sNum) = shp
        End If
    Next shp
    gShpCachedD = True
    On Error GoTo 0
End Sub

Private Sub EnsureGoalsShapeCache(ByVal ws As Worksheet)
    If gShpCachedG Then Exit Sub
    On Error Resume Next
    Dim shp As Shape, nm As String, sNum As Long
    For Each shp In ws.Shapes
        nm = shp.Name
        If Left$(nm, 11) = "SPR_GHERO_S" And Len(nm) = 12 Then
            sNum = CLng(Right$(nm, 1))
            If sNum >= 0 And sNum <= 5 Then Set gGHeroShp(sNum) = shp
        End If
    Next shp
    gShpCachedG = True
    On Error GoTo 0
End Sub

Private Sub SyncCached1D(ByRef arr() As Shape, ByRef cachedStage As Long, ByVal newStage As Long)
    If cachedStage = newStage Then Exit Sub
    On Error Resume Next
    If cachedStage >= 1 And cachedStage <= 7 Then
        If cachedStage <= 6 Then
            If Not arr(cachedStage - 1) Is Nothing Then arr(cachedStage - 1).Visible = MSO_FALSE
        End If
        If newStage >= 1 And newStage <= 6 Then
            If Not arr(newStage - 1) Is Nothing Then arr(newStage - 1).Visible = MSO_TRUE
        End If
    Else
        Dim k As Long
        For k = 0 To 5
            If Not arr(k) Is Nothing Then
                arr(k).Visible = IIf(k = newStage - 1, MSO_TRUE, MSO_FALSE)
            End If
        Next k
    End If
    cachedStage = newStage
    On Error GoTo 0
End Sub

Private Sub SyncCachedDay(ByVal dayIdx As Long, ByVal newStage As Long)
    Dim oldStage As Long
    oldStage = gLastDayStage(dayIdx)
    If oldStage = newStage Then Exit Sub
    On Error Resume Next
    If oldStage >= 1 And oldStage <= 7 Then
        If oldStage <= 6 Then
            If Not gDayShp(dayIdx, oldStage - 1) Is Nothing Then gDayShp(dayIdx, oldStage - 1).Visible = MSO_FALSE
        End If
        If newStage >= 1 And newStage <= 6 Then
            If Not gDayShp(dayIdx, newStage - 1) Is Nothing Then gDayShp(dayIdx, newStage - 1).Visible = MSO_TRUE
        End If
    Else
        Dim k As Long
        For k = 0 To 5
            If Not gDayShp(dayIdx, k) Is Nothing Then
                gDayShp(dayIdx, k).Visible = IIf(k = newStage - 1, MSO_TRUE, MSO_FALSE)
            End If
        Next k
    End If
    gLastDayStage(dayIdx) = newStage
    On Error GoTo 0
End Sub

Private Sub SyncCachedAMonth(ByVal mIdx As Long, ByVal newStage As Long)
    Dim oldStage As Long
    oldStage = gLastAMonth(mIdx)
    If oldStage = newStage Then Exit Sub
    On Error Resume Next
    If oldStage >= 1 And oldStage <= 7 Then
        If oldStage <= 6 Then
            If Not gAMonthShp(mIdx, oldStage - 1) Is Nothing Then gAMonthShp(mIdx, oldStage - 1).Visible = MSO_FALSE
        End If
        If newStage >= 1 And newStage <= 6 Then
            If Not gAMonthShp(mIdx, newStage - 1) Is Nothing Then gAMonthShp(mIdx, newStage - 1).Visible = MSO_TRUE
        End If
    Else
        Dim k As Long
        For k = 0 To 5
            If Not gAMonthShp(mIdx, k) Is Nothing Then
                gAMonthShp(mIdx, k).Visible = IIf(k = newStage - 1, MSO_TRUE, MSO_FALSE)
            End If
        Next k
    End If
    gLastAMonth(mIdx) = newStage
    On Error GoTo 0
End Sub

Private Sub ResetSpriteCaches()
    Dim i As Long
    For i = 1 To 31
        gLastDayStage(i) = 0
    Next i
    gLastMHero = 0
    gLastDHero = 0
    gLastGHero = 0
    gLastAHero = 0
    gLastBHero = 0
    For i = 1 To 12
        gLastAMonth(i) = 0
    Next i
    gShpCachedM = False
    gShpCachedA = False
    gShpCachedD = False
    gShpCachedG = False
End Sub

Private Sub InitSpriteCachesFromCalc()
    On Error Resume Next
    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Dim dayArr As Variant
    dayArr = wsCalc.Range("B15:AF15").Value2
    Dim d As Long
    For d = 1 To 31
        gLastDayStage(d) = StageVal(dayArr(1, d), True)
    Next d
    gLastMHero = StageVal(wsCalc.Range("C14").Value2, False)
    gLastDHero = StageVal(wsCalc.Range("AN16").Value2, False)
    gLastGHero = StageVal(wsCalc.Range("AN7").Value2, False)
    gLastAHero = StageVal(wsCalc.Range("AN8").Value2, False)
    gLastBHero = StageVal(wsCalc.Range("AN9").Value2, False)
    Dim annArr As Variant
    annArr = wsCalc.Range("AW2:AW13").Value2
    Dim m As Long
    For m = 1 To 12
        gLastAMonth(m) = StageVal(annArr(m, 1), False)
    Next m
    gShpCachedM = False
    gShpCachedA = False
    gShpCachedD = False
    gShpCachedG = False
    Dim wsTr As Worksheet
    Set wsTr = GetAnchorSheet("ANCHOR_TRACKER")
    If Not wsTr Is Nothing Then EnsureMonthlyShapeCache wsTr
    On Error GoTo 0
End Sub

Public Sub SyncAllMonthlySprites(ByVal ws As Worksheet, ByVal wsCalc As Worksheet)
    EnsureMonthlyShapeCache ws
    Dim stages As Variant
    stages = wsCalc.Range("B15:AF15").Value2
    Dim d As Long, st As Long
    For d = 1 To 31
        st = StageVal(stages(1, d), True)
        If st <> gLastDayStage(d) Then
            SyncCachedDay d, st
        End If
    Next d
    Dim hSt As Long
    hSt = StageVal(wsCalc.Range("C14").Value2, False)
    If hSt <> gLastMHero Then
        SyncCached1D gMHeroShp, gLastMHero, hSt
    End If
End Sub

Private Sub SyncSingleDayAndHero(ByVal ws As Worksheet, ByVal wsCalc As Worksheet, ByVal dayIdx As Long)
    Dim st As Long, hSt As Long
    Dim needDay As Boolean, needHero As Boolean
    needDay = False
    If dayIdx >= 1 And dayIdx <= 31 Then
        st = StageVal(wsCalc.Cells(15, dayIdx + 1).Value2, True)
        If st <> gLastDayStage(dayIdx) Then needDay = True
    End If
    hSt = StageVal(wsCalc.Range("C14").Value2, False)
    needHero = (hSt <> gLastMHero)
    If Not needDay And Not needHero Then Exit Sub

    EnsureMonthlyShapeCache ws
    ' Direct 2-shape diff flip without full-sheet ScreenUpdating flush -> ~2ms!
    If needDay Then SyncCachedDay dayIdx, st
    If needHero Then SyncCached1D gMHeroShp, gLastMHero, hSt
End Sub

Public Sub SyncDailyTaskSprite(ByVal ws As Worksheet, ByVal wsCalc As Worksheet)
    Dim st As Long
    st = StageVal(wsCalc.Range("AN16").Value2, False)
    If st <> gLastDHero Then
        EnsureDailyShapeCache ws
        SyncCached1D gDHeroShp, gLastDHero, st
    End If
End Sub

Public Sub SyncGoalsSprite(ByVal ws As Worksheet, ByVal wsCalc As Worksheet)
    Dim st As Long
    st = StageVal(wsCalc.Range("AN7").Value2, False)
    If st <> gLastGHero Then
        EnsureGoalsShapeCache ws
        SyncCached1D gGHeroShp, gLastGHero, st
    End If
End Sub

Public Sub SyncAnnualSprites(ByVal ws As Worksheet, ByVal wsCalc As Worksheet)
    EnsureAnnualShapeCache ws
    Dim aSt As Long, bSt As Long
    aSt = StageVal(wsCalc.Range("AN8").Value2, False)
    If aSt <> gLastAHero Then
        SyncCached1D gAHeroShp, gLastAHero, aSt
    End If
    bSt = StageVal(wsCalc.Range("AN9").Value2, False)
    If bSt <> gLastBHero Then
        SyncCached1D gBHeroShp, gLastBHero, bSt
    End If
    Dim mStages As Variant
    mStages = wsCalc.Range("AW2:AW13").Value2
    Dim m As Long, st As Long
    For m = 1 To 12
        st = StageVal(mStages(m, 1), False)
        If st <> gLastAMonth(m) Then
            SyncCachedAMonth m, st
        End If
    Next m
End Sub

' =============================================================================
'  BULK `.Value2` DATABASE WRITERS + LAZY-FLUSH DIRTY FLAG FLUSHERS
' =============================================================================
Private Sub SaveMonthBlock(ByVal wsDb As Worksheet, ByVal saveKey As String, _
                           ByVal namesArr As Variant, ByVal goalsArr As Variant, ByVal gridArr As Variant)
    EnsureDbIndexes wsDb
    Dim rawBlock(1 To N_HABITS, 1 To 35) As Variant
    Dim r As Long, d As Long

    For r = 1 To N_HABITS
        rawBlock(r, 1) = saveKey
        rawBlock(r, 2) = r
        rawBlock(r, 3) = namesArr(r, 1)
        rawBlock(r, 4) = goalsArr(r, 1)
        For d = 1 To 31
            rawBlock(r, 4 + d) = gridArr(r, d)
        Next d
    Next r

    Dim dstRow As Long
    dstRow = ColLookup(gMonthIndex, saveKey)
    If dstRow = 0 Then
        dstRow = gMonthNextRow
        gMonthNextRow = gMonthNextRow + N_HABITS
        ColPut gMonthIndex, saveKey, dstRow
    End If
    wsDb.Cells(dstRow, 1).Resize(N_HABITS, 1).NumberFormat = "@"
    wsDb.Cells(dstRow, 1).Resize(N_HABITS, 35).Value2 = rawBlock

    Dim parts() As String
    parts = Split(saveKey, "-")
    If UBound(parts) < 1 Then Exit Sub
    Dim yr As Long, mo As Long, dimDays As Long
    yr = CLng(Val(parts(0)))
    mo = CLng(Val(parts(1)))
    If yr < 2000 Or mo < 1 Or mo > 12 Then Exit Sub
    dimDays = Day(DateSerial(yr, mo + 1, 0))

    Dim activeCount As Long, totalDone As Long, totalGoal As Long
    Dim grownDays As Long, perfectDays As Long, bestStreak As Long
    Dim thrGrown As Double
    thrGrown = GetGrownThreshold()

    Dim isAct(1 To N_HABITS) As Boolean
    Dim curRun As Long, maxRun As Long, gVal As Double

    For r = 1 To N_HABITS
        If Len(Trim$(CStr(namesArr(r, 1)))) > 0 Then
            isAct(r) = True
            activeCount = activeCount + 1
            gVal = Val(CStr(goalsArr(r, 1)))
            If gVal <= 0 Then gVal = dimDays
            totalGoal = totalGoal + CLng(gVal)
            curRun = 0
            maxRun = 0
            For d = 1 To dimDays
                If gridArr(r, d) = True Then
                    totalDone = totalDone + 1
                    curRun = curRun + 1
                    If curRun > maxRun Then maxRun = curRun
                Else
                    curRun = 0
                End If
            Next d
            If maxRun > bestStreak Then bestStreak = maxRun
        End If
    Next r

    If activeCount > 0 Then
        Dim dayDone As Long, dayPct As Double
        For d = 1 To dimDays
            dayDone = 0
            For r = 1 To N_HABITS
                If isAct(r) And gridArr(r, d) = True Then dayDone = dayDone + 1
            Next r
            dayPct = CDbl(dayDone) / CDbl(activeCount)
            If dayPct >= thrGrown - 0.0001 Then grownDays = grownDays + 1
            If dayPct >= 0.999 Then perfectDays = perfectDays + 1
        Next d
    End If

    Dim overallPct As Double
    If totalGoal > 0 Then
        overallPct = CDbl(totalDone) / CDbl(totalGoal)
        If overallPct > 1# Then overallPct = 1#
    End If

    Dim sumRow(1 To 1, 1 To 9) As Variant
    sumRow(1, 1) = saveKey
    sumRow(1, 2) = yr
    sumRow(1, 3) = mo
    sumRow(1, 4) = totalDone
    sumRow(1, 5) = totalGoal
    sumRow(1, 6) = overallPct
    sumRow(1, 7) = grownDays
    sumRow(1, 8) = perfectDays
    sumRow(1, 9) = bestStreak

    Dim sRow As Long
    sRow = ColLookup(gMonthSumIndex, saveKey)
    If sRow = 0 Then
        sRow = gMonthSumNextRow
        gMonthSumNextRow = gMonthSumNextRow + 1
        ColPut gMonthSumIndex, saveKey, sRow
    End If
    wsDb.Cells(sRow, 37).NumberFormat = "@"
    wsDb.Cells(sRow, 37).Resize(1, 9).Value2 = sumRow
End Sub

Private Sub SaveGoalsBlock(ByVal wsDb As Worksheet, ByVal saveYr As Long, ByVal curYG As Variant)
    EnsureDbIndexes wsDb
    Dim ygBlock(1 To N_GOALS, 1 To 7) As Variant
    Dim r As Long, gDone As Long, gTot As Long

    For r = 1 To N_GOALS
        ygBlock(r, 1) = saveYr
        ygBlock(r, 2) = r
        ygBlock(r, 3) = IsCellChecked(curYG(r, 1))
        ygBlock(r, 4) = curYG(r, 2)
        ygBlock(r, 5) = curYG(r, 3)
        ygBlock(r, 6) = curYG(r, 4)
        ygBlock(r, 7) = curYG(r, 5)
        If Len(Trim$(CStr(curYG(r, 2)))) > 0 Then
            gTot = gTot + 1
            If IsCellChecked(curYG(r, 1)) Then gDone = gDone + 1
        End If
    Next r

    Dim yKey As String
    yKey = CStr(saveYr)
    Dim dstYGRow As Long
    dstYGRow = ColLookup(gGoalsIndex, yKey)
    If dstYGRow = 0 Then
        dstYGRow = gGoalsNextRow
        gGoalsNextRow = gGoalsNextRow + N_GOALS
        ColPut gGoalsIndex, yKey, dstYGRow
    End If
    wsDb.Cells(dstYGRow, 47).Resize(N_GOALS, 7).Value2 = ygBlock

    Dim ygSum(1 To 1, 1 To 3) As Variant
    ygSum(1, 1) = saveYr
    ygSum(1, 2) = gDone
    ygSum(1, 3) = gTot
    Dim sYGRow As Long
    sYGRow = ColLookup(gGoalsSumIndex, yKey)
    If sYGRow = 0 Then
        sYGRow = gGoalsSumNextRow
        gGoalsSumNextRow = gGoalsSumNextRow + 1
        ColPut gGoalsSumIndex, yKey, sYGRow
    End If
    wsDb.Cells(sYGRow, 55).Resize(1, 3).Value2 = ygSum
End Sub

Private Sub SaveDailyBlock(ByVal wsDb As Worksheet, ByVal saveKey As String, _
                           ByVal curTasks As Variant, ByVal curNote As Variant)
    EnsureDbIndexes wsDb
    Dim dtBlock(1 To N_TASKS, 1 To 8) As Variant
    Dim r As Long
    For r = 1 To N_TASKS
        dtBlock(r, 1) = saveKey
        dtBlock(r, 2) = r
        dtBlock(r, 3) = IsCellChecked(curTasks(r, 1))
        dtBlock(r, 4) = curTasks(r, 2)
        dtBlock(r, 5) = curTasks(r, 3)
        dtBlock(r, 6) = curTasks(r, 4)
        dtBlock(r, 7) = curTasks(r, 5)
        If r = 1 Then
            dtBlock(r, 8) = curNote
        Else
            dtBlock(r, 8) = ""
        End If
    Next r

    Dim dstRow As Long
    dstRow = ColLookup(gDailyIndex, saveKey)
    If dstRow = 0 Then
        dstRow = gDailyNextRow
        gDailyNextRow = gDailyNextRow + N_TASKS
        ColPut gDailyIndex, saveKey, dstRow
    End If
    wsDb.Cells(dstRow, 59).Resize(N_TASKS, 1).NumberFormat = "@"
    wsDb.Cells(dstRow, 59).Resize(N_TASKS, 8).Value2 = dtBlock
End Sub

Public Sub MarkMonthlyDirty()
    gDirtyMonthly = True
End Sub

Public Sub HandleTrackerMetaEdit(ByVal ws As Worksheet)
    On Error GoTo SafeExit
    gDirtyMonthly = True
    Application.ScreenUpdating = False
    SyncAllMonthlySprites ws, ThisWorkbook.Worksheets(CALC_SHEET)
SafeExit:
    Application.ScreenUpdating = True
End Sub

Public Sub MarkDailyDirty()
    gDirtyDaily = True
End Sub

Public Sub HandleDailyMetaEdit(ByVal ws As Worksheet)
    On Error GoTo SafeExit
    gDirtyDaily = True
    Application.ScreenUpdating = False
    SyncDailyTaskSprite ws, ThisWorkbook.Worksheets(CALC_SHEET)
SafeExit:
    Application.ScreenUpdating = True
End Sub

Public Sub MarkGoalsDirty()
    gDirtyGoals = True
End Sub

Public Sub HandleGoalsMetaEdit(ByVal ws As Worksheet)
    On Error GoTo SafeExit
    gDirtyGoals = True
    Application.ScreenUpdating = False
    SyncGoalsSprite ws, ThisWorkbook.Worksheets(CALC_SHEET)
SafeExit:
    Application.ScreenUpdating = True
End Sub

Public Sub FlushAllDirty()
    If Not gDirtyMonthly And Not gDirtyDaily And Not gDirtyGoals Then Exit Sub
    On Error GoTo SafeExit
    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)
    EnsureDbIndexes wsDb

    Dim prevEv As Boolean, prevCalc As XlCalculation
    prevEv = Application.EnableEvents
    prevCalc = Application.Calculation
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual

    If gDirtyMonthly Then
        Dim wsTr As Worksheet
        Set wsTr = GetAnchorSheet("ANCHOR_TRACKER")
        If Not wsTr Is Nothing Then
            Dim mKey As String
            mKey = KeyToString(wsCalc.Range("AN2").Value2)
            If Len(mKey) = 7 Then
                Dim curNames As Variant, curGoals As Variant, curGrid As Variant
                curNames = wsTr.Range("B17:B36").Value2
                curGoals = wsTr.Range("AI17:AI36").Value2
                curGrid = wsTr.Range("C17:AG36").Value2
                Dim saveGrid(1 To N_HABITS, 1 To 31) As Boolean
                Dim r As Long, d As Long
                For r = 1 To N_HABITS
                    For d = 1 To 31
                        saveGrid(r, d) = IsCellChecked(curGrid(r, d))
                    Next d
                Next r
                SaveMonthBlock wsDb, mKey, curNames, curGoals, saveGrid
            End If
        End If
        gDirtyMonthly = False
    End If

    If gDirtyGoals Then
        Dim wsYg As Worksheet
        Set wsYg = GetAnchorSheet("ANCHOR_GOALS")
        If Not wsYg Is Nothing Then
            Dim gYr As Long
            gYr = CLng(Val(wsCalc.Range("AN3").Value2))
            If gYr >= 2000 And gYr <= 2100 Then
                SaveGoalsBlock wsDb, gYr, wsYg.Range("B6:F25").Value2
            End If
        End If
        gDirtyGoals = False
    End If

    If gDirtyDaily Then
        Dim wsDt As Worksheet
        Set wsDt = GetAnchorSheet("ANCHOR_DAILYTASKS")
        If Not wsDt Is Nothing Then
            Dim dKey As String
            dKey = KeyToString(wsCalc.Range("AN12").Value2)
            If Len(dKey) = 10 Then
                SaveDailyBlock wsDb, dKey, wsDt.Range("B9:F28").Value2, wsDt.Range("B31").Value2
            End If
        End If
        gDirtyDaily = False
    End If

SafeExit:
    Application.Calculation = prevCalc
    Application.EnableEvents = prevEv
End Sub

' =============================================================================
'  PUBLIC: LIFECYCLE & O(1) CLEANUP (CALLED BY ThisWorkbook)
' =============================================================================
Public Sub InitWorkbookFastMode()
    On Error Resume Next
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        ws.DisplayPageBreaks = False
    Next ws
    CleanupAllFX
    gDirtyMonthly = False
    gDirtyDaily = False
    gDirtyGoals = False
    gDbIndexed = False
    EnsureDbIndexes ThisWorkbook.Worksheets(DB_SHEET)
    InitSpriteCachesFromCalc

    Dim wsAnn As Worksheet
    Set wsAnn = GetAnchorSheet("ANCHOR_ANNUAL")
    If Not wsAnn Is Nothing Then
        If ActiveSheet Is Nothing Then
            wsAnn.EnableCalculation = False
        ElseIf ActiveSheet.Name <> wsAnn.Name Then
            wsAnn.EnableCalculation = False
        End If
    End If
    Application.Calculation = xlCalculationAutomatic
    On Error GoTo 0
End Sub

Public Sub CleanupParticles(ByVal ws As Worksheet)
    On Error Resume Next
    Dim k As Long
    For k = 1 To 10
        ws.Shapes("FX_PARTICLE_" & CStr(k)).Delete
    Next k
    On Error GoTo 0
End Sub

Private Function GetCalcSheet() As Worksheet
    If gWsCalc Is Nothing Then Set gWsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set GetCalcSheet = gWsCalc
End Function

Private Function GetDbSheet() As Worksheet
    If gWsDb Is Nothing Then Set gWsDb = ThisWorkbook.Worksheets(DB_SHEET)
    Set GetDbSheet = gWsDb
End Function

Public Sub CleanupToasts()
    On Error Resume Next
    If gToastScheduled Then
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=False
        gToastScheduled = False
    End If
    If Not gToastShp Is Nothing Then
        gToastShp.Visible = MSO_FALSE
    ElseIf Len(gToastSheetName) > 0 Then
        ThisWorkbook.Worksheets(gToastSheetName).Shapes("FX_TOAST").Visible = MSO_FALSE
    End If
    On Error GoTo 0
End Sub

Public Sub CleanupAllFX()
    On Error Resume Next
    If gToastScheduled Then
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=False
        gToastScheduled = False
    End If
    Set gToastShp = Nothing
    gToastSheetName = ""
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        ws.Shapes("FX_TOAST").Delete
        CleanupParticles ws
    Next ws
    Dim wsAnn As Worksheet
    Set wsAnn = GetAnchorSheet("ANCHOR_ANNUAL")
    If Not wsAnn Is Nothing Then wsAnn.EnableCalculation = True
    On Error GoTo 0
End Sub

Public Sub DismissToast()
    CleanupToasts
End Sub

' =============================================================================
'  EFFECT 1: HERO MASCOT CELEBRATION BOUNCE (EXACT RESTORE GUARANTEED!)
' =============================================================================
Public Sub PlayHeroBounce(ByVal ws As Worksheet, ByVal shapeName As String)
    If Not IsFXEnabled() Then Exit Sub
    Dim shp As Shape
    On Error Resume Next
    Set shp = ws.Shapes(shapeName)
    On Error GoTo 0
    If shp Is Nothing Then Exit Sub

    Dim origL As Single, origT As Single, origW As Single, origH As Single
    Dim cx As Single, cy As Single
    origL = shp.Left
    origT = shp.Top
    origW = shp.Width
    origH = shp.Height
    cx = origL + origW / 2!
    cy = origT + origH / 2!

    On Error GoTo RestoreHero
    Application.ScreenUpdating = True

    Dim frames As Variant
    frames = Array(1#, 1.15, 0.95, 1.07, 0.99, 1#)
    Dim i As Long, sc As Double, nw As Single
    For i = LBound(frames) To UBound(frames)
        sc = CDbl(frames(i))
        nw = CSng(origW * sc)
        shp.Width = nw
        shp.Left = cx - shp.Width / 2!
        shp.Top = cy - shp.Height / 2!
        WaitSec 0.042
    Next i

RestoreHero:
    On Error Resume Next
    shp.Width = origW
    shp.Height = origH
    shp.Left = origL
    shp.Top = origT
    On Error GoTo 0
End Sub

' =============================================================================
'  EFFECT 2: FLOATING PASTEL SPARKLE / HEART / STAR BURST (ZERO ORPHANS!)
' =============================================================================
Public Sub PlaySparkleBurst(ByVal ws As Worksheet, ByVal anchorShapeName As String)
    If Not IsFXEnabled() Then Exit Sub
    CleanupParticles ws

    Dim cx As Single, cy As Single
    Dim anchorShp As Shape
    On Error Resume Next
    Set anchorShp = ws.Shapes(anchorShapeName)
    On Error GoTo 0
    If Not anchorShp Is Nothing Then
        cx = anchorShp.Left + anchorShp.Width / 2!
        cy = anchorShp.Top + anchorShp.Height / 2!
    Else
        cx = ws.Range("AG9").Left
        cy = ws.Range("AG9").Top
    End If

    Dim c1 As Long, c2 As Long, c3 As Long, c4 As Long, c5 As Long
    c1 = GetThemeRgb(2, RGB(232, 106, 146))
    c2 = GetThemeRgb(3, RGB(140, 60, 90))
    c3 = GetThemeRgb(5, RGB(244, 165, 194))
    c4 = RGB(251, 191, 36)
    c5 = RGB(244, 114, 182)
    Dim palette As Variant
    palette = Array(c1, c4, c3, c5, c2, c4, c1, c5, c3, c4)
    Dim kinds As Variant
    kinds = Array(MSO_STAR_4, MSO_STAR_5, MSO_HEART, MSO_STAR_4, MSO_STAR_5, _
                  MSO_HEART, MSO_STAR_4, MSO_STAR_5, MSO_HEART, MSO_STAR_4)

    Dim pShp(1 To 10) As Shape
    Dim vx(1 To 10) As Single
    Dim vy(1 To 10) As Single
    Dim sz(1 To 10) As Single
    Dim k As Long, ang As Double, spd As Single

    On Error GoTo WipeParticles
    Application.ScreenUpdating = True
    For k = 1 To 10
        ang = (k - 1) * (6.2831853 / 10#) - 0.3
        spd = 2.8! + (k Mod 3) * 1.1!
        vx(k) = CSng(Cos(ang) * spd)
        vy(k) = CSng(Sin(ang) * spd - 1.8)
        sz(k) = 10! + (k Mod 3) * 3!
        Set pShp(k) = ws.Shapes.AddShape(CLng(kinds(k - 1)), cx - sz(k) / 2!, cy - sz(k) / 2!, sz(k), sz(k))
        pShp(k).Name = "FX_PARTICLE_" & CStr(k)
        pShp(k).Fill.Solid
        pShp(k).Fill.ForeColor.RGB = CLng(palette(k - 1))
        pShp(k).Line.Visible = MSO_FALSE
    Next k

    Dim f As Long, shrink As Single
    For f = 1 To 10
        shrink = 1! - (CSng(f) * 0.065!)
        For k = 1 To 10
            pShp(k).Left = pShp(k).Left + vx(k)
            pShp(k).Top = pShp(k).Top + vy(k)
            pShp(k).Width = sz(k) * shrink
            pShp(k).Height = sz(k) * shrink
        Next k
        WaitSec 0.04
    Next f

WipeParticles:
    CleanupParticles ws
End Sub

' =============================================================================
'  EFFECT 3: SLEEK NON-BLOCKING FLOATING TOAST BANNER (O(1) AUTO-DISMISS 2s)
' =============================================================================
Public Sub ShowToast(ByVal ws As Worksheet, ByVal msgText As String)
    If Len(Trim$(msgText)) = 0 Then Exit Sub
    On Error GoTo SafeExit

    If gToastScheduled Then
        On Error Resume Next
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=False
        gToastScheduled = False
        On Error GoTo SafeExit
    End If

    Dim toast As Shape
    If gToastSheetName = ws.Name And Not gToastShp Is Nothing Then
        On Error Resume Next
        Dim testNm As String
        testNm = gToastShp.Name
        If Err.Number = 0 Then Set toast = gToastShp
        Err.Clear
        On Error GoTo SafeExit
    End If

    If Not toast Is Nothing Then
        ' Ultra-fast O(1) toast reuse (~1ms instead of ~30ms AddShape!)
        toast.TextFrame2.TextRange.Text = msgText
        toast.Visible = MSO_TRUE
    Else
        If Len(gToastSheetName) > 0 And gToastSheetName <> ws.Name Then
            On Error Resume Next
            ThisWorkbook.Worksheets(gToastSheetName).Shapes("FX_TOAST").Visible = MSO_FALSE
            On Error GoTo SafeExit
        End If
        On Error Resume Next
        ws.Shapes("FX_TOAST").Delete
        On Error GoTo SafeExit

        Dim tLeft As Single, tTop As Single, tW As Single, tH As Single
        tW = 310!
        tH = 34!

        On Error Resume Next
        Dim visR As Range
        Set visR = ActiveWindow.VisibleRange
        If Not visR Is Nothing Then
            tLeft = visR.Left + visR.Width - tW - 18!
            tTop = visR.Top + 14!
        Else
            tLeft = ws.Range("T2").Left
            tTop = ws.Range("T2").Top + 8!
        End If
        If tLeft < 16! Then tLeft = 16!
        If tTop < 8! Then tTop = 8!
        On Error GoTo SafeExit

        Set toast = ws.Shapes.AddShape(MSO_ROUNDED_RECT, tLeft, tTop, tW, tH)
        toast.Name = "FX_TOAST"
        toast.Adjustments(1) = 0.4
        toast.Fill.Solid
        toast.Fill.ForeColor.RGB = GetThemeRgb(3, RGB(110, 60, 80))
        toast.Line.Visible = MSO_TRUE
        toast.Line.ForeColor.RGB = GetThemeRgb(4, RGB(250, 235, 240))
        toast.Line.Weight = 1.25

        With toast.TextFrame2
            .WordWrap = MSO_TRUE
            .VerticalAnchor = 3
            .MarginLeft = 10
            .MarginRight = 10
            .MarginTop = 3
            .MarginBottom = 3
            With .TextRange
                .Text = msgText
                .ParagraphFormat.Alignment = 2
                With .Font
                    .Name = "Segoe UI"
                    .Size = 9.5
                    .Bold = MSO_TRUE
                    .Fill.ForeColor.RGB = RGB(255, 255, 255)
                End With
            End With
        End With
        Set gToastShp = toast
        gToastSheetName = ws.Name
    End If

    gToastDueTime = Now + TimeSerial(0, 0, 2)
    gToastScheduled = True
    Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=True
SafeExit:
End Sub

' =============================================================================
'  PUBLIC: ULTRA-FAST SINGLE-TICK HANDLERS (ZERO _Database WRITES, < 40ms!)
' =============================================================================
Public Sub HandleTrackerTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    gDirtyMonthly = True

    Dim wsCalc As Worksheet
    Set wsCalc = GetCalcSheet()

    If Target.Cells.CountLarge = 1 Then
        ' Zero-repaint fast-path: only toggles ScreenUpdating if a stage actually changed!
        SyncSingleDayAndHero ws, wsCalc, Target.Column - 2
    Else
        Application.ScreenUpdating = False
        SyncAllMonthlySprites ws, wsCalc
        Application.ScreenUpdating = True
        Exit Sub
    End If

    If Not IsCellChecked(Target.Value2) Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub

    Dim dayPct As Variant
    dayPct = ws.Cells(12, Target.Column).Value2
    Dim hitPerfect As Boolean
    hitPerfect = (IsNumeric(dayPct) And Val(CStr(dayPct)) >= 0.999)

    Dim curBest As Long, prevCel As Long, hitStreak As Long
    curBest = CLng(Val(wsCalc.Range("C11").Value2))
    prevCel = CLng(Val(wsCalc.Range("BA6").Value2))
    hitStreak = 0
    If (curBest = 7 Or curBest = 14 Or curBest = 21 Or curBest = 30) And curBest > prevCel Then
        hitStreak = curBest
        Application.EnableEvents = False
        wsCalc.Range("BA6").Value2 = curBest
        Application.EnableEvents = True
    End If

    Dim heroShpName As String
    heroShpName = GetSlotShapeName("SPR_MHERO_S", gLastMHero)
    If hitPerfect Then
        PlayHeroBounce ws, heroShpName
        PlaySparkleBurst ws, heroShpName
        ShowToast ws, GetFxMsg(8)
    ElseIf hitStreak > 0 Then
        PlayHeroBounce ws, heroShpName
        PlaySparkleBurst ws, heroShpName
        Select Case hitStreak
            Case 7:  ShowToast ws, GetFxMsg(9)
            Case 14: ShowToast ws, GetFxMsg(10)
            Case 21: ShowToast ws, GetFxMsg(11)
            Case 30: ShowToast ws, GetFxMsg(12)
        End Select
    End If
SafeExit:
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

Public Sub HandleDailyTaskTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    gDirtyDaily = True

    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)

    Application.ScreenUpdating = False
    SyncDailyTaskSprite ws, wsCalc
    Application.ScreenUpdating = True

    If Target.Cells.CountLarge <> 1 Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub
    If Not IsCellChecked(Target.Value2) Then Exit Sub

    Dim dtPct As Variant, dtTot As Variant
    dtPct = wsCalc.Range("AN15").Value2
    dtTot = wsCalc.Range("AN14").Value2
    If IsNumeric(dtPct) And IsNumeric(dtTot) Then
        If CLng(dtTot) > 0 And CDbl(dtPct) >= 0.999 Then
            Dim heroShpName As String
            heroShpName = GetSlotShapeName("SPR_DHERO_S", gLastDHero)
            PlayHeroBounce ws, heroShpName
            PlaySparkleBurst ws, heroShpName
            ShowToast ws, GetFxMsg(14)
        End If
    End If
SafeExit:
    Application.ScreenUpdating = True
End Sub

Public Sub HandleYearlyGoalTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    gDirtyGoals = True

    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)

    Application.ScreenUpdating = False
    SyncGoalsSprite ws, wsCalc
    Application.ScreenUpdating = True

    If Target.Cells.CountLarge <> 1 Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub
    If Not IsCellChecked(Target.Value2) Then Exit Sub

    Dim hitAll As Boolean, ygPct As Variant
    ygPct = wsCalc.Range("AN6").Value2
    hitAll = (IsNumeric(ygPct) And Val(CStr(ygPct)) >= 0.999)

    Dim heroShpName As String
    heroShpName = GetSlotShapeName("SPR_GHERO_S", gLastGHero)
    PlayHeroBounce ws, heroShpName
    If hitAll Then PlaySparkleBurst ws, heroShpName
    ShowToast ws, GetFxMsg(15)
SafeExit:
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  PUBLIC: DEFERRED ANNUAL RECALC, LAZY-FLUSH SYNC & HALL SPOTLIGHT
' =============================================================================
Public Sub HandleSheetActivate(ByVal Sh As Object)
    On Error GoTo SafeExit
    If Not TypeOf Sh Is Worksheet Then Exit Sub
    Dim ws As Worksheet
    Set ws = Sh
    ws.DisplayPageBreaks = False

    Dim wsAnn As Worksheet
    Set wsAnn = GetAnchorSheet("ANCHOR_ANNUAL")
    If wsAnn Is Nothing Then Exit Sub

    If ws.Name <> wsAnn.Name Then
        wsAnn.EnableCalculation = False
        Exit Sub
    End If

    Dim prevCalc As XlCalculation, prevAnim As Boolean
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo SafeExit
    Application.ScreenUpdating = False
    Application.EnableEvents = False

    ' Flush any lazy-dirty edits from Monthly / Daily / Goals before refreshing Annual Hall!
    FlushAllDirty

    wsAnn.EnableCalculation = True
    Application.Calculation = prevCalc
    SyncAnnualSprites wsAnn, ThisWorkbook.Worksheets(CALC_SHEET)

    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo SafeExit
    Application.ScreenUpdating = True

    If IsFXEnabled() Then
        Dim unlockedCnt As Long
        unlockedCnt = CLng(Application.WorksheetFunction.CountIf(wsAnn.Range("H35:H42"), ">=1"))
        If unlockedCnt > 0 Then
            PlayHeroBounce wsAnn, GetSlotShapeName("SPR_AHERO_S", gLastAHero)
        End If
    End If
    Exit Sub

SafeExit:
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
End Sub

Public Sub HandleAnnualYearSwitch(ByVal ws As Worksheet)
    On Error GoTo SafeExit
    Dim prevCalc As XlCalculation, prevAnim As Boolean
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo SafeExit
    Application.ScreenUpdating = False
    Application.EnableEvents = False

    ws.EnableCalculation = True
    Application.Calculation = prevCalc
    SyncAnnualSprites ws, ThisWorkbook.Worksheets(CALC_SHEET)

SafeExit:
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  EFFECT 4: QUICK-ACTION PASTEL PILL BUTTON MACROS (100% PURE ASCII!)
' =============================================================================
Private Sub StepMonthBy(ByVal delta As Long)
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_TRACKER")
    If ws Is Nothing Then Exit Sub

    Dim curM As Long, curY As Long
    curM = MonthNameToNum(CStr(ws.Range("B3").Value2))
    curY = CLng(Val(ws.Range("B5").Value2))
    If curM = 0 Then curM = 10
    If curY < 2024 Or curY > 2040 Then curY = 2026

    curM = curM + delta
    If curM > 12 Then
        curM = 1
        curY = curY + 1
    ElseIf curM < 1 Then
        curM = 12
        curY = curY - 1
    End If
    If curY < 2024 Then curY = 2024
    If curY > 2040 Then curY = 2040

    Dim prevCalc As XlCalculation
    prevCalc = Application.Calculation
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.Range("B3").Value2 = NumToMonthName(curM)
    ws.Range("B5").Value2 = curY
    HandleMonthlySwitch ws
    If Application.Calculation <> prevCalc Then Application.Calculation = prevCalc
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

Public Sub BtnPrevMonth()
    StepMonthBy -1
End Sub

Public Sub BtnNextMonth()
    StepMonthBy 1
End Sub

Public Sub BtnToggleFX()
    On Error GoTo SafeExit
    Dim wsCalc As Worksheet, wsTr As Worksheet
    Set wsCalc = GetCalcSheet()
    Set wsTr = GetAnchorSheet("ANCHOR_TRACKER")

    Dim newState As Boolean
    gFXCached = False
    newState = Not IsFXEnabled()
    wsCalc.Range("BA1").Value2 = newState
    gFXVal = newState
    gFXCached = True

    If Not wsTr Is Nothing Then
        Dim btn As Shape
        On Error Resume Next
        Set btn = wsTr.Shapes("BTN_FX_TOGGLE")
        On Error GoTo SafeExit
        If Not btn Is Nothing Then
            If newState Then
                btn.TextFrame2.TextRange.Text = GetFxMsg(17)
                btn.Fill.ForeColor.RGB = GetThemeRgb(2, RGB(232, 106, 146))
                btn.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = RGB(255, 255, 255)
            Else
                btn.TextFrame2.TextRange.Text = GetFxMsg(18)
                btn.Fill.ForeColor.RGB = RGB(229, 231, 235)
                btn.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = RGB(75, 85, 99)
            End If
        End If
        If newState Then
            ShowToast wsTr, GetFxMsg(19)
        Else
            ShowToast wsTr, GetFxMsg(20)
        End If
    End If
SafeExit:
End Sub

Private Sub SetDailyTasksDate(ByVal targetDate As Date)
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If ws Is Nothing Then Exit Sub

    Dim y As Long, m As Long, d As Long
    y = Year(targetDate)
    m = Month(targetDate)
    d = Day(targetDate)
    If y < 2024 Then y = 2024
    If y > 2040 Then y = 2040

    Dim prevCalc As XlCalculation
    prevCalc = Application.Calculation
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.Range("D5").Value2 = d
    ws.Range("E5").Value2 = NumToMonthName(m)
    ws.Range("F5").Value2 = y
    HandleDailyTasksSwitch ws
    If Application.Calculation <> prevCalc Then Application.Calculation = prevCalc
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

Public Sub BtnPrevDay()
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If ws Is Nothing Then Exit Sub
    Dim curD As Long, curM As Long, curY As Long
    curD = CLng(Val(ws.Range("D5").Value2))
    curM = MonthNameToNum(CStr(ws.Range("E5").Value2))
    curY = CLng(Val(ws.Range("F5").Value2))
    If curM = 0 Or curD < 1 Or curY < 2000 Then Exit Sub
    SetDailyTasksDate DateAdd("d", -1, DateSerial(curY, curM, curD))
End Sub

Public Sub BtnNextDay()
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If ws Is Nothing Then Exit Sub
    Dim curD As Long, curM As Long, curY As Long
    curD = CLng(Val(ws.Range("D5").Value2))
    curM = MonthNameToNum(CStr(ws.Range("E5").Value2))
    curY = CLng(Val(ws.Range("F5").Value2))
    If curM = 0 Or curD < 1 Or curY < 2000 Then Exit Sub
    SetDailyTasksDate DateAdd("d", 1, DateSerial(curY, curM, curD))
End Sub

Public Sub BtnToday()
    SetDailyTasksDate Date
End Sub

Public Sub BtnDemoFX()
    On Error GoTo SafeExit
    Dim wsG As Worksheet
    Set wsG = GetAnchorSheet("ANCHOR_GUIDE")
    If wsG Is Nothing Then Set wsG = ActiveSheet
    Dim prevFX As Boolean
    prevFX = IsFXEnabled()
    GetCalcSheet().Range("BA1").Value2 = True
    gFXVal = True
    gFXCached = True
    PlayHeroBounce wsG, "Guide_Stage5"
    PlaySparkleBurst wsG, "Guide_Stage5"
    ShowToast wsG, GetFxMsg(16)
    GetCalcSheet().Range("BA1").Value2 = prevFX
    gFXVal = prevFX
SafeExit:
End Sub

' =============================================================================
'  1-CLICK CUSTOM `_Assets` SPRITE SYNC MACRO (`SyncSpritesFromAssets`)
'  Allows users who replace custom PNGs in `_Assets!B2:B7` to refresh ALL
'  native pre-placed sprite stacks across all 5 visible tabs in 1 click!
' =============================================================================
Private Sub ReplaceSheetSpritesFromAssets(ByVal ws As Worksheet, ByRef assetShp() As Shape)
    Dim targets() As String
    Dim tStage() As Long
    Dim tL() As Single, tT() As Single, tW() As Single, tH() As Single
    Dim tVis() As Long
    Dim cnt As Long
    cnt = 0

    Dim shp As Shape, nm As String, stChar As String, stIdx As Long
    For Each shp In ws.Shapes
        nm = shp.Name
        stIdx = -1
        If Left$(nm, 4) = "SPR_" And InStr(nm, "_S") > 0 Then
            stChar = Right$(nm, 1)
            If stChar >= "0" And stChar <= "5" Then stIdx = CLng(stChar)
        ElseIf Left$(nm, 11) = "Guide_Stage" Then
            stChar = Right$(nm, 1)
            If stChar >= "0" And stChar <= "5" Then stIdx = CLng(stChar)
        End If
        If stIdx >= 0 And stIdx <= 5 Then
            If Not assetShp(stIdx) Is Nothing Then
                cnt = cnt + 1
                ReDim Preserve targets(1 To cnt)
                ReDim Preserve tStage(1 To cnt)
                ReDim Preserve tL(1 To cnt)
                ReDim Preserve tT(1 To cnt)
                ReDim Preserve tW(1 To cnt)
                ReDim Preserve tH(1 To cnt)
                ReDim Preserve tVis(1 To cnt)
                targets(cnt) = nm
                tStage(cnt) = stIdx
                tL(cnt) = shp.Left
                tT(cnt) = shp.Top
                tW(cnt) = shp.Width
                tH(cnt) = shp.Height
                tVis(cnt) = shp.Visible
            End If
        End If
    Next shp

    If cnt = 0 Then Exit Sub

    Dim prevVis As XlSheetVisibility
    prevVis = ws.Visible
    ws.Visible = xlSheetVisible
    ws.Activate

    Dim i As Long, k As Long
    Dim newShp As Shape
    For k = 0 To 5
        If Not assetShp(k) Is Nothing Then
            assetShp(k).Copy
            For i = 1 To cnt
                If tStage(i) = k Then
                    ws.Paste
                    Set newShp = ws.Shapes(ws.Shapes.Count)
                    newShp.Line.Visible = MSO_FALSE
                    newShp.LockAspectRatio = MSO_TRUE
                    newShp.Width = tW(i)
                    If newShp.Height > tH(i) Then newShp.Height = tH(i)
                    newShp.Left = tL(i) + (tW(i) - newShp.Width) / 2!
                    newShp.Top = tT(i) + (tH(i) - newShp.Height) / 2!
                    newShp.Placement = xlMoveAndSize
                    newShp.Visible = tVis(i)
                    On Error Resume Next
                    ws.Shapes(targets(i)).Delete
                    On Error GoTo 0
                    newShp.Name = targets(i)
                End If
            Next i
        End If
    Next k
    Application.CutCopyMode = False
    ws.Visible = prevVis
End Sub

Public Sub SyncSpritesFromAssets()
    On Error GoTo Cleanup
    Dim wsAssets As Worksheet
    Set wsAssets = ThisWorkbook.Worksheets(ASSETS_SHEET)

    Dim prevCalc As XlCalculation, prevAnim As Boolean, prevActive As Worksheet
    Set prevActive = ActiveSheet
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual

    Dim prevAssVis As XlSheetVisibility
    prevAssVis = wsAssets.Visible
    wsAssets.Visible = xlSheetVisible

    ' Locate the 6 user shapes in `_Assets!B2:B7` (row 2..7 -> stage 0..5)
    Dim assetShp(0 To 5) As Shape
    Dim shp As Shape, rr As Long
    For Each shp In wsAssets.Shapes
        If Left$(shp.Name, 4) <> "BTN_" Then
            rr = shp.TopLeftCell.Row
            If rr >= 2 And rr <= 7 And shp.TopLeftCell.Column <= 3 Then
                Set assetShp(rr - 2) = shp
            End If
        End If
    Next shp

    Dim anchors As Variant, idx As Long, wsT As Worksheet
    anchors = Array("ANCHOR_GUIDE", "ANCHOR_TRACKER", "ANCHOR_DAILYTASKS", "ANCHOR_GOALS", "ANCHOR_ANNUAL")
    For idx = LBound(anchors) To UBound(anchors)
        Set wsT = GetAnchorSheet(CStr(anchors(idx)))
        If Not wsT Is Nothing Then
            ReplaceSheetSpritesFromAssets wsT, assetShp
        End If
    Next idx

    wsAssets.Visible = prevAssVis
    If Not prevActive Is Nothing Then
        If prevActive.Visible = xlSheetVisible Then prevActive.Activate
    End If

    ResetSpriteCaches
    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsT = GetAnchorSheet("ANCHOR_TRACKER")
    If Not wsT Is Nothing Then SyncAllMonthlySprites wsT, wsCalc
    Set wsT = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If Not wsT Is Nothing Then SyncDailyTaskSprite wsT, wsCalc
    Set wsT = GetAnchorSheet("ANCHOR_GOALS")
    If Not wsT Is Nothing Then SyncGoalsSprite wsT, wsCalc
    Set wsT = GetAnchorSheet("ANCHOR_ANNUAL")
    If Not wsT Is Nothing Then SyncAnnualSprites wsT, wsCalc

Cleanup:
    Application.Calculation = prevCalc
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
    If Not ActiveSheet Is Nothing Then
        ShowToast ActiveSheet, GetFxMsg(23)
    End If
End Sub

' =============================================================================
'  PUBLIC: MONTHLY SWITCH (B3 Month / B5 Year -> SUB-150ms O(1) TURBO SWAP!)
' =============================================================================
Public Sub HandleMonthlySwitch(ByVal ws As Worksheet)
    Dim prevCalc As XlCalculation, prevAnim As Boolean
    Dim didSwitch As Boolean
    didSwitch = False

    On Error GoTo Cleanup
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim newM As Long, newY As Long
    newM = MonthNameToNum(CStr(ws.Range("B3").Value2))
    newY = CLng(Val(ws.Range("B5").Value2))
    If newM = 0 Or newY < 2000 Or newY > 2100 Then GoTo Cleanup

    Dim newKey As String, lastKey As String
    newKey = Format$(newY, "0000") & "-" & Format$(newM, "00")
    lastKey = KeyToString(wsCalc.Range("AN2").Value2)
    If lastKey = newKey Then GoTo Cleanup

    EnsureDbIndexes wsDb

    Dim curNames As Variant, curGoals As Variant, curGrid As Variant
    curNames = ws.Range("B17:B36").Value2
    curGoals = ws.Range("AI17:AI36").Value2
    curGrid = ws.Range("C17:AG36").Value2

    Dim r As Long, d As Long
    If Len(lastKey) = 7 Then
        If gDirtyMonthly Or ColLookup(gMonthIndex, lastKey) = 0 Then
            Dim saveGrid(1 To N_HABITS, 1 To 31) As Boolean
            For r = 1 To N_HABITS
                For d = 1 To 31
                    saveGrid(r, d) = IsCellChecked(curGrid(r, d))
                Next d
            Next r
            SaveMonthBlock wsDb, lastKey, curNames, curGoals, saveGrid
        End If
        gDirtyMonthly = False
    End If

    Dim srcRow As Long
    srcRow = ColLookup(gMonthIndex, newKey)
    Dim loadGrid(1 To N_HABITS, 1 To 31) As Variant
    Dim gridChanged As Boolean
    gridChanged = False

    If srcRow > 0 Then
        Dim srcBlock As Variant
        srcBlock = wsDb.Cells(srcRow, 1).Resize(N_HABITS, 35).Value2
        Dim loadNames(1 To N_HABITS, 1 To 1) As Variant
        Dim loadGoals(1 To N_HABITS, 1 To 1) As Variant
        Dim hasAnyName As Boolean, namesDiff As Boolean, goalsDiff As Boolean
        hasAnyName = False: namesDiff = False: goalsDiff = False

        For r = 1 To N_HABITS
            loadNames(r, 1) = srcBlock(r, 3)
            loadGoals(r, 1) = srcBlock(r, 4)
            If Len(Trim$(CStr(srcBlock(r, 3)))) > 0 Then hasAnyName = True
            If CStr(curNames(r, 1)) <> CStr(loadNames(r, 1)) Then namesDiff = True
            If CStr(curGoals(r, 1)) <> CStr(loadGoals(r, 1)) Then goalsDiff = True
            For d = 1 To 31
                If r <= N_FORM_ROWS Then
                    loadGrid(r, d) = IsCellChecked(srcBlock(r, 4 + d))
                    If IsCellChecked(curGrid(r, d)) <> CBool(loadGrid(r, d)) Then gridChanged = True
                Else
                    If IsCellChecked(srcBlock(r, 4 + d)) Then
                        loadGrid(r, d) = ChrW$(10003)
                    Else
                        loadGrid(r, d) = ""
                    End If
                    If CStr(curGrid(r, d)) <> CStr(loadGrid(r, d)) Then gridChanged = True
                End If
            Next d
        Next r

        If hasAnyName And namesDiff Then ws.Range("B17:B36").Value2 = loadNames
        If hasAnyName And goalsDiff Then ws.Range("AI17:AI36").Value2 = loadGoals
        If gridChanged Then ws.Range("C17:AG36").Value2 = loadGrid
    Else
        For r = 1 To N_HABITS
            For d = 1 To 31
                If r <= N_FORM_ROWS Then
                    loadGrid(r, d) = False
                    If IsCellChecked(curGrid(r, d)) Then gridChanged = True
                Else
                    loadGrid(r, d) = ""
                    If Len(CStr(curGrid(r, d))) > 0 Then gridChanged = True
                End If
            Next d
        Next r
        If gridChanged Then ws.Range("C17:AG36").Value2 = loadGrid
    End If

    wsCalc.Range("AN2").NumberFormat = "@"
    wsCalc.Range("AN2").Value2 = newKey
    wsCalc.Range("BA6").Value2 = 0

    ' Single native incremental calc while ScreenUpdating = False -> then O(1) sprite diff!
    Application.Calculation = xlCalculationAutomatic
    SyncAllMonthlySprites ws, wsCalc

    didSwitch = True
    If IsFXEnabled() Then
        ShowToast ws, GetFxMsg(13)
    End If

Cleanup:
    If Application.Calculation <> xlCalculationAutomatic Then Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  PUBLIC: YEARLY GOALS SWITCH (I2 Year -> SUB-150ms O(1) TURBO SWAP!)
' =============================================================================
Public Sub HandleYearlyGoalsSwitch(ByVal ws As Worksheet)
    Dim prevCalc As XlCalculation, prevAnim As Boolean

    On Error GoTo Cleanup
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim oldYr As Long, newYr As Long
    oldYr = CLng(Val(wsCalc.Range("AN3").Value2))
    newYr = CLng(Val(ws.Range("I2").Value2))
    If newYr < 2000 Or newYr > 2100 Or oldYr = newYr Then GoTo Cleanup

    EnsureDbIndexes wsDb

    If oldYr >= 2000 Then
        If gDirtyGoals Or ColLookup(gGoalsIndex, CStr(oldYr)) = 0 Then
            SaveGoalsBlock wsDb, oldYr, ws.Range("B6:F25").Value2
        End If
        gDirtyGoals = False
    End If

    Dim srcYGRow As Long
    srcYGRow = ColLookup(gGoalsIndex, CStr(newYr))
    Dim loadYG(1 To N_GOALS, 1 To 5) As Variant
    Dim i As Long
    If srcYGRow > 0 Then
        Dim srcYG As Variant
        srcYG = wsDb.Cells(srcYGRow, 47).Resize(N_GOALS, 7).Value2
        For i = 1 To N_GOALS
            loadYG(i, 1) = IsCellChecked(srcYG(i, 3))
            loadYG(i, 2) = srcYG(i, 4)
            loadYG(i, 3) = srcYG(i, 5)
            loadYG(i, 4) = srcYG(i, 6)
            loadYG(i, 5) = srcYG(i, 7)
        Next i
    Else
        For i = 1 To N_GOALS
            loadYG(i, 1) = False
            loadYG(i, 2) = ""
            loadYG(i, 3) = ""
            loadYG(i, 4) = ""
            loadYG(i, 5) = ""
        Next i
    End If
    ws.Range("B6:F25").Value2 = loadYG
    wsCalc.Range("AN3").Value2 = newYr

    Application.Calculation = prevCalc
    SyncGoalsSprite ws, wsCalc

Cleanup:
    If Application.Calculation <> prevCalc Then Application.Calculation = prevCalc
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  PUBLIC: DAILY TASKS DATE SWITCH (D5:F5 -> SUB-150ms O(1) TURBO SWAP!)
' =============================================================================
Public Sub HandleDailyTasksSwitch(ByVal ws As Worksheet)
    Dim prevCalc As XlCalculation, prevAnim As Boolean
    Dim didDateSwitch As Boolean
    didDateSwitch = False

    On Error GoTo Cleanup
    prevCalc = Application.Calculation
    On Error Resume Next
    prevAnim = Application.EnableAnimations
    Application.EnableAnimations = False
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim newDay As Long, newMonth As Long, newYear As Long
    newDay = CLng(Val(ws.Range("D5").Value2))
    newMonth = MonthNameToNum(CStr(ws.Range("E5").Value2))
    newYear = CLng(Val(ws.Range("F5").Value2))
    If newDay < 1 Or newMonth = 0 Or newYear < 2000 Or newYear > 2100 Then GoTo Cleanup

    Dim maxDay As Long
    maxDay = Day(DateSerial(newYear, newMonth + 1, 0))
    If newDay > maxDay Then
        newDay = maxDay
        ws.Range("D5").Value2 = newDay
    End If

    Dim newKey As String, lastKey As String
    newKey = Format$(newYear, "0000") & "-" & Format$(newMonth, "00") & "-" & Format$(newDay, "00")
    lastKey = KeyToString(wsCalc.Range("AN12").Value2)
    If lastKey = newKey Then GoTo Cleanup

    EnsureDbIndexes wsDb

    If Len(lastKey) = 10 Then
        If gDirtyDaily Or ColLookup(gDailyIndex, lastKey) = 0 Then
            SaveDailyBlock wsDb, lastKey, ws.Range("B9:F28").Value2, ws.Range("B31").Value2
        End If
        gDirtyDaily = False
    End If

    Dim srcRow As Long
    srcRow = ColLookup(gDailyIndex, newKey)
    Dim loadTasks(1 To N_TASKS, 1 To 5) As Variant
    Dim loadNote As Variant
    Dim i As Long
    If srcRow > 0 Then
        Dim srcArr As Variant
        srcArr = wsDb.Cells(srcRow, 59).Resize(N_TASKS, 8).Value2
        For i = 1 To N_TASKS
            loadTasks(i, 1) = IsCellChecked(srcArr(i, 3))
            loadTasks(i, 2) = srcArr(i, 4)
            loadTasks(i, 3) = srcArr(i, 5)
            loadTasks(i, 4) = srcArr(i, 6)
            loadTasks(i, 5) = srcArr(i, 7)
        Next i
        loadNote = srcArr(1, 8)
    Else
        For i = 1 To N_TASKS
            loadTasks(i, 1) = False
            loadTasks(i, 2) = ""
            loadTasks(i, 3) = ""
            loadTasks(i, 4) = ""
            loadTasks(i, 5) = ""
        Next i
        loadNote = ""
    End If

    ws.Range("B9:F28").Value2 = loadTasks
    ws.Range("B31").Value2 = loadNote
    wsCalc.Range("AN12").NumberFormat = "@"
    wsCalc.Range("AN12").Value2 = newKey

    Application.Calculation = xlCalculationAutomatic
    SyncDailyTaskSprite ws, wsCalc

    didDateSwitch = True
    If IsFXEnabled() Then
        ShowToast ws, GetFxMsg(21)
    End If

Cleanup:
    If Application.Calculation <> xlCalculationAutomatic Then Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    On Error Resume Next
    Application.EnableAnimations = prevAnim
    On Error GoTo 0
    Application.ScreenUpdating = True
End Sub
