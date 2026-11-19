VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "SheetTrackerEvents"
Option Explicit

' =============================================================================
'  Worksheet Event Handler — Paste into your main Tracker sheet code window
'  Enables:
'    1) Single-click toggle (TRUE/FALSE or checkbox symbol) in legacy Excel
'    2) Instant offline sprite swap when _SpritesVBA sheet is installed
'    3) Micro celebration status banner on 100% days & 7/14/21/30-day streaks
' =============================================================================

Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)
    Dim grid As Range
    Set grid = Me.Range(HabitTrackerPro.HABIT_GRID)
    If Target.CountLarge > 1 Then Exit Sub
    If Intersect(Target, grid) Is Nothing Then Exit Sub
    ' Ignore out-of-month blank days
    If Trim$(CStr(Me.Cells(16, Target.Column).Value)) = "" Then Exit Sub

    Cancel = True
    Application.EnableEvents = False
    If Target.Value = True Or Target.Value = ChrW(10003) Or Target.Value = ChrW(9745) Then
        Target.Value = False
    Else
        Target.Value = True
    End If
    Application.EnableEvents = True

    HabitTrackerPro.RefreshDaySprite Me, Target.Column
    HabitTrackerPro.CheckAndCelebrate Me, Target
End Sub

Private Sub Worksheet_Change(ByVal Target As Range)
    Dim grid As Range
    Dim cell As Range
    Set grid = Me.Range(HabitTrackerPro.HABIT_GRID)
    If Intersect(Target, grid) Is Nothing Then Exit Sub
    If Target.CountLarge > 31 Then
        HabitTrackerPro.RefreshAllOfflineStages Me
        Exit Sub
    End If

    For Each cell In Intersect(Target, grid)
        HabitTrackerPro.RefreshDaySprite Me, cell.Column
    Next cell
    If Target.CountLarge = 1 Then
        HabitTrackerPro.CheckAndCelebrate Me, Target
    End If
End Sub
