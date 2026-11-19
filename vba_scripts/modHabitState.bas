Attribute VB_Name = "modHabitState"
Option Explicit

' =============================================================================
'  modHabitState — Habit Tracker v2.1 Ultra-Fast Persistence Engine
'  ---------------------------------------------------------------------------
'  - 100% bulk in-memory 2D Variant array read/write (ZERO cell-by-cell loops)
'  - Disables ScreenUpdating, EnableEvents, Calculation, DisplayPageBreaks
'  - Avoids redundant double recalculation & skips unchanged range writes
'  - Pure ASCII VBA (locale-safe across Windows & Mac Excel)
' =============================================================================

Private Const CALC_SHEET As String = "_Calc"
Private Const DB_SHEET As String = "_Database"
Private Const N_HABITS As Long = 20
Private Const N_FORM_ROWS As Long = 20
Private Const N_GOALS As Long = 20

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
        If CStr(arr) = targetKey Then FindBlockRow = 2
        Exit Function
    End If
    For i = 1 To UBound(arr, 1) Step N_HABITS
        If CStr(arr(i, 1)) = targetKey Then
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
        If CStr(arr) = targetKey Then FindSummaryRow = 2
        Exit Function
    End If
    For i = 1 To UBound(arr, 1)
        If CStr(arr(i, 1)) = targetKey Then
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
    wsDb.Cells(dstRow, 1).Resize(N_HABITS, 35).Value = rawBlock

    Dim yr As Long, mo As Long, dimDays As Long
    yr = CLng(Left$(saveKey, 4))
    mo = CLng(Right$(saveKey, 2))
    dimDays = Day(DateSerial(yr, mo + 1, 0))

    Dim activeCount As Long, totalDone As Long, totalGoal As Long, bestStreak As Long
    Dim runLen As Long, effGoal As Long
    Dim activeRows(1 To N_HABITS) As Boolean
    Dim nm As String

    For r = 1 To N_HABITS
        nm = Trim$(CStr(namesArr(r, 1)))
        If Len(nm) > 0 Then
            activeRows(r) = True
            activeCount = activeCount + 1
            If IsNumeric(goalsArr(r, 1)) And Val(goalsArr(r, 1)) > 0 Then
                effGoal = CLng(Val(goalsArr(r, 1)))
                If effGoal > dimDays Then effGoal = dimDays
            Else
                effGoal = dimDays
            End If
            totalGoal = totalGoal + effGoal

            runLen = 0
            For d = 1 To dimDays
                If IsCellChecked(gridArr(r, d)) Then
                    totalDone = totalDone + 1
                    runLen = runLen + 1
                    If runLen > bestStreak Then bestStreak = runLen
                Else
                    runLen = 0
                End If
            Next d
        End If
    Next r

    Dim grownDays As Long, perfectDays As Long, doneDay As Long
    Dim pctDay As Double, thr3 As Double
    thr3 = GetGrownThreshold()
    If activeCount > 0 Then
        For d = 1 To dimDays
            doneDay = 0
            For r = 1 To N_HABITS
                If activeRows(r) Then
                    If IsCellChecked(gridArr(r, d)) Then doneDay = doneDay + 1
                End If
            Next r
            pctDay = CDbl(doneDay) / CDbl(activeCount)
            If pctDay >= thr3 - 0.000001 Then grownDays = grownDays + 1
            If pctDay >= 0.999 Then perfectDays = perfectDays + 1
        Next d
    End If

    Dim overallPct As Double
    If totalGoal > 0 Then
        overallPct = CDbl(totalDone) / CDbl(totalGoal)
        If overallPct > 1# Then overallPct = 1#
    Else
        overallPct = 0#
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
    wsDb.Cells(sRow, 37).Resize(1, 9).Value = sumRow
End Sub

' =============================================================================
'  PUBLIC: Triggered on Monthly Tracker Worksheet_Change when B3 or B5 changes
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

    Dim oldKey As String
    oldKey = Trim$(CStr(wsCalc.Range("AN2").Value))

    Dim newMo As Long, newYr As Long
    newMo = MonthNameToNum(CStr(ws.Range("B3").Value))
    newYr = CLng(Val(ws.Range("B5").Value))
    If newMo < 1 Or newMo > 12 Or newYr < 2000 Or newYr > 2100 Then GoTo Cleanup

    Dim newKey As String
    newKey = Format$(newYr, "0000") & "-" & Format$(newMo, "00")
    If oldKey = newKey Then GoTo Cleanup

    Dim curNames As Variant, curGoals As Variant, curGrid As Variant
    curNames = ws.Range("B17:B36").Value
    curGoals = ws.Range("AI17:AI36").Value
    curGrid = ws.Range("C17:AG36").Value

    ' 1) Save current month under oldKey
    If Len(oldKey) = 7 And Mid$(oldKey, 5, 1) = "-" Then
        SaveMonthBlock wsDb, oldKey, curNames, curGoals, curGrid
    End If

    ' 2) Load newKey from _Database (only write ranges that actually changed!)
    Dim srcRow As Long
    srcRow = FindBlockRow(wsDb, 1, newKey)
    Dim loadGrid(1 To N_HABITS, 1 To 31) As Variant
    Dim r As Long, d As Long
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

    ' 3) Update LastLoadedKey
    wsCalc.Range("AN2").Value = newKey

Cleanup:
    ' Setting xlCalculationAutomatic triggers ONE clean recalculation (no double Calc!)
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  PUBLIC: Triggered on Yearly Goals Worksheet_Change when I2 (Year) changes
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

Cleanup:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub
