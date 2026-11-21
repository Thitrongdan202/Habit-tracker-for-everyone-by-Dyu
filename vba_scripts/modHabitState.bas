Attribute VB_Name = "modHabitState"
Option Explicit

' =============================================================================
'  modHabitState -- Habit Tracker v3.5 Ultra-Smooth Persistence + Rich FX Engine
'  ---------------------------------------------------------------------------
'  - 100% PURE ASCII VBA (ZERO Vietnamese/Emoji string literals in VBA code!)
'    All Vietnamese Toast/Button texts live in hidden `_Calc!BA8:BA22`.
'  - 100% bulk in-memory 2D Variant array read/write (ZERO cell-by-cell loops)
'  - Active-sheet-only smart recalc on checkbox ticks + DisplayPageBreaks=False
'  - Rich toggleable FX Suite (Hero Bounce, Sparkle Burst, Non-Blocking Toast,
'    Quick-Action Month/Date/FX Pill Buttons, Annual Hall Spotlight)
'  - Guaranteed Cleanup blocks -> ZERO orphan FX_PARTICLE_* / FX_TOAST shapes!
' =============================================================================

Private Const CALC_SHEET As String = "_Calc"
Private Const DB_SHEET As String = "_Database"
Private Const N_HABITS As Long = 20
Private Const N_FORM_ROWS As Long = 20
Private Const N_GOALS As Long = 20

Private Const MSO_ROUNDED_RECT As Long = 5
Private Const MSO_HEART As Long = 21
Private Const MSO_STAR_5 As Long = 92
Private Const MSO_STAR_4 As Long = 187
Private Const MSO_FALSE As Long = 0
Private Const MSO_TRUE As Long = -1

Private gToastDueTime As Double
Private gToastScheduled As Boolean

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

Private Function GetAnchorSheet(ByVal anchorName As String) As Worksheet
    On Error Resume Next
    Set GetAnchorSheet = ThisWorkbook.Names(anchorName).RefersToRange.Worksheet
    On Error GoTo 0
End Function

Private Function GetGrownThreshold() As Double
    On Error Resume Next
    Dim v As Variant
    v = ThisWorkbook.Names("CFG_THR_3").RefersToRange.Value
    If IsNumeric(v) And CDbl(v) > 0 And CDbl(v) <= 1 Then
        GetGrownThreshold = CDbl(v)
    Else
        GetGrownThreshold = 0.75
    End If
    On Error GoTo 0
End Function

Public Function IsFXEnabled() As Boolean
    On Error Resume Next
    Dim v As Variant
    v = ThisWorkbook.Worksheets(CALC_SHEET).Range("BA1").Value
    If VarType(v) = vbBoolean Then
        IsFXEnabled = CBool(v)
    Else
        IsFXEnabled = True
    End If
    On Error GoTo 0
End Function

Private Function GetFxMsg(ByVal rowIdx As Long) As String
    On Error Resume Next
    GetFxMsg = CStr(ThisWorkbook.Worksheets(CALC_SHEET).Cells(rowIdx, 53).Value)
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
    s = CStr(ThisWorkbook.Worksheets(CALC_SHEET).Cells(calcRow, 53).Value)
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

Private Function FindBlockRow(ByVal wsDb As Worksheet, ByVal keyCol As Long, ByVal targetKey As String) As Long
    Dim lastRow As Long
    lastRow = wsDb.Cells(wsDb.Rows.Count, keyCol).End(xlUp).Row
    If lastRow < 2 Then
        FindBlockRow = 0
        Exit Function
    End If
    Dim arr As Variant
    arr = wsDb.Cells(2, keyCol).Resize(lastRow - 1, 1).Value
    Dim i As Long
    If lastRow = 2 Then
        If KeyToString(arr) = targetKey Then FindBlockRow = 2
        Exit Function
    End If
    For i = 1 To UBound(arr, 1) Step N_HABITS
        If KeyToString(arr(i, 1)) = targetKey Then
            FindBlockRow = i + 1
            Exit Function
        End If
    Next i
    FindBlockRow = 0
End Function

Private Function FindSummaryRow(ByVal wsDb As Worksheet, ByVal keyCol As Long, ByVal targetKey As String) As Long
    Dim lastRow As Long
    lastRow = wsDb.Cells(wsDb.Rows.Count, keyCol).End(xlUp).Row
    If lastRow < 2 Then
        FindSummaryRow = 0
        Exit Function
    End If
    Dim arr As Variant
    arr = wsDb.Cells(2, keyCol).Resize(lastRow - 1, 1).Value
    Dim i As Long
    If lastRow = 2 Then
        If KeyToString(arr) = targetKey Then FindSummaryRow = 2
        Exit Function
    End If
    For i = 1 To UBound(arr, 1)
        If KeyToString(arr(i, 1)) = targetKey Then
            FindSummaryRow = i + 1
            Exit Function
        End If
    Next i
    FindSummaryRow = 0
End Function

Private Sub SaveMonthBlock(ByVal wsDb As Worksheet, ByVal saveKey As String, _
                           ByVal namesArr As Variant, ByVal goalsArr As Variant, ByVal gridArr As Variant)
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
    dstRow = FindBlockRow(wsDb, 1, saveKey)
    If dstRow = 0 Then
        dstRow = wsDb.Cells(wsDb.Rows.Count, 1).End(xlUp).Row + 1
    End If
    wsDb.Cells(dstRow, 1).Resize(N_HABITS, 1).NumberFormat = "@"
    wsDb.Cells(dstRow, 1).Resize(N_HABITS, 35).Value = rawBlock

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
    sRow = FindSummaryRow(wsDb, 37, saveKey)
    If sRow = 0 Then
        sRow = wsDb.Cells(wsDb.Rows.Count, 37).End(xlUp).Row + 1
    End If
    wsDb.Cells(sRow, 37).NumberFormat = "@"
    wsDb.Cells(sRow, 37).Resize(1, 9).Value = sumRow
End Sub

' =============================================================================
'  PUBLIC: LIFECYCLE & CLEANUP (CALLED BY ThisWorkbook)
' =============================================================================
Public Sub InitWorkbookFastMode()
    On Error Resume Next
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        ws.DisplayPageBreaks = False
    Next ws
    CleanupAllFX
    Application.Calculation = xlCalculationAutomatic
    On Error GoTo 0
End Sub

Public Sub CleanupParticles(ByVal ws As Worksheet)
    On Error Resume Next
    Dim i As Long
    For i = ws.Shapes.Count To 1 Step -1
        If Left$(ws.Shapes(i).Name, 12) = "FX_PARTICLE_" Then
            ws.Shapes(i).Delete
        End If
    Next i
    On Error GoTo 0
End Sub

Public Sub CleanupToasts()
    On Error Resume Next
    If gToastScheduled Then
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=False
        gToastScheduled = False
    End If
    Dim ws As Worksheet, i As Long
    For Each ws In ThisWorkbook.Worksheets
        For i = ws.Shapes.Count To 1 Step -1
            If ws.Shapes(i).Name = "FX_TOAST" Then
                ws.Shapes(i).Delete
            End If
        Next i
    Next ws
    On Error GoTo 0
End Sub

Public Sub CleanupAllFX()
    On Error Resume Next
    CleanupToasts
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
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
    Dim i As Long, sc As Double, nw As Single, nh As Single
    For i = LBound(frames) To UBound(frames)
        sc = CDbl(frames(i))
        nw = CSng(origW * sc)
        nh = CSng(origH * sc)
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
'  EFFECT 3: SLEEK NON-BLOCKING FLOATING TOAST BANNER (AUTO-DISMISS 2s)
' =============================================================================
Public Sub ShowToast(ByVal ws As Worksheet, ByVal msgText As String)
    If Len(Trim$(msgText)) = 0 Then Exit Sub
    On Error GoTo SafeExit
    CleanupToasts

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

    Dim toast As Shape
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

    gToastDueTime = Now + TimeSerial(0, 0, 2)
    gToastScheduled = True
    Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissToast", Schedule:=True
SafeExit:
End Sub

' =============================================================================
'  PUBLIC: ULTRA-SMOOTH SINGLE-TICK HANDLERS (ZERO REDUNDANT FULL RECALC!)
'  Excel's native incremental calc already updates only the dirty cells (<30ms)
'  before Worksheet_Change fires -- we read the already-updated KPIs directly!
' =============================================================================
Public Sub HandleTrackerTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    If Target.Cells.CountLarge <> 1 Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub
    If Not IsCellChecked(Target.Value) Then Exit Sub

    Dim dayPct As Variant
    dayPct = ws.Cells(12, Target.Column).Value
    Dim hitPerfect As Boolean
    hitPerfect = (IsNumeric(dayPct) And Val(CStr(dayPct)) >= 0.999)

    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Dim curBest As Long, prevCel As Long, hitStreak As Long
    curBest = CLng(Val(wsCalc.Range("C11").Value))
    prevCel = CLng(Val(wsCalc.Range("BA6").Value))
    hitStreak = 0
    If (curBest = 7 Or curBest = 14 Or curBest = 21 Or curBest = 30) And curBest > prevCel Then
        hitStreak = curBest
        Application.EnableEvents = False
        wsCalc.Range("BA6").Value = curBest
        Application.EnableEvents = True
    End If

    If hitPerfect Then
        PlayHeroBounce ws, "Anim_MonthlyHero"
        PlaySparkleBurst ws, "Anim_MonthlyHero"
        ShowToast ws, GetFxMsg(8)
    ElseIf hitStreak > 0 Then
        PlayHeroBounce ws, "Anim_MonthlyHero"
        PlaySparkleBurst ws, "Anim_MonthlyHero"
        Select Case hitStreak
            Case 7:  ShowToast ws, GetFxMsg(9)
            Case 14: ShowToast ws, GetFxMsg(10)
            Case 21: ShowToast ws, GetFxMsg(11)
            Case 30: ShowToast ws, GetFxMsg(12)
        End Select
    End If
SafeExit:
    Application.EnableEvents = True
End Sub

Public Sub HandleDailyTaskTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    If Target.Cells.CountLarge <> 1 Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub
    If Not IsCellChecked(Target.Value) Then Exit Sub

    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Dim dtPct As Variant, dtTot As Variant
    dtPct = wsCalc.Range("AN15").Value
    dtTot = wsCalc.Range("AN14").Value
    If IsNumeric(dtPct) And IsNumeric(dtTot) Then
        If CLng(dtTot) > 0 And CDbl(dtPct) >= 0.999 Then
            PlayHeroBounce ws, "Anim_DailyTaskHero"
            PlaySparkleBurst ws, "Anim_DailyTaskHero"
            ShowToast ws, GetFxMsg(14)
        End If
    End If
SafeExit:
End Sub

Public Sub HandleYearlyGoalTick(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    If Target.Cells.CountLarge <> 1 Then Exit Sub
    If Not IsFXEnabled() Then Exit Sub
    If Not IsCellChecked(Target.Value) Then Exit Sub

    Dim wsCalc As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Dim hitAll As Boolean
    Dim ygPct As Variant
    ygPct = wsCalc.Range("AN6").Value
    hitAll = (IsNumeric(ygPct) And Val(CStr(ygPct)) >= 0.999)

    PlayHeroBounce ws, "Anim_YearlyGoals"
    If hitAll Then PlaySparkleBurst ws, "Anim_YearlyGoals"
    ShowToast ws, GetFxMsg(15)
SafeExit:
End Sub

' =============================================================================
'  PUBLIC: DEFERRED ANNUAL RECALC & HALL SPOTLIGHT ON SHEET ACTIVATE
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
        ' Defer heavy Annual sheet recalc while user ticks on Tracker / Daily Tasks!
        wsAnn.EnableCalculation = False
        Exit Sub
    End If

    ' User clicked Annual Achievements: re-enable & refresh cleanly!
    wsAnn.EnableCalculation = True
    wsAnn.Calculate

    If IsFXEnabled() Then
        Dim unlockedCnt As Long
        unlockedCnt = CLng(Application.WorksheetFunction.CountIf(ws.Range("H35:H42"), ">=1"))
        If unlockedCnt > 0 Then
            PlayHeroBounce ws, "Anim_AnnualHero"
        End If
    End If
SafeExit:
End Sub

' =============================================================================
'  EFFECT 4: QUICK-ACTION PASTEL PILL BUTTON MACROS (100% PURE ASCII!)
' =============================================================================
Private Sub StepMonthBy(ByVal delta As Long)
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_TRACKER")
    If ws Is Nothing Then Exit Sub

    Dim curM As Long, curY As Long
    curM = MonthNameToNum(CStr(ws.Range("B3").Value))
    curY = CLng(Val(ws.Range("B5").Value))
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

    Application.EnableEvents = False
    ws.Range("B3").Value = NumToMonthName(curM)
    ws.Range("B5").Value = curY
    Application.EnableEvents = True

    HandleMonthlySwitch ws
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
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsTr = GetAnchorSheet("ANCHOR_TRACKER")

    Dim newState As Boolean
    newState = Not IsFXEnabled()
    wsCalc.Range("BA1").Value = newState

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

    Application.EnableEvents = False
    ws.Range("D5").Value = d
    ws.Range("E5").Value = NumToMonthName(m)
    ws.Range("F5").Value = y
    Application.EnableEvents = True

    HandleDailyTasksSwitch ws
End Sub

Public Sub BtnPrevDay()
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If ws Is Nothing Then Exit Sub
    Dim curD As Long, curM As Long, curY As Long
    curD = CLng(Val(ws.Range("D5").Value))
    curM = MonthNameToNum(CStr(ws.Range("E5").Value))
    curY = CLng(Val(ws.Range("F5").Value))
    If curM = 0 Or curD < 1 Or curY < 2000 Then Exit Sub
    SetDailyTasksDate DateAdd("d", -1, DateSerial(curY, curM, curD))
End Sub

Public Sub BtnNextDay()
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_DAILYTASKS")
    If ws Is Nothing Then Exit Sub
    Dim curD As Long, curM As Long, curY As Long
    curD = CLng(Val(ws.Range("D5").Value))
    curM = MonthNameToNum(CStr(ws.Range("E5").Value))
    curY = CLng(Val(ws.Range("F5").Value))
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
    ThisWorkbook.Worksheets(CALC_SHEET).Range("BA1").Value = True
    PlayHeroBounce wsG, "Guide_Stage5"
    PlaySparkleBurst wsG, "Guide_Stage5"
    ShowToast wsG, GetFxMsg(16)
    ThisWorkbook.Worksheets(CALC_SHEET).Range("BA1").Value = prevFX
SafeExit:
End Sub

' =============================================================================
'  PUBLIC: MONTHLY SWITCH (B3 Month / B5 Year -> SAVE OLD & LOAD NEW)
' =============================================================================
Public Sub HandleMonthlySwitch(ByVal ws As Worksheet)
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim newM As Long, newY As Long
    newM = MonthNameToNum(CStr(ws.Range("B3").Value))
    newY = CLng(Val(ws.Range("B5").Value))
    If newM = 0 Or newY < 2000 Or newY > 2100 Then GoTo Cleanup

    Dim newKey As String, lastKey As String
    newKey = Format$(newY, "0000") & "-" & Format$(newM, "00")
    lastKey = KeyToString(wsCalc.Range("AN2").Value)
    If lastKey = newKey Then GoTo Cleanup

    Dim curNames As Variant, curGoals As Variant, curGrid As Variant
    curNames = ws.Range("B17:B36").Value
    curGoals = ws.Range("AI17:AI36").Value
    curGrid = ws.Range("C17:AG36").Value

    Dim r As Long, d As Long
    If Len(lastKey) = 7 Then
        Dim saveGrid(1 To N_HABITS, 1 To 31) As Boolean
        For r = 1 To N_HABITS
            For d = 1 To 31
                saveGrid(r, d) = IsCellChecked(curGrid(r, d))
            Next d
        Next r
        SaveMonthBlock wsDb, lastKey, curNames, curGoals, saveGrid
    End If

    Dim srcRow As Long
    srcRow = FindBlockRow(wsDb, 1, newKey)
    Dim loadGrid(1 To N_HABITS, 1 To 31) As Variant
    Dim gridChanged As Boolean
    gridChanged = False

    If srcRow > 0 Then
        Dim srcBlock As Variant
        srcBlock = wsDb.Cells(srcRow, 1).Resize(N_HABITS, 35).Value
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

        If hasAnyName And namesDiff Then ws.Range("B17:B36").Value = loadNames
        If hasAnyName And goalsDiff Then ws.Range("AI17:AI36").Value = loadGoals
        If gridChanged Then ws.Range("C17:AG36").Value = loadGrid
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
        If gridChanged Then ws.Range("C17:AG36").Value = loadGrid
    End If

    wsCalc.Range("AN2").NumberFormat = "@"
    wsCalc.Range("AN2").Value = newKey
    wsCalc.Range("BA6").Value = 0
    wsCalc.Calculate
    ws.Calculate

    Dim didSwitch As Boolean
    didSwitch = True

Cleanup:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    If didSwitch And IsFXEnabled() Then
        ShowToast ws, GetFxMsg(13)
    End If
End Sub

' =============================================================================
'  PUBLIC: YEARLY GOALS SWITCH (I2 Year -> SAVE OLD & LOAD NEW)
' =============================================================================
Public Sub HandleYearlyGoalsSwitch(ByVal ws As Worksheet)
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim oldYr As Long, newYr As Long
    oldYr = CLng(Val(wsCalc.Range("AN3").Value))
    newYr = CLng(Val(ws.Range("I2").Value))
    If newYr < 2000 Or newYr > 2100 Or oldYr = newYr Then GoTo Cleanup

    If oldYr >= 2000 Then
        Dim curYG As Variant
        curYG = ws.Range("B6:F25").Value
        Dim ygBlock(1 To N_GOALS, 1 To 7) As Variant
        Dim r As Long, gDone As Long, gTot As Long

        For r = 1 To N_GOALS
            ygBlock(r, 1) = oldYr
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

        Dim dstYGRow As Long
        dstYGRow = FindBlockRow(wsDb, 47, CStr(oldYr))
        If dstYGRow = 0 Then
            dstYGRow = wsDb.Cells(wsDb.Rows.Count, 47).End(xlUp).Row + 1
        End If
        wsDb.Cells(dstYGRow, 47).Resize(N_GOALS, 7).Value = ygBlock

        Dim ygSum(1 To 1, 1 To 3) As Variant
        ygSum(1, 1) = oldYr
        ygSum(1, 2) = gDone
        ygSum(1, 3) = gTot
        Dim sYGRow As Long
        sYGRow = FindSummaryRow(wsDb, 55, CStr(oldYr))
        If sYGRow = 0 Then
            sYGRow = wsDb.Cells(wsDb.Rows.Count, 55).End(xlUp).Row + 1
        End If
        wsDb.Cells(sYGRow, 55).Resize(1, 3).Value = ygSum
    End If

    Dim srcYGRow As Long
    srcYGRow = FindBlockRow(wsDb, 47, CStr(newYr))
    Dim loadYG(1 To N_GOALS, 1 To 5) As Variant
    Dim i As Long
    If srcYGRow > 0 Then
        Dim srcYG As Variant
        srcYG = wsDb.Cells(srcYGRow, 47).Resize(N_GOALS, 7).Value
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
    ws.Range("B6:F25").Value = loadYG
    wsCalc.Range("AN3").Value = newYr
    wsCalc.Calculate
    ws.Calculate

Cleanup:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  PUBLIC: DAILY TASKS DATE SWITCH (D5:F5 -> SAVE OLD & LOAD NEW YYYY-MM-DD)
' =============================================================================
Public Sub HandleDailyTasksSwitch(ByVal ws As Worksheet)
    On Error GoTo Cleanup
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    ws.DisplayPageBreaks = False

    Dim wsCalc As Worksheet, wsDb As Worksheet
    Set wsCalc = ThisWorkbook.Worksheets(CALC_SHEET)
    Set wsDb = ThisWorkbook.Worksheets(DB_SHEET)

    Dim newDay As Long, newMonth As Long, newYear As Long
    newDay = CLng(Val(ws.Range("D5").Value))
    newMonth = MonthNameToNum(CStr(ws.Range("E5").Value))
    newYear = CLng(Val(ws.Range("F5").Value))
    If newDay < 1 Or newMonth = 0 Or newYear < 2000 Or newYear > 2100 Then GoTo Cleanup

    Dim maxDay As Long
    maxDay = Day(DateSerial(newYear, newMonth + 1, 0))
    If newDay > maxDay Then
        newDay = maxDay
        ws.Range("D5").Value = newDay
    End If

    Dim newKey As String, lastKey As String
    newKey = Format$(newYear, "0000") & "-" & Format$(newMonth, "00") & "-" & Format$(newDay, "00")
    lastKey = KeyToString(wsCalc.Range("AN12").Value)
    If lastKey = newKey Then GoTo Cleanup

    If Len(lastKey) = 10 Then
        Dim curTasks As Variant
        curTasks = ws.Range("B9:F28").Value
        Dim curNote As Variant
        curNote = ws.Range("B31").Value

        Dim dtBlock(1 To 20, 1 To 8) As Variant
        Dim r As Long
        For r = 1 To 20
            dtBlock(r, 1) = lastKey
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
        dstRow = FindBlockRow(wsDb, 59, lastKey)
        If dstRow = 0 Then
            dstRow = wsDb.Cells(wsDb.Rows.Count, 59).End(xlUp).Row + 1
        End If
        wsDb.Cells(dstRow, 59).Resize(20, 1).NumberFormat = "@"
        wsDb.Cells(dstRow, 59).Resize(20, 8).Value = dtBlock
    End If

    Dim srcRow As Long
    srcRow = FindBlockRow(wsDb, 59, newKey)
    Dim loadTasks(1 To 20, 1 To 5) As Variant
    Dim loadNote As Variant
    Dim i As Long
    If srcRow > 0 Then
        Dim srcArr As Variant
        srcArr = wsDb.Cells(srcRow, 59).Resize(20, 8).Value
        For i = 1 To 20
            loadTasks(i, 1) = IsCellChecked(srcArr(i, 3))
            loadTasks(i, 2) = srcArr(i, 4)
            loadTasks(i, 3) = srcArr(i, 5)
            loadTasks(i, 4) = srcArr(i, 6)
            loadTasks(i, 5) = srcArr(i, 7)
        Next i
        loadNote = srcArr(1, 8)
    Else
        For i = 1 To 20
            loadTasks(i, 1) = False
            loadTasks(i, 2) = ""
            loadTasks(i, 3) = ""
            loadTasks(i, 4) = ""
            loadTasks(i, 5) = ""
        Next i
        loadNote = ""
    End If

    ws.Range("B9:F28").Value = loadTasks
    ws.Range("B31").Value = loadNote
    wsCalc.Range("AN12").NumberFormat = "@"
    wsCalc.Range("AN12").Value = newKey
    wsCalc.Calculate
    ws.Calculate

    Dim didDateSwitch As Boolean
    didDateSwitch = True

Cleanup:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    If didDateSwitch And IsFXEnabled() Then
        ShowToast ws, GetFxMsg(21)
    End If
End Sub
