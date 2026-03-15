VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} UserForm_KPIAutomation 
   Caption         =   "UserForm1"
   ClientHeight    =   10008
   ClientLeft      =   110
   ClientTop       =   460
   ClientWidth     =   13710
   OleObjectBlob   =   "UserForm_KPIAutomation.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "UserForm_KPIAutomation"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
' ===================================================================
' UserForm - KPIAutomation (UPDATED with Source Worksheet Selection)
' ===================================================================

Option Explicit

Private wsSource As Worksheet
Private dataRange As Range
Private fieldNames As Variant

' Multi-KPI tracking collections
Private MultiKPIList As Collection ' Stores selected KPIs
Private MultiAggList As Collection ' Stores selected aggregations per KPI

Private Sub UserForm_Initialize()
    On Error GoTo ErrorHandler
    
    ' Load all worksheets into source dropdown
    LoadWorksheetList
    
    ' Set default to active sheet
    Dim i As Integer
    For i = 0 To cboSourceWorksheet.ListCount - 1
        If cboSourceWorksheet.List(i) = ActiveSheet.Name Then
            cboSourceWorksheet.ListIndex = i
            Exit For
        End If
    Next i
    
    ' If active sheet not found, select first
    If cboSourceWorksheet.ListIndex = -1 And cboSourceWorksheet.ListCount > 0 Then
        cboSourceWorksheet.ListIndex = 0
    End If
    
    ' Load fields from selected worksheet
    LoadFieldsFromSelectedWorksheet
    
    ' Setup aggregation options
    cboAggregation.AddItem "SUM"
    cboAggregation.AddItem "AVERAGE"
    cboAggregation.AddItem "COUNT"
    cboAggregation.ListIndex = 0

    lstXAxis.MultiSelect = fmMultiSelectMulti

    ' Initialize Multi-KPI collections
    Set MultiKPIList = New Collection
    Set MultiAggList = New Collection

    ' Setup Multi-KPI mode controls (initially hidden)
    ToggleMultiKPIMode False
    
    ConfigCount = 0
    ReDim ChartConfigs(1 To 1)
    
    LoadSavedConfigNames
    
    ' Set default worksheet name
    txtWorksheetName.Value = "KPI_Charts_" & Format(Now, "yyyymmdd_hhmmss")
    
    Me.Caption = "Telco KPI Chart Automation"
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Error initializing form: " & Err.Description, vbCritical
End Sub

Private Sub LoadWorksheetList()
    ' NEW: Loads all worksheets into dropdown
    Dim ws As Worksheet
    
    cboSourceWorksheet.Clear
    
    For Each ws In ThisWorkbook.worksheets
        If ws.Visible = xlSheetVisible Then
            cboSourceWorksheet.AddItem ws.Name
        End If
    Next ws
End Sub

Private Sub cboSourceWorksheet_Change()
    ' NEW: Reload fields when source worksheet changes
    LoadFieldsFromSelectedWorksheet
End Sub

Private Sub LoadFieldsFromSelectedWorksheet()
    ' NEW: Loads fields from selected source worksheet
    
    If cboSourceWorksheet.Value = "" Then Exit Sub
    
    On Error Resume Next
    Set wsSource = ThisWorkbook.worksheets(cboSourceWorksheet.Value)
    On Error GoTo 0
    
    If wsSource Is Nothing Then Exit Sub
    
    Set dataRange = GetDataRange(wsSource)
    fieldNames = GetUniqueFieldNames(dataRange)

    ' Clear and reload dropdowns
    cboKPI.Clear
    cboLegend.Clear
    lstXAxis.Clear
    lstKPI_Multi.Clear ' NEW: Multi-KPI listbox

    Dim i As Integer
    For i = LBound(fieldNames) To UBound(fieldNames)
        If fieldNames(i) <> "" Then
            cboKPI.AddItem fieldNames(i)
            cboLegend.AddItem fieldNames(i)
            lstXAxis.AddItem fieldNames(i)
            lstKPI_Multi.AddItem fieldNames(i) ' NEW: Multi-KPI listbox
        End If
    Next i

    ' Setup Multi-KPI aggregation dropdown
    If cboAggregation_Multi.ListCount = 0 Then
        cboAggregation_Multi.AddItem "SUM"
        cboAggregation_Multi.AddItem "AVERAGE"
        cboAggregation_Multi.AddItem "COUNT"
        cboAggregation_Multi.ListIndex = 0
    End If
    
    ' Auto-select first two X-axis items
    If lstXAxis.ListCount > 0 Then
        lstXAxis.Selected(0) = True
        If lstXAxis.ListCount > 1 Then
            lstXAxis.Selected(1) = True
        End If
    End If
End Sub

Private Sub LoadSavedConfigNames()
    Dim configs As Variant
    Dim i As Integer
    
    cboSavedConfigs.Clear
    configs = KPI_AUTOMATION.GetSavedConfigNames()
    
    If IsArray(configs) Then
        For i = LBound(configs) To UBound(configs)
            cboSavedConfigs.AddItem configs(i)
        Next i
    End If
End Sub

Private Sub btnAddChart_Click()
    ' UPDATED: Now handles both single and multi-KPI modes

    If cboSourceWorksheet.Value = "" Then
        MsgBox "Please select a source worksheet", vbExclamation
        Exit Sub
    End If

    ' Check Multi-KPI or Single KPI mode
    Dim isMultiMode As Boolean
    isMultiMode = chkMultiKPI.Value

    If isMultiMode Then
        ' MULTI-KPI MODE validation
        If MultiKPIList.Count = 0 Then
            MsgBox "Please add at least one KPI to the Multi-KPI list", vbExclamation
            Exit Sub
        End If
    Else
        ' SINGLE KPI MODE validation
        If cboKPI.Value = "" Then
            MsgBox "Please select a KPI field", vbExclamation
            Exit Sub
        End If

        If cboAggregation.Value = "" Then
            MsgBox "Please select an aggregation type", vbExclamation
            Exit Sub
        End If
    End If
    
    Dim xAxisSelected As Boolean
    Dim i As Integer
    xAxisSelected = False
    For i = 0 To lstXAxis.ListCount - 1
        If lstXAxis.Selected(i) Then
            xAxisSelected = True
            Exit For
        End If
    Next i
    
    If Not xAxisSelected Then
        MsgBox "Please select at least one X-Axis field", vbExclamation
        Exit Sub
    End If
    
    ConfigCount = ConfigCount + 1
    ReDim Preserve ChartConfigs(1 To ConfigCount)

    Dim XAxisFields As String
    XAxisFields = ""
    For i = 0 To lstXAxis.ListCount - 1
        If lstXAxis.Selected(i) Then
            If XAxisFields <> "" Then XAxisFields = XAxisFields & ","
            XAxisFields = XAxisFields & lstXAxis.List(i)
        End If
    Next i

    With ChartConfigs(ConfigCount)
        .LegendField = cboLegend.Value
        .XAxisFields = XAxisFields
        .SourceWorksheet = cboSourceWorksheet.Value

        ' Set Multi-KPI or Single KPI data
        If isMultiMode Then
            ' MULTI-KPI MODE
            .IsMultiKPI = True

            ' Build comma-separated KPI fields and aggregations
            Dim kpiFieldsStr As String
            Dim aggTypesStr As String
            Dim j As Integer

            kpiFieldsStr = ""
            aggTypesStr = ""

            For j = 1 To MultiKPIList.Count
                If kpiFieldsStr <> "" Then kpiFieldsStr = kpiFieldsStr & ","
                If aggTypesStr <> "" Then aggTypesStr = aggTypesStr & ","

                kpiFieldsStr = kpiFieldsStr & MultiKPIList(j)
                aggTypesStr = aggTypesStr & MultiAggList(j)
            Next j

            .KPIFields_Multi = kpiFieldsStr
            .AggregationTypes_Multi = aggTypesStr

            ' Set defaults for backward compatibility
            .KPIField = MultiKPIList(1) ' First KPI
            .AggregationType = MultiAggList(1) ' First Agg

            If txtChartName.Value <> "" Then
                .chartName = txtChartName.Value
            Else
                .chartName = "Multi-KPI Chart"
            End If
        Else
            ' SINGLE KPI MODE
            .IsMultiKPI = False
            .KPIField = cboKPI.Value
            .AggregationType = cboAggregation.Value
            .KPIFields_Multi = ""
            .AggregationTypes_Multi = ""

            If txtChartName.Value <> "" Then
                .chartName = txtChartName.Value
            Else
                .chartName = cboKPI.Value
            End If
        End If
    End With

    ' Display in chart list
    Dim displayText As String
    If isMultiMode Then
        displayText = ChartConfigs(ConfigCount).chartName & " (Multi-KPI: " & _
                      MultiKPIList.Count & " fields | " & _
                      ChartConfigs(ConfigCount).SourceWorksheet & ")"
    Else
        displayText = ChartConfigs(ConfigCount).chartName & " (" & _
                      ChartConfigs(ConfigCount).AggregationType & " - " & _
                      ChartConfigs(ConfigCount).KPIField & " | " & _
                      ChartConfigs(ConfigCount).SourceWorksheet & ")"
    End If

    lstCharts.AddItem displayText

    ' Clear inputs
    txtChartName.Value = ""

    ' Clear multi-KPI list if in multi mode
    If isMultiMode Then
        lstMultiKPIDisplay.Clear
        Set MultiKPIList = New Collection
        Set MultiAggList = New Collection
    End If

    MsgBox "Chart added from '" & cboSourceWorksheet.Value & "'!", vbInformation
End Sub

Private Sub btnRemoveChart_Click()
    Dim selectedIndex As Integer
    selectedIndex = lstCharts.ListIndex
    
    If selectedIndex = -1 Then
        MsgBox "Please select a chart to remove", vbExclamation
        Exit Sub
    End If
    
    lstCharts.RemoveItem selectedIndex
    
    Dim i As Integer
    For i = selectedIndex + 1 To ConfigCount
        ChartConfigs(i) = ChartConfigs(i + 1)
    Next i
    
    ConfigCount = ConfigCount - 1
    
    If ConfigCount > 0 Then
        ReDim Preserve ChartConfigs(1 To ConfigCount)
    Else
        ReDim ChartConfigs(1 To 1)
    End If
End Sub

Private Sub btnGenerate_Click()
    ' UPDATED: No longer needs dataRange parameter - gets it from configs
    
    If ConfigCount = 0 Then
        MsgBox "Please add at least one chart configuration", vbExclamation
        Exit Sub
    End If
    
    Dim sheetName As String
    sheetName = Trim(txtWorksheetName.Value)
    
    If sheetName = "" Then
        MsgBox "Please enter a worksheet name", vbExclamation
        Exit Sub
    End If
    
    Dim wsOutput As Worksheet
    Dim sheetExists As Boolean
    
    sheetExists = False
    On Error Resume Next
    Set wsOutput = ThisWorkbook.worksheets(sheetName)
    sheetExists = (Not wsOutput Is Nothing)
    On Error GoTo 0
    
    If sheetExists Then
        Dim response As VbMsgBoxResult
        response = MsgBox("Worksheet '" & sheetName & "' already exists." & vbCrLf & vbCrLf & _
                         "Delete and create new?", _
                         vbYesNo + vbQuestion, "Worksheet Exists")
        
        If response = vbYes Then
            Application.DisplayAlerts = False
            wsOutput.Delete
            Application.DisplayAlerts = True
        Else
            Exit Sub
        End If
    End If
    
    Set wsOutput = ThisWorkbook.worksheets.Add
    wsOutput.Name = sheetName
    
    Me.Hide
    
    ' UPDATED: No dataRange parameter needed
    CreatePivotChartsFromConfigs wsOutput
    
    Unload Me
End Sub

Private Sub btnCancel_Click()
    Unload Me
End Sub

' ===================================================================
' CONFIG SAVE/LOAD/DELETE
' ===================================================================

Private Sub btnSaveConfig_Click()
    Dim configName As String
    configName = Trim(txtConfigName.Value)
    
    If configName = "" Then
        MsgBox "Please enter a name for this configuration", vbExclamation
        Exit Sub
    End If
    
    If ConfigCount = 0 Then
        MsgBox "No charts to save!", vbExclamation
        Exit Sub
    End If
    
    SaveConfiguration configName
    LoadSavedConfigNames
    
    Dim i As Integer
    For i = 0 To cboSavedConfigs.ListCount - 1
        If cboSavedConfigs.List(i) = configName Then
            cboSavedConfigs.ListIndex = i
            Exit For
        End If
    Next i
End Sub

Private Sub btnLoadConfig_Click()
    Dim configName As String
    configName = cboSavedConfigs.Value
    
    If configName = "" Then
        MsgBox "Please select a configuration to load", vbExclamation
        Exit Sub
    End If
    
    If ConfigCount > 0 Then
        If MsgBox("Loading will replace current charts. Continue?", vbYesNo + vbQuestion) = vbNo Then
            Exit Sub
        End If
    End If
    
    If LoadConfiguration(configName) Then
        RefreshChartList
        MsgBox "Configuration loaded! (" & ConfigCount & " chart(s) from multiple sources)", vbInformation
    End If
End Sub

Private Sub btnDeleteConfig_Click()
    Dim configName As String
    configName = cboSavedConfigs.Value
    
    If configName = "" Then
        MsgBox "Please select a configuration to delete", vbExclamation
        Exit Sub
    End If
    
    If MsgBox("Delete '" & configName & "'?", vbYesNo + vbQuestion) = vbYes Then
        DeleteConfiguration configName
        LoadSavedConfigNames
        MsgBox "Configuration deleted!", vbInformation
    End If
End Sub

Private Sub RefreshChartList()
    ' UPDATED: Show source worksheet and multi-KPI info
    Dim i As Integer
    Dim displayText As String
    lstCharts.Clear

    For i = 1 To ConfigCount
        If ChartConfigs(i).IsMultiKPI Then
            ' Multi-KPI chart display
            Dim kpiCount As Integer
            kpiCount = UBound(Split(ChartConfigs(i).KPIFields_Multi, ",")) + 1
            displayText = ChartConfigs(i).chartName & " (Multi-KPI: " & _
                          kpiCount & " fields | " & _
                          ChartConfigs(i).SourceWorksheet & ")"
        Else
            ' Single KPI chart display
            displayText = ChartConfigs(i).chartName & " (" & _
                          ChartConfigs(i).AggregationType & " - " & _
                          ChartConfigs(i).KPIField & " | " & _
                          ChartConfigs(i).SourceWorksheet & ")"
        End If
        lstCharts.AddItem displayText
    Next i
End Sub

' ===================================================================
' AUTO-GENERATE CHART NAME
' ===================================================================

Private Sub cboKPI_Change()
    If txtChartName.Value = "" And cboKPI.Value <> "" Then
        txtChartName.Value = cboKPI.Value
    End If
End Sub

Private Sub cboAggregation_Change()
    If txtChartName.Value = "" And cboKPI.Value <> "" Then
        txtChartName.Value = cboKPI.Value
    End If
End Sub

' ===================================================================
' MULTI-KPI MODE FUNCTIONS (NEW)
' ===================================================================

Private Sub chkMultiKPI_Change()
    ' Toggle between single and multi-KPI mode
    ToggleMultiKPIMode chkMultiKPI.Value
End Sub

Private Sub ToggleMultiKPIMode(isMultiMode As Boolean)
    ' Show/hide controls based on mode
    If isMultiMode Then
        ' MULTI-KPI MODE
        cboKPI.Visible = False
        cboAggregation.Visible = False
        lblKPI.Caption = "KPI Fields:"
        lblAggregation.Caption = "Multi-KPI List:"

        ' Show multi-KPI controls
        lstKPI_Multi.Visible = True
        cboAggregation_Multi.Visible = True
        btnAddKPI.Visible = True
        btnRemoveKPI.Visible = True
        lstMultiKPIDisplay.Visible = True
    Else
        ' SINGLE KPI MODE
        cboKPI.Visible = True
        cboAggregation.Visible = True
        lblKPI.Caption = "KPI Field:"
        lblAggregation.Caption = "Aggregation:"

        ' Hide multi-KPI controls
        lstKPI_Multi.Visible = False
        cboAggregation_Multi.Visible = False
        btnAddKPI.Visible = False
        btnRemoveKPI.Visible = False
        lstMultiKPIDisplay.Visible = False
    End If
End Sub

Private Sub btnAddKPI_Click()
    ' Add selected KPI with aggregation to the multi-KPI list

    If lstKPI_Multi.ListIndex = -1 Then
        MsgBox "Please select a KPI field", vbExclamation
        Exit Sub
    End If

    If cboAggregation_Multi.Value = "" Then
        MsgBox "Please select an aggregation type", vbExclamation
        Exit Sub
    End If

    Dim kpiField As String
    Dim aggType As String

    kpiField = lstKPI_Multi.Value
    aggType = cboAggregation_Multi.Value

    ' Check if already added
    Dim i As Integer
    For i = 0 To lstMultiKPIDisplay.ListCount - 1
        If InStr(lstMultiKPIDisplay.List(i), kpiField & " (") > 0 Then
            MsgBox "KPI '" & kpiField & "' already added!", vbExclamation
            Exit Sub
        End If
    Next i

    ' Add to collections
    MultiKPIList.Add kpiField
    MultiAggList.Add aggType

    ' Display in list
    lstMultiKPIDisplay.AddItem kpiField & " (" & aggType & ")"
End Sub

Private Sub btnRemoveKPI_Click()
    ' Remove selected KPI from multi-KPI list

    If lstMultiKPIDisplay.ListIndex = -1 Then
        MsgBox "Please select a KPI to remove", vbExclamation
        Exit Sub
    End If

    Dim selectedIndex As Integer
    selectedIndex = lstMultiKPIDisplay.ListIndex

    ' Remove from collections (collections are 1-based)
    MultiKPIList.Remove selectedIndex + 1
    MultiAggList.Remove selectedIndex + 1

    ' Remove from display list
    lstMultiKPIDisplay.RemoveItem selectedIndex
End Sub



