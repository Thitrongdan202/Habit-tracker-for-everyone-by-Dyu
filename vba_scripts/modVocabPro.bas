Attribute VB_Name = "modVocabPro"
Option Explicit

' =============================================================================
'  modVocabPro -- Chiikawa Vocabulary Tracker Pro Engine (#96-#100)
'  ---------------------------------------------------------------------------
'  - 100% PURE ASCII VBA (ZERO Vietnamese/Emoji string literals in VBA code!)
'    All Vietnamese UI strings, quiz prompts & Toast messages live in `_Calc!Z1:AA25`.
'  - Native Pre-Placed Sprite Stacks (`SPR_VHERO_S0..S5`, `SPR_PHERO_S0..S5`,
'    `SPR_SHERO_S0..S5`, `Guide_Stage0..5`) for instant <5ms stage switching!
'  - Interactive Random Flashcard Quiz Pop-up (`BtnVocabQuiz`):
'      * Prioritizes active unmastered words from Tab 1 (`📚 Kho Từ Vựng`)
'      * Shows Word + Pronunciation + Hint -> reveals Meaning + Example
'      * Updates word progress directly back into Tab 1 & syncs Chiikawa mascot!
'  - Exclusive Chiikawa Pastel Celebration FX (`BtnVocabDemoFX` / goal reached):
'      * Pastel stars, sakura/daisy petals, hearts + Hero bounce + Bottom-Left Toast
'      * 100% guaranteed zero orphan shapes (`FX_VOC_*`) & respects `FX: BAT / TAT`!
' =============================================================================

Private Const CALC_SHEET As String = "_Calc"
Private Const MSO_DIAMOND As Long = 4
Private Const MSO_ROUNDED_RECT As Long = 5
Private Const MSO_OVAL As Long = 9
Private Const MSO_HEART As Long = 21
Private Const MSO_STAR_5 As Long = 92
Private Const MSO_STAR_4 As Long = 187
Private Const MSO_FALSE As Long = 0
Private Const MSO_TRUE As Long = -1

Private gToastDueTime As Double
Private gToastScheduled As Boolean
Private gToastSheetName As String
Private gToastShp As Shape
Private gFXCached As Boolean
Private gFXVal As Boolean

' =============================================================================
'  INTERNAL HELPERS (100% PURE ASCII)
' =============================================================================
Private Function GetCalcSheet() As Worksheet
    Set GetCalcSheet = ThisWorkbook.Worksheets(CALC_SHEET)
End Function

Private Function GetAnchorSheet(ByVal anchorName As String) As Worksheet
    On Error Resume Next
    Set GetAnchorSheet = ThisWorkbook.Names(anchorName).RefersToRange.Worksheet
    On Error GoTo 0
End Function

Private Function GetVocabMsg(ByVal rowIdx As Long) As String
    On Error Resume Next
    GetVocabMsg = CStr(GetCalcSheet().Cells(rowIdx, 27).Value2) ' Col AA (27)
    On Error GoTo 0
End Function

Private Function GetCfgNum(ByVal rowIdx As Long, ByVal fallbackVal As Long) As Long
    On Error Resume Next
    Dim v As Variant
    v = GetCalcSheet().Cells(rowIdx, 27).Value2
    If IsNumeric(v) And CLng(v) > 0 Then
        GetCfgNum = CLng(v)
    Else
        GetCfgNum = fallbackVal
    End If
    On Error GoTo 0
End Function

Private Function HexToRgb(ByVal hexStr As String, ByVal fallbackRgb As Long) As Long
    On Error GoTo BadHex
    Dim s As String
    s = Replace(Trim$(hexStr), "#", "")
    If Len(s) <> 6 Then GoTo BadHex
    HexToRgb = RGB(CLng("&H" & Left$(s, 2)), CLng("&H" & Mid$(s, 3, 2)), CLng("&H" & Right$(s, 2)))
    Exit Function
BadHex:
    HexToRgb = fallbackRgb
End Function

Private Function GetThemeRgb(ByVal rowIdx As Long, ByVal fallbackRgb As Long) As Long
    GetThemeRgb = HexToRgb(GetVocabMsg(rowIdx), fallbackRgb)
End Function

Private Function IsFXEnabled() As Boolean
    If gFXCached Then
        IsFXEnabled = gFXVal
        Exit Function
    End If
    On Error Resume Next
    Dim v As Variant
    v = GetCalcSheet().Range("AA1").Value2
    If VarType(v) = vbBoolean Then
        gFXVal = CBool(v)
    Else
        gFXVal = (UCase$(Trim$(CStr(v))) <> "FALSE")
    End If
    gFXCached = True
    IsFXEnabled = gFXVal
    On Error GoTo 0
End Function

Private Sub WaitSec(ByVal secs As Double)
    Dim t0 As Double, tNow As Double
    t0 = Timer
    Do
        DoEvents
        tNow = Timer
        If tNow < t0 Then tNow = tNow + 86400#
    Loop While (tNow - t0) < secs
End Sub

Private Function StageIdxFromCell(ByVal addr As String) As Long
    On Error Resume Next
    Dim v As Variant
    v = GetCalcSheet().Range(addr).Value2
    If IsNumeric(v) Then
        StageIdxFromCell = CLng(v)
    Else
        StageIdxFromCell = 1
    End If
    If StageIdxFromCell < 1 Then StageIdxFromCell = 1
    If StageIdxFromCell > 6 Then StageIdxFromCell = 6
    On Error GoTo 0
End Function

' =============================================================================
'  SPRITE STACK SYNC (<5ms O(1) VISIBILITY SWITCH)
' =============================================================================
Private Sub SyncStack(ByVal ws As Worksheet, ByVal prefix As String, ByVal stage1to6 As Long)
    If ws Is Nothing Then Exit Sub
    On Error Resume Next
    Dim k As Long
    For k = 0 To 5
        ws.Shapes(prefix & CStr(k)).Visible = IIf(k = stage1to6 - 1, MSO_TRUE, MSO_FALSE)
    Next k
    On Error GoTo 0
End Sub

Public Sub SyncAllVocabSprites()
    On Error Resume Next
    Dim st As Long
    st = StageIdxFromCell("C6")
    SyncStack GetAnchorSheet("ANCHOR_VOCAB"), "SPR_VHERO_S", st
    SyncStack GetAnchorSheet("ANCHOR_PRACTICE"), "SPR_PHERO_S", StageIdxFromCell("C7")
    SyncStack GetAnchorSheet("ANCHOR_STATS"), "SPR_SHERO_S", st
    On Error GoTo 0
End Sub

' =============================================================================
'  LIFECYCLE & SHEET PROTECTION (UserInterfaceOnly:=True)
' =============================================================================
Public Sub ProtectVocabSheets()
    On Error Resume Next
    Dim anchors As Variant, idx As Long, ws As Worksheet
    anchors = Array("ANCHOR_VOCAB", "ANCHOR_PRACTICE", "ANCHOR_STATS", "ANCHOR_GUIDE")
    For idx = LBound(anchors) To UBound(anchors)
        Set ws = GetAnchorSheet(CStr(anchors(idx)))
        If Not ws Is Nothing Then
            ws.Protect Password:="", DrawingObjects:=False, Contents:=True, _
                       Scenarios:=False, UserInterfaceOnly:=True, AllowFormattingCells:=False
        End If
    Next idx
    On Error GoTo 0
End Sub

Public Sub InitVocabWorkbook()
    On Error Resume Next
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        ws.DisplayPageBreaks = False
    Next ws
    CleanupAllVocabFX
    SyncAllVocabSprites
    ProtectVocabSheets
    Application.Calculation = xlCalculationAutomatic
    On Error GoTo 0
End Sub

Public Sub HandleVocabEdit(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    Application.ScreenUpdating = False
    SyncAllVocabSprites
    Application.ScreenUpdating = True

    If Not IsFXEnabled() Then GoTo SafeExit
    Dim pct As Double
    On Error Resume Next
    pct = CDbl(GetCalcSheet().Range("C5").Value2)
    On Error GoTo SafeExit
    If pct >= 0.999 Then
        Dim heroNm As String
        heroNm = "SPR_VHERO_S" & CStr(StageIdxFromCell("C6") - 1)
        PlayChiikawaCelebration ws, heroNm, GetVocabMsg(14)
    End If
SafeExit:
    Application.ScreenUpdating = True
End Sub

Public Sub HandlePracticeEdit(ByVal ws As Worksheet, ByVal Target As Range)
    On Error GoTo SafeExit
    Application.ScreenUpdating = False
    SyncAllVocabSprites
    Application.ScreenUpdating = True

    If Not IsFXEnabled() Then GoTo SafeExit
    Dim pPct As Double
    On Error Resume Next
    pPct = CDbl(GetCalcSheet().Range("C8").Value2)
    On Error GoTo SafeExit
    If pPct >= 0.999 Then
        Dim heroNm As String
        heroNm = "SPR_PHERO_S" & CStr(StageIdxFromCell("C7") - 1)
        PlayChiikawaCelebration ws, heroNm, GetVocabMsg(15)
    End If
SafeExit:
    Application.ScreenUpdating = True
End Sub

' =============================================================================
'  CLEANUP & BOTTOM-LEFT NON-BLOCKING TOAST
' =============================================================================
Public Sub CleanupVocabParticles(ByVal ws As Worksheet)
    If ws Is Nothing Then Exit Sub
    On Error Resume Next
    Dim i As Long, nm As String
    For i = ws.Shapes.Count To 1 Step -1
        nm = ws.Shapes(i).Name
        If Left$(nm, 7) = "FX_VOC_" Then
            ws.Shapes(i).Delete
        End If
    Next i
    On Error GoTo 0
End Sub

Public Sub CleanupVocabToasts()
    On Error Resume Next
    If gToastScheduled Then
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissVocabToast", Schedule:=False
        gToastScheduled = False
    End If
    If Not gToastShp Is Nothing Then
        gToastShp.Visible = MSO_FALSE
    ElseIf Len(gToastSheetName) > 0 Then
        ThisWorkbook.Worksheets(gToastSheetName).Shapes("FX_TOAST").Visible = MSO_FALSE
    End If
    On Error GoTo 0
End Sub

Public Sub CleanupAllVocabFX()
    On Error Resume Next
    CleanupVocabToasts
    Set gToastShp = Nothing
    gToastSheetName = ""
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        ws.Shapes("FX_TOAST").Delete
        CleanupVocabParticles ws
    Next ws
    On Error GoTo 0
End Sub

Public Sub DismissVocabToast()
    CleanupVocabToasts
End Sub

Public Sub ShowVocabToast(ByVal ws As Worksheet, ByVal msgText As String)
    If ws Is Nothing Or Len(Trim$(msgText)) = 0 Then Exit Sub
    On Error GoTo SafeExit

    If gToastScheduled Then
        On Error Resume Next
        Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissVocabToast", Schedule:=False
        gToastScheduled = False
        On Error GoTo SafeExit
    End If

    Dim tW As Single, tH As Single, tL As Single, tT As Single
    tW = IIf(Len(msgText) > 50, 392!, 325!)
    tH = 38!
    On Error Resume Next
    Dim vr As Range
    Set vr = ActiveWindow.VisibleRange
    If Not vr Is Nothing Then
        tL = vr.Left + 14!
        tT = vr.Top + vr.Height - tH - 18!
    Else
        tL = 14!
        tT = ws.Range("A18").Top
    End If
    If tL < 10! Then tL = 10!
    If tT < 10! Then tT = 10!
    On Error GoTo SafeExit

    On Error Resume Next
    ws.Shapes("FX_TOAST").Delete
    On Error GoTo SafeExit

    Dim toast As Shape
    Set toast = ws.Shapes.AddShape(MSO_ROUNDED_RECT, Application.Max(2!, tL - 12!), tT, tW, tH)
    toast.Name = "FX_TOAST"
    toast.Adjustments(1) = 0.42
    toast.Fill.Solid
    toast.Fill.ForeColor.RGB = GetThemeRgb(3, RGB(140, 62, 92))
    toast.Line.Visible = MSO_TRUE
    toast.Line.ForeColor.RGB = GetThemeRgb(4, RGB(255, 240, 245))
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

    Application.ScreenUpdating = True
    toast.Left = Application.Max(2!, tL - 6!)
    WaitSec 0.015
    toast.Left = tL

    gToastDueTime = Now + TimeSerial(0, 0, 2)
    gToastScheduled = True
    Application.OnTime EarliestTime:=gToastDueTime, Procedure:="DismissVocabToast", Schedule:=True
SafeExit:
End Sub

' =============================================================================
'  CHIIKAWA PASTEL CELEBRATION FX (STARS + PETALS + HEARTS + BOUNCE + TOAST)
' =============================================================================
Private Sub PlayMascotBounce(ByVal ws As Worksheet, ByVal shpName As String)
    Dim shp As Shape
    On Error Resume Next
    Set shp = ws.Shapes(shpName)
    On Error GoTo 0
    If shp Is Nothing Then Exit Sub

    Dim oL As Single, oT As Single, oW As Single, oH As Single, cx As Single, cy As Single
    oL = shp.Left: oT = shp.Top: oW = shp.Width: oH = shp.Height
    cx = oL + oW / 2!: cy = oT + oH / 2!

    On Error GoTo RestoreIt
    Application.ScreenUpdating = True
    Dim fr As Variant, i As Long
    fr = Array(1#, 1.14, 0.94, 1.07, 1#)
    For i = LBound(fr) To UBound(fr)
        shp.Width = CSng(oW * CDbl(fr(i)))
        shp.Left = cx - shp.Width / 2!
        shp.Top = cy - shp.Height / 2!
        WaitSec 0.04
    Next i
RestoreIt:
    On Error Resume Next
    shp.Width = oW: shp.Height = oH: shp.Left = oL: shp.Top = oT
    On Error GoTo 0
End Sub

Public Sub PlayChiikawaCelebration(ByVal ws As Worksheet, ByVal anchorName As String, ByVal toastMsg As String)
    If Not IsFXEnabled() Then Exit Sub
    CleanupVocabParticles ws

    ShowVocabToast ws, toastMsg
    PlayMascotBounce ws, anchorName

    Dim cx As Single, cy As Single, vL As Single, vT As Single, vW As Single, vH As Single
    On Error Resume Next
    Dim vr As Range
    Set vr = ActiveWindow.VisibleRange
    If Not vr Is Nothing Then
        vL = vr.Left: vT = vr.Top: vW = vr.Width: vH = vr.Height
    Else
        vL = 16!: vT = 16!: vW = 720!: vH = 420!
    End If
    Dim aShp As Shape
    Set aShp = ws.Shapes(anchorName)
    If Not aShp Is Nothing Then
        cx = aShp.Left + aShp.Width / 2!
        cy = aShp.Top + aShp.Height / 2!
    Else
        cx = vL + vW * 0.5!: cy = vT + vH * 0.32!
    End If
    On Error GoTo WipeFX

    Const N_STARS As Long = 12
    Const N_PETALS As Long = 12
    Dim stShp(1 To N_STARS) As Shape
    Dim stVx(1 To N_STARS) As Single, stVy(1 To N_STARS) As Single, stSz(1 To N_STARS) As Single
    Dim ptShp(1 To N_PETALS) As Shape
    Dim ptX(1 To N_PETALS) As Single, ptY(1 To N_PETALS) As Single, ptVx(1 To N_PETALS) As Single, ptVy(1 To N_PETALS) As Single

    Dim pal As Variant
    pal = Array(GetThemeRgb(2, RGB(232, 114, 148)), RGB(251, 191, 36), RGB(249, 168, 212), _
                RGB(147, 197, 253), RGB(196, 181, 253), RGB(167, 243, 208))

    Application.ScreenUpdating = False
    Dim k As Long, ang As Double, spd As Single, sk As Long
    For k = 1 To N_STARS
        ang = (k - 1) * (6.2831853# / CDbl(N_STARS)) + 0.18#
        spd = 2.6! + CSng(k Mod 3) * 1.15!
        stVx(k) = CSng(Cos(ang) * spd)
        stVy(k) = CSng(Sin(ang) * spd - 0.9#)
        stSz(k) = 8.5! + CSng(k Mod 3) * 2.5!
        If (k Mod 3) = 0 Then
            sk = MSO_HEART
        ElseIf (k Mod 2) = 0 Then
            sk = MSO_STAR_5
        Else
            sk = MSO_STAR_4
        End If
        Set stShp(k) = ws.Shapes.AddShape(sk, cx - stSz(k) / 2!, cy - stSz(k) / 2!, stSz(k), stSz(k))
        stShp(k).Name = "FX_VOC_ST_" & CStr(k)
        stShp(k).Fill.Solid
        stShp(k).Fill.ForeColor.RGB = CLng(pal((k - 1) Mod 6))
        stShp(k).Line.Visible = MSO_FALSE
    Next k

    For k = 1 To N_PETALS
        ptX(k) = vL + 20! + (vW - 40!) * (CSng((k * 43) Mod 89) / 89!)
        ptY(k) = vT + 6! + (vH * 0.35!) * (CSng((k * 17) Mod 41) / 41!)
        ptVx(k) = 1.6! + CSng(k Mod 3) * 0.9!
        ptVy(k) = 4.6! + CSng(k Mod 4) * 1.7!
        Set ptShp(k) = ws.Shapes.AddShape(MSO_OVAL, ptX(k), ptY(k), 9.5!, 6!)
        ptShp(k).Name = "FX_VOC_PT_" & CStr(k)
        ptShp(k).Fill.Solid
        ptShp(k).Fill.ForeColor.RGB = CLng(pal(k Mod 6))
        ptShp(k).Line.Visible = MSO_FALSE
    Next k
    Application.ScreenUpdating = True

    Dim f As Long, sc As Single
    For f = 1 To 28
        sc = CSng(1# - CDbl(f) / 34#)
        If sc < 0.16! Then sc = 0.16!
        For k = 1 To N_STARS
            stShp(k).Left = stShp(k).Left + stVx(k)
            stShp(k).Top = stShp(k).Top + stVy(k) + CSng(f) * 0.06!
            stShp(k).Width = stSz(k) * sc
            stShp(k).Height = stSz(k) * sc
        Next k
        For k = 1 To N_PETALS
            ptX(k) = ptX(k) + ptVx(k) + CSng(Sin(CDbl(k) + CDbl(f) * 0.35#) * 2.2#)
            ptY(k) = ptY(k) + ptVy(k)
            If ptY(k) > vT + vH - 18! Then ptY(k) = vT + 6!
            ptShp(k).Left = ptX(k)
            ptShp(k).Top = ptY(k)
            ptShp(k).Rotation = CSng((f * 16 + k * 24) Mod 360)
        Next k
        WaitSec 0.055
    Next f

WipeFX:
    CleanupVocabParticles ws
End Sub

' =============================================================================
'  INTERACTIVE FLASHCARD QUIZ POP-UP ENGINE (`BtnVocabQuiz`)
'  Reads schema col indices from `_Calc!AA6:AA13` so ALL 5 distinct templates work!
'    AA6  = StartRow (15)
'    AA7  = EndRow (114)
'    AA8  = WordCol (3 = C)
'    AA9  = PronCol (4 = D)
'    AA10 = MeanCol (e.g., 5 = E or 7 = G or 6 = F)
'    AA11 = HintCol (Example / Collocation / Dialogue / Quote / Mnemonic)
'    AA12 = MasterCol (Boolean checkbox col for mastered; for SRS #96 = L (12))
'    AA13 = ModeCode (1=SRS_5STEP, 2=STANDARD_BOOL, 3=CONFIDENCE_BOOL, 4=MISTAKE_BANK)
' =============================================================================
Private Function PickQuizRow(ByVal ws As Worksheet, ByVal r0 As Long, ByVal r1 As Long, _
                             ByVal cWord As Long, ByVal cMast As Long) As Long
    Dim unmastered() As Long, allActive() As Long
    Dim uCnt As Long, aCnt As Long, r As Long, wTxt As String, isDone As Boolean
    uCnt = 0: aCnt = 0
    For r = r0 To r1
        wTxt = Trim$(CStr(ws.Cells(r, cWord).Value2))
        If Len(wTxt) > 0 Then
            aCnt = aCnt + 1
            ReDim Preserve allActive(1 To aCnt)
            allActive(aCnt) = r
            isDone = (ws.Cells(r, cMast).Value2 = True)
            If Not isDone Then
                uCnt = uCnt + 1
                ReDim Preserve unmastered(1 To uCnt)
                unmastered(uCnt) = r
            End If
        End If
    Next r
    Randomize
    If uCnt > 0 Then
        PickQuizRow = unmastered(Int(Rnd() * uCnt) + 1)
    ElseIf aCnt > 0 Then
        PickQuizRow = allActive(Int(Rnd() * aCnt) + 1)
    Else
        PickQuizRow = 0
    End If
End Function

Private Sub ApplyQuizOutcome(ByVal ws As Worksheet, ByVal r As Long, ByVal remembered As Boolean, _
                             ByVal cMast As Long, ByVal modeCode As Long)
    Application.EnableEvents = False
    On Error GoTo DoneUpd
    If modeCode = 1 Then
        ' SRS 5-Step (#96): cols H(8)..L(12) are L1..L5!
        Dim c As Long
        If remembered Then
            For c = 8 To 12
                If ws.Cells(r, c).Value2 <> True Then
                    ws.Cells(r, c).Value2 = True
                    Exit For
                End If
            Next c
        Else
            ' Reset last checked step so user reviews it again
            For c = 12 To 8 Step -1
                If ws.Cells(r, c).Value2 = True Then
                    ws.Cells(r, c).Value2 = False
                    Exit For
                End If
            Next c
        End If
    ElseIf modeCode = 4 Then
        ' Mistake Bank (#100): Col H(8)=MistakeCount, Col J(10)=Mastered
        If remembered Then
            ws.Cells(r, cMast).Value2 = True
        Else
            ws.Cells(r, cMast).Value2 = False
            ws.Cells(r, 8).Value2 = CLng(Val(ws.Cells(r, 8).Value2)) + 1
        End If
    Else
        ' Standard / IELTS / Flashcard / Media: mark mastered boolean directly!
        ws.Cells(r, cMast).Value2 = remembered
    End If
DoneUpd:
    Application.EnableEvents = True
End Sub

Public Sub BtnVocabQuiz()
    On Error GoTo SafeExit
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_VOCAB")
    If ws Is Nothing Then Set ws = ActiveSheet

    Dim r0 As Long, r1 As Long, cWord As Long, cPron As Long, cMean As Long, cHint As Long, cMast As Long, mCode As Long
    r0 = GetCfgNum(6, 15)
    r1 = GetCfgNum(7, 114)
    cWord = GetCfgNum(8, 3)
    cPron = GetCfgNum(9, 4)
    cMean = GetCfgNum(10, 5)
    cHint = GetCfgNum(11, 6)
    cMast = GetCfgNum(12, 12)
    mCode = GetCfgNum(13, 2)

    Dim qRow As Long
    qRow = PickQuizRow(ws, r0, r1, cWord, cMast)
    If qRow = 0 Then
        ShowVocabToast ws, GetVocabMsg(20)
        Exit Sub
    End If

    Dim wTxt As String, pTxt As String, mTxt As String, hTxt As String
    wTxt = Trim$(CStr(ws.Cells(qRow, cWord).Value2))
    pTxt = Trim$(CStr(ws.Cells(qRow, cPron).Value2))
    mTxt = Trim$(CStr(ws.Cells(qRow, cMean).Value2))
    hTxt = Trim$(CStr(ws.Cells(qRow, cHint).Value2))

    Dim titleTxt As String
    titleTxt = GetVocabMsg(16)
    Dim askBody As String
    askBody = wTxt & IIf(Len(pTxt) > 0, "  " & pTxt, "") & vbCrLf & vbCrLf & GetVocabMsg(17)
    If MsgBox(askBody, vbOKCancel + vbQuestion, titleTxt) = vbCancel Then Exit Sub

    Dim ansBody As String
    ansBody = wTxt & IIf(Len(pTxt) > 0, "  " & pTxt, "") & vbCrLf & _
              "-> " & mTxt & vbCrLf & _
              IIf(Len(hTxt) > 0, vbCrLf & hTxt & vbCrLf, "") & vbCrLf & _
              GetVocabMsg(18)
    Dim resp As VbMsgBoxResult
    resp = MsgBox(ansBody, vbYesNoCancel + vbInformation, titleTxt)
    If resp = vbCancel Then Exit Sub

    If resp = vbYes Then
        ApplyQuizOutcome ws, qRow, True, cMast, mCode
        SyncAllVocabSprites
        ShowVocabToast ws, GetVocabMsg(19)
    ElseIf resp = vbNo Then
        ApplyQuizOutcome ws, qRow, False, cMast, mCode
        SyncAllVocabSprites
        ShowVocabToast ws, GetVocabMsg(21)
    End If
SafeExit:
    Application.EnableEvents = True
End Sub

Public Function VerifyQuizEngineHeadless() As Long
    ' Non-modal self-test used by automated Excel COM QA (zero MsgBox blocking!)
    Dim ws As Worksheet
    Set ws = GetAnchorSheet("ANCHOR_VOCAB")
    If ws Is Nothing Then
        VerifyQuizEngineHeadless = 0
        Exit Function
    End If
    Dim r0 As Long, r1 As Long, cWord As Long, cMast As Long
    r0 = GetCfgNum(6, 15)
    r1 = GetCfgNum(7, 114)
    cWord = GetCfgNum(8, 3)
    cMast = GetCfgNum(12, 12)
    VerifyQuizEngineHeadless = PickQuizRow(ws, r0, r1, cWord, cMast)
End Function

Public Sub BtnVocabToggleFX()
    On Error GoTo SafeExit
    Dim wsCalc As Worksheet, wsV As Worksheet
    Set wsCalc = GetCalcSheet()
    Set wsV = GetAnchorSheet("ANCHOR_VOCAB")
    Dim newState As Boolean
    gFXCached = False
    newState = Not IsFXEnabled()
    wsCalc.Range("AA1").Value2 = newState
    gFXVal = newState
    gFXCached = True

    If Not wsV Is Nothing Then
        On Error Resume Next
        Dim btn As Shape
        Set btn = wsV.Shapes("BTN_FX_TOGGLE")
        If Not btn Is Nothing Then
            If newState Then
                btn.TextFrame2.TextRange.Text = GetVocabMsg(22)
                btn.Fill.ForeColor.RGB = GetThemeRgb(2, RGB(226, 113, 146))
                btn.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = RGB(255, 255, 255)
            Else
                btn.TextFrame2.TextRange.Text = GetVocabMsg(23)
                btn.Fill.ForeColor.RGB = RGB(229, 231, 235)
                btn.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = RGB(75, 85, 99)
            End If
        End If
        On Error GoTo SafeExit
        ShowVocabToast wsV, GetVocabMsg(IIf(newState, 24, 25))
    End If
SafeExit:
End Sub

Public Sub BtnVocabDemoFX()
    On Error GoTo SafeExit
    Dim wsA As Worksheet
    Set wsA = ActiveSheet
    If wsA Is Nothing Then Set wsA = GetAnchorSheet("ANCHOR_GUIDE")
    Dim prevFX As Boolean
    prevFX = IsFXEnabled()
    GetCalcSheet().Range("AA1").Value2 = True
    gFXVal = True
    gFXCached = True

    Dim anchorShp As String
    On Error Resume Next
    If Not wsA.Shapes("Guide_Stage5") Is Nothing Then
        anchorShp = "Guide_Stage5"
    Else
        anchorShp = "SPR_VHERO_S" & CStr(StageIdxFromCell("C6") - 1)
    End If
    On Error GoTo SafeExit

    PlayChiikawaCelebration wsA, anchorShp, GetVocabMsg(14)
    GetCalcSheet().Range("AA1").Value2 = prevFX
    gFXVal = prevFX
SafeExit:
End Sub
