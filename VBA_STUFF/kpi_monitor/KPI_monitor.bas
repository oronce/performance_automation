Attribute VB_Name = "KPI_AUTOMATION"
' ===================================================================
' Main Module - KPI_AUTOMATION (UPDATED with Multi-Worksheet Support)
' ===================================================================

Option Explicit

' UPDATED Type - now includes source worksheet and multi-KPI support
Public Type ChartConfig
    KPIField As String
    AggregationType As String
    chartName As String
    LegendField As String
    XAxisFields As String
    SourceWorksheet As String ' NEW: stores which worksheet this chart pulls from
    ' Multi-KPI support (NEW)
    KPIFields_Multi As String ' Comma-separated KPI fields (e.g., "CSSR,CBR,DROP")
    AggregationTypes_Multi As String ' Comma-separated aggregations (e.g., "AVG,SUM,AVG")
    IsMultiKPI As Boolean ' True if using multi-KPI mode
End Type

Public ChartConfigs() As ChartConfig
Public ConfigCount As Integer

Sub ShowKPIForm()
    UserForm_KPIAutomation.Show
End Sub

Sub CreatePivotChartsFromConfigs(wsDestination As Worksheet)
    ' UPDATED: Now pulls from different source worksheets based on config
    
    Dim i As Integer
    Dim pc As PivotCache
    Dim pt As PivotTable
    Dim cht As Chart
    Dim chtObj As ChartObject
    Dim chartRow As Long
    Dim chartCol As Long
    Dim chartsPerRow As Integer
    Dim pivotRow As Long
    Dim pivotCol As Long
    Dim pivotsPerRow As Integer
    Dim maxPivotHeight As Long
    Dim xFields As Variant
    Dim j As Integer
    
    ' NEW: Variables for handling different source worksheets
    Dim wsSource As Worksheet
    Dim dataRange As Range
    
    On Error GoTo ErrorHandler
    
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    chartRow = 2
    chartCol = 10
    chartsPerRow = 2
    pivotRow = 2
    pivotCol = 1
    pivotsPerRow = 2
    maxPivotHeight = 0
    
    For i = 1 To ConfigCount
        
        ' NEW: Get source worksheet for THIS chart
        If ChartConfigs(i).SourceWorksheet <> "" Then
            On Error Resume Next
            Set wsSource = ThisWorkbook.worksheets(ChartConfigs(i).SourceWorksheet)
            On Error GoTo ErrorHandler
            
            If wsSource Is Nothing Then
                MsgBox "Warning: Source worksheet '" & ChartConfigs(i).SourceWorksheet & "' not found for chart " & i & ". Skipping.", vbExclamation
                GoTo NextChart
            End If
        Else
            ' Fallback to active sheet if no source specified
            Set wsSource = ActiveSheet
        End If
        
        ' Get data range from the source worksheet
        Set dataRange = GetDataRange(wsSource)
        
        ' Create pivot cache from this specific worksheet
        Set pc = ThisWorkbook.PivotCaches.Create( _
            SourceType:=xlDatabase, _
            SourceData:=dataRange)
        
        ' Calculate pivot position
        Dim pivotLeftCol As Long
        Dim pivotTopRow As Long
        
        If (i - 1) Mod pivotsPerRow = 0 Then
            pivotLeftCol = pivotCol
        Else
            pivotLeftCol = pivotCol + 10
        End If
        
        pivotTopRow = pivotRow
        
        ' Create pivot table
        Set pt = pc.CreatePivotTable( _
            TableDestination:=wsDestination.Cells(pivotTopRow, pivotLeftCol), _
            TableName:="PivotTable_" & i)
        
        With pt
            ' Add Row Fields (X-Axis)
            If ChartConfigs(i).XAxisFields <> "" Then
                xFields = Split(ChartConfigs(i).XAxisFields, ",")
                For j = LBound(xFields) To UBound(xFields)
                    On Error Resume Next
                    .PivotFields(Trim(xFields(j))).Orientation = xlRowField
                    On Error GoTo ErrorHandler
                Next j
            End If
            
            ' Add Column Field (Legend)
            If ChartConfigs(i).LegendField <> "" Then
                On Error Resume Next
                .PivotFields(ChartConfigs(i).LegendField).Orientation = xlColumnField
                On Error GoTo ErrorHandler
            End If
            
            ' Add Data Field(s) - Single or Multi-KPI
            If ChartConfigs(i).IsMultiKPI And ChartConfigs(i).KPIFields_Multi <> "" Then
                ' MULTI-KPI MODE: Add multiple data fields
                Dim kpiFields As Variant
                Dim aggTypes As Variant
                Dim k As Integer
                Dim kpiFieldName As String
                Dim aggType As String

                kpiFields = Split(ChartConfigs(i).KPIFields_Multi, ",")
                aggTypes = Split(ChartConfigs(i).AggregationTypes_Multi, ",")

                For k = LBound(kpiFields) To UBound(kpiFields)
                    kpiFieldName = Trim(kpiFields(k))

                    ' Get corresponding aggregation type
                    If k <= UBound(aggTypes) Then
                        aggType = Trim(aggTypes(k))
                    Else
                        aggType = "SUM" ' Default fallback
                    End If

                    On Error Resume Next
                    With .PivotFields(kpiFieldName)
                        .Orientation = xlDataField

                        Select Case UCase(aggType)
                            Case "SUM"
                                .Function = xlSum
                                .Caption = "Sum of " & kpiFieldName
                            Case "AVERAGE", "AVG"
                                .Function = xlAverage
                                .Caption = "Avg of " & kpiFieldName
                            Case "COUNT"
                                .Function = xlCount
                                .Caption = "Count of " & kpiFieldName
                            Case Else
                                .Function = xlSum
                                .Caption = "Sum of " & kpiFieldName
                        End Select
                    End With
                    On Error GoTo ErrorHandler
                Next k
            Else
                ' SINGLE KPI MODE (backward compatible)
                With .PivotFields(ChartConfigs(i).KPIField)
                    .Orientation = xlDataField

                    Select Case UCase(ChartConfigs(i).AggregationType)
                        Case "SUM"
                            .Function = xlSum
                            .Caption = "Sum of " & ChartConfigs(i).KPIField
                        Case "AVERAGE", "AVG"
                            .Function = xlAverage
                            .Caption = "Avg of " & ChartConfigs(i).KPIField
                        Case "COUNT"
                            .Function = xlCount
                            .Caption = "Count of " & ChartConfigs(i).KPIField
                        Case Else
                            .Function = xlSum
                    End Select
                End With
            End If
            
            .RowAxisLayout xlTabularRow
            .RepeatAllLabels xlRepeatLabels
            .ColumnGrand = False
            .RowGrand = False
            .DisplayFieldCaptions = False
        End With
        
        Dim pivotHeight As Long
        Dim pivotWidth As Long
        
        pt.RefreshTable
        DoEvents
        
        pivotHeight = pt.TableRange2.rows.Count
        pivotWidth = pt.TableRange2.Columns.Count
        
        If pivotHeight > maxPivotHeight Then
            maxPivotHeight = pivotHeight
        End If
        
        Dim ptStartCell As Range
        Set ptStartCell = pt.TableRange2.Cells(1, 1)
        
        wsDestination.Select
        ptStartCell.Select
        
        ' Create chart
        Dim chartLeftPos As Long
        Dim chartTopPos As Long
        Dim chartWidth As Long
        Dim chartHeight As Long
        
        chartWidth = 450
        chartHeight = 280
        
        If (i - 1) Mod chartsPerRow = 0 Then
            chartLeftPos = wsDestination.Cells(chartRow, 10).Left
        Else
            chartLeftPos = wsDestination.Cells(chartRow, 10).Left + chartWidth + 30
        End If
        
        chartTopPos = wsDestination.Cells(chartRow, 10).Top
        
        Set chtObj = wsDestination.ChartObjects.Add( _
            Left:=chartLeftPos, _
            Top:=chartTopPos, _
            Width:=chartWidth, _
            Height:=chartHeight)
        
        Set cht = chtObj.Chart
        cht.ChartType = xlLine
        cht.SetSourceData Source:=ptStartCell
        
        With cht
            .ChartType = xlLine
            
            If ChartConfigs(i).chartName <> "" Then
                .HasTitle = True
                .chartTitle.Text = ChartConfigs(i).chartName
            Else
                .HasTitle = True
                .chartTitle.Text = ChartConfigs(i).KPIField
            End If
            
            On Error Resume Next
            .Axes(xlValue).HasMajorGridlines = False
            .Axes(xlValue).HasMinorGridlines = False
            On Error GoTo ErrorHandler
            
            .HasLegend = True
            .Legend.Position = xlLegendPositionBottom
            
            .Axes(xlCategory).TickLabels.Font.Size = 9
            .Axes(xlCategory).MajorTickMark = xlTickMarkNone
            .Axes(xlValue).TickLabels.Font.Size = 9
            .Axes(xlValue).Format.Line.Visible = msoFalse
            .Legend.Font.Size = 9
            .Legend.Position = xlLegendPositionRight
            .chartTitle.Font.Size = 14
        End With
        
NextChart:
        If i Mod chartsPerRow = 0 Then
            chartRow = chartRow + 20
            pivotRow = pivotRow + maxPivotHeight + 3
            maxPivotHeight = 0
        End If
        
    Next i
    
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    
    MsgBox ConfigCount & " pivot chart(s) created successfully!", vbInformation
    Exit Sub
    
ErrorHandler:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    MsgBox "Error creating pivot charts: " & Err.Description & vbCrLf & "Chart: " & i, vbCritical
End Sub

Function GetDataRange(ws As Worksheet) As Range
    Dim lastRow As Long
    Dim lastCol As Long
    
    With ws
        lastRow = .Cells(.rows.Count, 1).End(xlUp).Row
        lastCol = .Cells(1, .Columns.Count).End(xlToLeft).Column
        Set GetDataRange = .Range(.Cells(1, 1), .Cells(lastRow, lastCol))
    End With
End Function

Function GetUniqueFieldNames(dataRange As Range) As Variant
    Dim i As Long
    Dim fields() As String
    Dim headerRow As Range
    
    Set headerRow = dataRange.rows(1)
    ReDim fields(1 To headerRow.Columns.Count)
    
    For i = 1 To headerRow.Columns.Count
        fields(i) = headerRow.Cells(1, i).Value
    Next i
    
    GetUniqueFieldNames = fields
End Function

' ===================================================================
' CONFIGURATION SAVE/LOAD (UPDATED with SourceWorksheet)
' ===================================================================

Function GetConfigSheet() As Worksheet
    Dim ws As Worksheet
    Const CONFIG_SHEET_NAME As String = "_KPI_Configs"
    
    On Error Resume Next
    Set ws = ThisWorkbook.worksheets(CONFIG_SHEET_NAME)
    On Error GoTo 0
    
    If ws Is Nothing Then
        Set ws = ThisWorkbook.worksheets.Add
        ws.Name = CONFIG_SHEET_NAME
        ws.Visible = xlSheetVeryHidden
        
        ' UPDATED: Added SourceWorksheet column and Multi-KPI columns
        ws.Range("A1").Value = "ConfigName"
        ws.Range("B1").Value = "KPIField"
        ws.Range("C1").Value = "AggregationType"
        ws.Range("D1").Value = "ChartName"
        ws.Range("E1").Value = "LegendField"
        ws.Range("F1").Value = "XAxisFields"
        ws.Range("G1").Value = "SourceWorksheet"
        ws.Range("H1").Value = "KPIFields_Multi" ' NEW: Multi-KPI fields
        ws.Range("I1").Value = "AggregationTypes_Multi" ' NEW: Multi-KPI aggregations
        ws.Range("J1").Value = "IsMultiKPI" ' NEW: Multi-KPI flag

        ws.Range("A1:J1").Font.Bold = True
        ws.Range("A1:J1").Interior.Color = RGB(200, 200, 200)
    End If
    
    Set GetConfigSheet = ws
End Function

Sub SaveConfiguration(configName As String)
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Integer
    
    If ConfigCount = 0 Then
        MsgBox "No configurations to save!", vbExclamation
        Exit Sub
    End If
    
    If Trim(configName) = "" Then
        MsgBox "Please provide a configuration name!", vbExclamation
        Exit Sub
    End If
    
    Set ws = GetConfigSheet()
    
    Dim cell As Range
    Set cell = ws.Columns(1).Find(What:=configName, LookIn:=xlValues, LookAt:=xlWhole)
    
    If Not cell Is Nothing Then
        If MsgBox("Configuration '" & configName & "' already exists. Overwrite?", vbYesNo + vbQuestion) = vbNo Then
            Exit Sub
        End If
        DeleteConfiguration configName
    End If
    
    lastRow = ws.Cells(ws.rows.Count, 1).End(xlUp).Row + 1

    ' UPDATED: Save with SourceWorksheet and Multi-KPI data
    For i = 1 To ConfigCount
        ws.Cells(lastRow, 1).Value = configName
        ws.Cells(lastRow, 2).Value = ChartConfigs(i).KPIField
        ws.Cells(lastRow, 3).Value = ChartConfigs(i).AggregationType
        ws.Cells(lastRow, 4).Value = ChartConfigs(i).chartName
        ws.Cells(lastRow, 5).Value = ChartConfigs(i).LegendField
        ws.Cells(lastRow, 6).Value = ChartConfigs(i).XAxisFields
        ws.Cells(lastRow, 7).Value = ChartConfigs(i).SourceWorksheet
        ws.Cells(lastRow, 8).Value = ChartConfigs(i).KPIFields_Multi ' NEW
        ws.Cells(lastRow, 9).Value = ChartConfigs(i).AggregationTypes_Multi ' NEW
        ws.Cells(lastRow, 10).Value = ChartConfigs(i).IsMultiKPI ' NEW
        lastRow = lastRow + 1
    Next i
    
    MsgBox "Configuration '" & configName & "' saved successfully!", vbInformation
End Sub

Function LoadConfiguration(configName As String) As Boolean
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    
    LoadConfiguration = False
    
    Set ws = GetConfigSheet()
    lastRow = ws.Cells(ws.rows.Count, 1).End(xlUp).Row
    
    ConfigCount = 0
    ReDim ChartConfigs(1 To 1)

    ' UPDATED: Load with SourceWorksheet and Multi-KPI data
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = configName Then
            ConfigCount = ConfigCount + 1
            ReDim Preserve ChartConfigs(1 To ConfigCount)

            With ChartConfigs(ConfigCount)
                .KPIField = ws.Cells(i, 2).Value
                .AggregationType = ws.Cells(i, 3).Value
                .chartName = ws.Cells(i, 4).Value
                .LegendField = ws.Cells(i, 5).Value
                .XAxisFields = ws.Cells(i, 6).Value
                .SourceWorksheet = ws.Cells(i, 7).Value
                .KPIFields_Multi = ws.Cells(i, 8).Value ' NEW
                .AggregationTypes_Multi = ws.Cells(i, 9).Value ' NEW
                .IsMultiKPI = ws.Cells(i, 10).Value ' NEW
            End With
        End If
    Next i
    
    If ConfigCount > 0 Then
        LoadConfiguration = True
    Else
        MsgBox "Configuration '" & configName & "' not found!", vbExclamation
    End If
End Function

Sub DeleteConfiguration(configName As String)
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    
    Set ws = GetConfigSheet()
    lastRow = ws.Cells(ws.rows.Count, 1).End(xlUp).Row
    
    For i = lastRow To 2 Step -1
        If ws.Cells(i, 1).Value = configName Then
            ws.rows(i).Delete
        End If
    Next i
End Sub

Function GetSavedConfigNames() As Variant
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim configNames As Collection
    Dim configArray() As String
    Dim configName As String
    Dim j As Long
    
    Set ws = GetConfigSheet()
    lastRow = ws.Cells(ws.rows.Count, 1).End(xlUp).Row
    
    Set configNames = New Collection
    
    For i = 2 To lastRow
        configName = ws.Cells(i, 1).Value
        If configName <> "" Then
            On Error Resume Next
            configNames.Add configName, configName
            On Error GoTo 0
        End If
    Next i
    
    If configNames.Count > 0 Then
        ReDim configArray(1 To configNames.Count)
        For j = 1 To configNames.Count
            configArray(j) = configNames(j)
        Next j
        GetSavedConfigNames = configArray
    Else
        GetSavedConfigNames = Array()
    End If
End Function


