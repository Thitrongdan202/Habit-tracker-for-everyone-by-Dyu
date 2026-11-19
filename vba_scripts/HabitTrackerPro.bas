Attribute VB_Name = "HabitTrackerPro"
Option Explicit

' =============================================================================
'  Habit Tracker Pro — Offline Sprites, Celebration & Utility Macros
'  Compatible with Microsoft Excel 2016 / 2019 / 2021 / 365 (Windows & macOS)
'  Repo: https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu
' =============================================================================

Public Const HABIT_GRID As String = "C17:AG36"
Public Const PCT_ROW As Long = 12
Public Const IMG_ROW As Long = 9
Public Const DAY_START_COL As Long = 3   ' Column C (Day 1)
Public Const DAY_END_COL As Long = 33    ' Column AG (Day 31)

' -----------------------------------------------------------------------------
' 1. Import 6 local PNG files (stage_0.png .. stage_5.png) into hidden _Sprites
'    sheet so older Excel versions can animate completely offline.
' -----------------------------------------------------------------------------
Public Sub SetupOfflineSprites()
    Dim fd As FileDialog
    Dim folderPath As String
    Dim wsSpr As Worksheet
    Dim i As Long
    Dim imgFile As String
    Dim shp As Shape

    Set fd = Application.FileDialog(msoFileDialogFolderPicker)
    fd.Title = "Chon thu muc chua stage_0.png .. stage_5.png (vd: assets\sunflower)"
    If fd.Show <> -1 Then Exit Sub
    folderPath = fd.SelectedItems(1)
    If Right$(folderPath, 1) <> "\" Then folderPath = folderPath & "\"

    For i = 0 To 5
        If Dir$(folderPath & "stage_" & i & ".png") = "" Then
            MsgBox "Khong tim thay file: " & folderPath & "stage_" & i & ".png", vbExclamation, "Thieu anh Sprite"
            Exit Sub
        End If
    Next i

    Application.ScreenUpdating = False
    On Error Resume Next
    Set wsSpr = ThisWorkbook.Worksheets("_SpritesVBA")
    On Error GoTo 0
    If wsSpr Is Nothing Then
        Set wsSpr = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        wsSpr.Name = "_SpritesVBA"
    Else
        For Each shp In wsSpr.Shapes
            shp.Delete
        Next shp
    End If

    For i = 0 To 5
        imgFile = folderPath & "stage_" & i & ".png"
        Set shp = wsSpr.Shapes.AddPicture(Filename:=imgFile, LinkToFile:=msoFalse, _
                                          SaveWithDocument:=msoTrue, Left:=10, Top:=10 + i * 70, _
                                          Width:=56, Height:=56)
        shp.Name = "Stage_" & i
    Next i

    wsSpr.Visible = xlSheetVeryHidden
    Application.ScreenUpdating = True

    RefreshAllOfflineStages ActiveSheet
    MsgBox "Da nhung thanh cong 6 anh hoat anh Offline! Ban co the su dung khong can Internet.", vbInformation, "Habit Tracker Pro"
End Sub

' -----------------------------------------------------------------------------
' 2. Refresh all 31 day sprite shapes on the active tracker sheet (Offline mode)
' -----------------------------------------------------------------------------
Public Sub RefreshAllOfflineStages(Optional ByVal ws As Worksheet = Nothing)
    Dim colIdx As Long
    If ws Is Nothing Then Set ws = ActiveSheet
    Application.ScreenUpdating = False
    For colIdx = DAY_START_COL To DAY_END_COL
        RefreshDaySprite ws, colIdx
    Next colIdx
    Application.ScreenUpdating = True
End Sub

' -----------------------------------------------------------------------------
' 3. Swap one day's offline sprite shape based on % Completed (row 12)
' -----------------------------------------------------------------------------
Public Sub RefreshDaySprite(ByVal ws As Worksheet, ByVal colIdx As Long)
    Dim wsSpr As Worksheet
    Dim shpName As String
    Dim stageIdx As Long
    Dim pctVal As Double
    Dim thr1 As Double, thr2 As Double, thr3 As Double
    Dim targetCell As Range
    Dim srcShp As Shape, newShp As Shape

    On Error Resume Next
    Set wsSpr = ThisWorkbook.Worksheets("_SpritesVBA")
    On Error GoTo 0
    If wsSpr Is Nothing Then Exit Sub

    shpName = "DaySprite_" & colIdx
    On Error Resume Next
    ws.Shapes(shpName).Delete
    On Error GoTo 0

    ' Skip out-of-month blank day
    If Trim$(CStr(ws.Cells(16, colIdx).Value)) = "" Then Exit Sub

    thr1 = 0.25: thr2 = 0.5: thr3 = 0.75
    On Error Resume Next
    thr1 = CDbl(ThisWorkbook.Names("CFG_THR_1").RefersToRange.Value)
    thr2 = CDbl(ThisWorkbook.Names("CFG_THR_2").RefersToRange.Value)
    thr3 = CDbl(ThisWorkbook.Names("CFG_THR_3").RefersToRange.Value)
    On Error GoTo 0

    pctVal = Val(ws.Cells(PCT_ROW, colIdx).Value)
    stageIdx = 0
    If pctVal > 0 Then stageIdx = 1
    If pctVal >= thr1 Then stageIdx = 2
    If pctVal >= thr2 Then stageIdx = 3
    If pctVal >= thr3 Then stageIdx = 4
    If pctVal >= 0.999 Then stageIdx = 5

    Set targetCell = ws.Cells(IMG_ROW, colIdx)
    Set srcShp = wsSpr.Shapes("Stage_" & stageIdx)
    srcShp.Copy
    ws.Paste Destination:=targetCell
    Set newShp = ws.Shapes(ws.Shapes.Count)
    With newShp
        .Name = shpName
        .LockAspectRatio = msoTrue
        .Height = Application.Min(targetCell.Height - 6, targetCell.Width - 2)
        .Left = targetCell.Left + (targetCell.Width - .Width) / 2
        .Top = targetCell.Top + (targetCell.Height - .Height) / 2
        .Placement = xlMoveAndSize
    End With
End Sub

' -----------------------------------------------------------------------------
' 4. Safely reset all habit checkboxes for a fresh month (keeps all formulas!)
' -----------------------------------------------------------------------------
Public Sub ResetCurrentMonth()
    Dim ans As VbMsgBoxResult
    Dim cell As Range
    ans = MsgBox("Ban co chac muon dat lai toan bo o tick (C17:AG36) cho thang moi?" & vbCrLf & _
                 "(Ten thoi quen, muc tieu va toan bo cong thuc se duoc giu nguyen.)", _
                 vbYesNo + vbQuestion, "Reset Thang Moi")
    If ans <> vbYes Then Exit Sub

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    For Each cell In ActiveSheet.Range(HABIT_GRID)
        If VarType(cell.Value) = vbBoolean Then
            cell.Value = False
        ElseIf cell.Value = ChrW(9745) Or cell.Value = ChrW(10003) Then
            cell.Value = ChrW(9744)
        Else
            cell.Value = False
        End If
    Next cell
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    RefreshAllOfflineStages ActiveSheet
    MsgBox "Da lam moi bang theo doi! Chuc ban mot thang moi day cam hung!", vbInformation, "Habit Tracker Pro"
End Sub

' -----------------------------------------------------------------------------
' 5. Export active tracker sheet as a 1-page crisp landscape PDF report
' -----------------------------------------------------------------------------
Public Sub ExportDashboardPDF()
    Dim outPath As String
    Dim ws As Worksheet
    Set ws = ActiveSheet
    outPath = ThisWorkbook.Path & "\" & Replace(ws.Name, " ", "_") & "_" & Format$(Now, "yyyymmdd") & ".pdf"
    With ws.PageSetup
        .Orientation = xlLandscape
        .Zoom = False
        .FitToPagesWide = 1
        .FitToPagesTall = 1
    End With
    ws.ExportAsFixedFormat Type:=xlTypePDF, Filename:=outPath, Quality:=xlQualityStandard
    MsgBox "Da xuat bao cao PDF thanh cong:" & vbCrLf & outPath, vbInformation, "Export PDF"
End Sub

' -----------------------------------------------------------------------------
' 6. Soundless visual celebration status banner for 100% day / streak milestones
' -----------------------------------------------------------------------------
Public Sub CheckAndCelebrate(ByVal ws As Worksheet, ByVal changedCell As Range)
    Dim pctVal As Double
    Dim streakVal As Long
    Dim msg As String

    pctVal = Val(ws.Cells(PCT_ROW, changedCell.Column).Value)
    streakVal = CLng(Val(ws.Cells(changedCell.Row, 38).Value)) ' Col AL = Current Streak

    If pctVal >= 0.999 Then
        msg = "TUYET VOI! Ngay " & ws.Cells(16, changedCell.Column).Value & " da hoan thanh 100% — Cay no hoa ruc ro!"
    ElseIf streakVal = 7 Or streakVal = 14 Or streakVal = 21 Or streakVal = 30 Then
        msg = "CHUC MUNG! Thoi quen '" & ws.Cells(changedCell.Row, 2).Value & "' vua cham moc chuoi " & streakVal & " ngay lien tiep!"
    End If

    If msg <> "" Then
        Application.StatusBar = "★ " & msg
    End If
End Sub
