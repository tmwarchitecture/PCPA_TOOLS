import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import rhinoscriptsyntax as rs
import os
import database_tools as dt


class LevelsDialog(forms.Dialog):
    def __init__(self):
        self.Initialize()
        self.CreateControls()
        self.CreateLayouts()
    
    def Initialize(self):
        #Setup the dialog
        self.Title = "Project Levels"
        self.Size = drawing.Size(450,565)
        self.Padding = drawing.Padding(5, 5)
        
        self.databasePath = r'C:\Users\twilliams\Desktop\TEMP\Database'
        self.versionName = r'Project_Info.yaml'
        
        try:
            self.databaseFile = rs.GetDocumentData('PCPA', 'Project_Database')
        except:
            self.databaseFile = ''
    
    def CreateControls(self):
        def labels():
            self.tboxFileName = forms.TextBox()
            self.tboxFileName.ReadOnly = True
        def contextMenu():
            ctxtMnu = forms.ContextMenu()
            ctxtInsertRow = forms.ButtonMenuItem(Text = "Insert New Floor Above")
            ctxtInsertRow.Click += self.OnInsertRowAbove
            
            ctxtDeleteRow = forms.ButtonMenuItem(Text = "Remove Floor")
            ctxtDeleteRow.Click += self.OnDeleteRow
            
            ctxtMnu.Items.Add(ctxtInsertRow)
            ctxtMnu.Items.Add(ctxtDeleteRow)
            
            self.grid.ContextMenu = ctxtMnu
        def menuBar():
            mnuFile = forms.ButtonMenuItem(Text = "File")
            mnuNew = forms.ButtonMenuItem(Text = "New")
            mnuNew.Click += self.OnNewFileClick
            mnuSave = forms.ButtonMenuItem(Text = "Save")
            mnuSave.Click += self.OnFileSaveClick
            mnuSaveAs = forms.ButtonMenuItem(Text = "Save As...")
            mnuSaveAs.Click += self.OnFileSaveAsClick
            mnuOpen = forms.ButtonMenuItem(Text = "Open")
            mnuOpen.Click += self.OnFileOpenClick
            mnuClose = forms.ButtonMenuItem(Text = "Close")
            mnuClose.Click += self.OnFileCloseClick
            
            mnuEdit = forms.ButtonMenuItem(Text = "Edit")
            mnuCopy = forms.ButtonMenuItem(Text = "Copy")
            mnuCopy.Click += self.copyToClipboard
            mnuEdit.Items.Add(mnuCopy)
            
            mnuFile.Items.Add(mnuNew)
            mnuFile.Items.Add(mnuOpen)
            mnuFile.Items.Add(mnuSave)
            mnuFile.Items.Add(mnuSaveAs)
            mnuFile.Items.Add(mnuClose)
            mnuBar = forms.MenuBar(mnuFile, mnuEdit)
            #self.Menu.Spacing = drawing.Size(2,2)
            #mnuBar.Padding = 5
            
            self.Menu = mnuBar
        def combobox():
            #Combobox
            data = dt.GetProjectDatabase(self.databaseFile)
            bldgNames = []
            try:
                bldgData = data['building']
                for i, key in enumerate(bldgData.keys()):
                    bldgNames.append(str(i) + " - " + bldgData[key]['name'])
            except:
                bldgNames = [''] 
            
            self.comboBuildingNum = forms.ComboBox()
            self.comboBuildingNum.DataStore = bldgNames
            self.comboBuildingNum.SelectedIndex = 0
            self.comboBuildingNum.SelectedIndexChanged += self.OnBldgNumChanged
        def buttons():
            #BUTTONS
            self.btnApply = forms.Button()
            self.btnApply.Text = "OK"
            self.btnApply.Click += self.OnFileSaveClick
            
            self.btnCancel = forms.Button()
            self.btnCancel.Text = "Cancel"
            self.btnCancel.Click += self.OnCancelPressed
        def grid():
            self.grid = forms.GridView()
            self.grid.BackgroundColor = drawing.Colors.LightGrey
            self.grid.Size = drawing.Size(300,425)
            self.grid.GridLines = forms.GridLines.Both
            self.grid.AllowMultipleSelection = True
            self.grid.CellEdited += self.OnCellEdited
            self.grid.CellFormatting += self.OnCellFormatting
            
            #COLUMNS
            numberColumn = forms.GridColumn()
            numberColumn.HeaderText = "#"
            numberColumn.DataCell = forms.TextBoxCell(0)
            numberColumn.DataCell.TextAlignment = forms.TextAlignment.Right
            
            nameColumn = forms.GridColumn()
            nameColumn.HeaderText = "Floor\t"
            nameColumn.Editable = True
            nameColumn.DataCell = forms.TextBoxCell(1)
            
            funcColumn = forms.GridColumn()
            funcColumn.HeaderText = "Program\t\t"
            funcColumn.DataCell = forms.TextBoxCell(2)
            funcColumn.Editable = True
            funcColumn.DataCell.TextAlignment = forms.TextAlignment.Center
            
            ftfColumn = forms.GridColumn()
            ftfColumn.HeaderText = "FTF\t"
            ftfColumn.DataCell = forms.TextBoxCell(3)
            ftfColumn.Editable = True
            ftfColumn.DataCell.TextAlignment = forms.TextAlignment.Right
            
            levelColumn = forms.GridColumn()
            levelColumn.HeaderText = "Height\t"
            levelColumn.Editable = True
            levelColumn.DataCell = forms.TextBoxCell(4)
            levelColumn.DataCell.TextAlignment = forms.TextAlignment.Right
            
            areaColumn = forms.GridColumn()
            areaColumn.HeaderText = "Area\t"
            areaColumn.Editable = True
            areaColumn.DataCell = forms.TextBoxCell(5)
            areaColumn.DataCell.TextAlignment = forms.TextAlignment.Right
            
            self.grid.Columns.Add(numberColumn)
            self.grid.Columns.Add(nameColumn)
            self.grid.Columns.Add(funcColumn)
            self.grid.Columns.Add(ftfColumn)
            self.grid.Columns.Add(levelColumn)
            self.grid.Columns.Add(areaColumn)
        
        labels()
        combobox()
        buttons()
        grid()
        menuBar()
        contextMenu()
        self.GenData()
        self.UpdateFileLabel(self.databaseFile)
    
    def CreateLayouts(self):
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(self.tboxFileName)
        layoutButtons.AddRow(self.comboBuildingNum)
        layoutButtons.AddRow(self.grid)
        layoutButtons.AddSeparateRow(None, self.btnCancel, self.btnApply)
        layoutButtons.Spacing = drawing.Size(1,1)
        layout = forms.DynamicLayout()
        #layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)
        
        #5 - add the layout to the dialog
        self.Content = layout
    
    def OnCancelPressed(self, sender, e):
        self.Close()
    
    #New File
    def OnNewFileClick(self, sender, e):
        self.grid.DataStore = []
        print "New File"
    
    #Open File
    def OnFileOpenClick(self, sender, e):
        self.databaseFile = rs.OpenFileName("Open file")
        if self.databaseFile is None: return
        self.OpenFile()
        rs.SetDocumentData('PCPA', 'Project_Database', self.databaseFile)
        dt.LoadLevelsToRhinoDoc(self.databaseFile)
        self.UpdateFileLabel(self.databaseFile)
    
    def OpenFile(self):
        data = dt.GetProjectDatabase(self.databaseFile)
        
        #Fix dropdown
        bldgNames = []
        try:
            bldgData = data['building']
            for key in bldgData.keys():
                bldgNames.append(bldgData[key]['name'])
        except:
            bldgNames = [''] 
        
        self.comboBuildingNum.DataStore = bldgNames
        self.comboBuildingNum.SelectedIndex = 0
        
        self.GenData()
        
        
        print "Opening new file"
    
    #Save
    def OnFileSaveAsClick(self, sender, e):
        newFile = rs.SaveFileName("Save", "YAML Files (*.yaml)|*.yaml||")
        dt.SaveProjectLevelData(self.grid.DataStore, self.databaseFile, newFile, self.comboBuildingNum.SelectedIndex)
        self.databaseFile = newFile
        rs.SetDocumentData('PCPA', 'Project_Database', self.databaseFile)
        self.UpdateFileLabel(newFile)
    
    def OnFileSaveClick(self, sender, e):
        dt.SaveProjectLevelData(self.grid.DataStore, self.databaseFile, self.databaseFile, self.comboBuildingNum.SelectedIndex)
        data = self.grid.DataStore
        data.reverse()
        rs.SetDocumentData('PCPA', 'Levels', str(data))
        self.Close()
    
    #Close
    def OnFileCloseClick(self, sender, e):
        self.grid.DataStore = []
        self.comboBuildingNum.DataStore = []
        self.databaseFile = None
        self.UpdateFileLabel()
        rs.SetDocumentData('PCPA', 'Project_Database', "")
    
    #Building Num
    def OnBldgNumChanged(self, sender, e):
        try:
            self.GenData()
        except:
            print "Error reading the database"
    
    #Grid editing
    def OnInsertRowAbove(self, sender, e):
        print "Inserting above"
        data = self.grid.DataStore
        selectedRow = self.grid.SelectedRow
        if len(data) == 0:
            self.grid.DataStore = [[1,'L1','',10.0,0.0, '']]
            return
        
        try:
            newRowNameRaw = int(data[selectedRow][1][1:]) + 1
            newRowName = "L" + str(newRowNameRaw)
        except:
            newRowName = data[selectedRow][1]
        
        try:
            newRowFunc = data[selectedRow][2]
            newRowFTF = float(data[selectedRow][3])
            newRowHeight = newRowFTF + float(data[selectedRow][4])
            newRowArea = ''
        except:
            newRowFTF = ''
            newRowHeight = ''
            newRowFunc = ''
            newRowArea = ''
        blankRow = ['', newRowName, newRowFunc, newRowFTF, newRowHeight, newRowArea]
        data.insert(selectedRow, blankRow)
        self.grid.DataStore = data
        self.RenumberRows()
        self.UpdateHeights()
    
    def OnDeleteRow(self, sender, e):
        data = self.grid.DataStore
        
        for row in self.grid.SelectedRows:
            del data[row]
        
        self.grid.DataStore = data
        self.RenumberRows()
        self.UpdateHeights()
    
    def OnCellEdited(self, sender, e):
        if e.Column == 4 or e.Column == 3:
            # "Height Adjusted"
            self.CheckIfNumber(e.Row, e.Column)
            self.UpdateHeights()
    
    def OnCellFormatting(self, sender, e):
        if e.Column.HeaderText == '#':
            e.ForegroundColor = drawing.Colors.DarkGray
    
    #Util functions
    def RenumberRows(self):
        data = self.grid.DataStore
        data.reverse()
        for i, row in enumerate(data):
            row[0] = i+1
        data.reverse()
        self.grid.DataStore = data
        #print "Renumbered"
    
    def GenData(self):
        bldgNum = self.comboBuildingNum.SelectedIndex
        try:
            data = dt.GetLevelsFromRhinoDoc()
            data.reverse()
            self.grid.DataStore = data
            #self.grid.DataStore = dt.GetProjectLevelData(self.databaseFile, bldgNum)[::-1]
        except:
            self.grid.DataStore = []
    
    def UpdateFileLabel(self, name = "--No File Selected--"):
        self.tboxFileName.Text = name
    
    def CheckIfNumber(self, row, col):
        try:
            float(self.grid.DataStore[row][col])
        except:
            print "Cell accepts numbers only"
            self.grid.DataStore[row][col] = 0
    
    def UpdateHeights(self):
        data = list(self.grid.DataStore)
        data.reverse()
        #
        numRows = len(data)
        for i in range(1,numRows):
            data[i][4] = float(data[i-1][3]) + float(data[i-1][4])
            data[i-1][3] =  float(data[i][4])-float(data[i-1][4])
        #
        data.reverse()
        self.grid.DataStore = data
    
    def InchesToFeet(self):
        print "A"
    
    #I/O Functions
    def copyToClipboard(self, sender, e):
        try:
            string = self.DataStoreToHTML()
            rs.ClipboardText(string)
            print "Copied to clipboard"
        except:
            print "copyToClipboard() Failed"

    def copySelectionToClipboard(self, sender, e):
        try:
            items = list(self.grid.SelectedItems)
            string = self.DataStoreToHTML(items)
            rs.ClipboardText(string)
            print "Copied Selection to clipboard"
        except:
            print "copySelectionToClipboard() Failed"

    def exportData(self, sender, e):
        fileName = rs.SaveFileName("Save table", filter = "CSV Files (*.csv)|*.csv|HTML Files (*.html)|*.html|TXT Files (*.txt)|*.txt||")
        if fileName is None:
            return
        extension = fileName.split(".")[-1]
        try:
            f = open(fileName,'w')
        except IOError:
            print "Cannot save file. File already open."
            return
        try:
            if extension == "html":
                string = self.DataStoreToHTML()
            if extension == "csv":
                global commaSep
                
                prevCommaSep = commaSep
                prevColorFormat = self.colorFormat
                
                if self.colorFormat == 2:
                    self.colorFormat = 1
                
                if commaSep:
                    commaSep = False
                
                self.Regen()
                
                string = self.DataStoreToCSV()
                
                self.colorFormat = prevColorFormat
                commaSep = prevCommaSep
                
                self.Regen()
            if extension == "txt":
                string = self.DataStoreToTXT()
            f.write(string)
            f.close()
            print "Exported to {}".format(extension)
        except:
            print "exportData() Failed"

    def DataStoreToTXT(self):
        string = ""
        seperator = "\t"
        if self.showHeaders.Checked:
            allHeadings = self.activeHeadingsList()
            print "Headings received"
            for heading in allHeadings:
                itemLen = len(str(heading))
                if itemLen >= 8:
                    numTabs = 1
                else:
                    numTabs = 2
                string += str(heading) + (seperator * numTabs)
            string += "\n"

        allData = self.activeDataList()

        for row in allData:
            for item in row:
                if str(item) == "None":
                    string += (seperator * numTabs)
                else:
                    itemLen = len(str(item))
                    if itemLen >= 8:
                        numTabs = 1
                    else:
                        numTabs = 2
                    string += str(item) + (seperator * numTabs)
            string += "\n"
        return string

    def DataStoreToCSV(self):
        string = ""
        if self.showHeaders.Checked:
            allHeadings = self.activeHeadingsList()
            print "Headings received"
            for heading in allHeadings:
                string += str(heading) + ","
            string += "\n"

        allData = self.activeDataList()

        for row in allData:
            for item in row:
                if str(item) == "None":
                    string += ","
                else:
                    string += str(item) + ","
            string += "\n"
        return string

    def DataStoreToHTML(self, *args):
        try:
            string = "<html><head><style>"
            string += "body {color: dimgray;}"
            string += "table, th, td{border-collapse: collapse; border: 1px solid black;padding: 10px;}"
            string += "</style></head><body><table>"
            
            allHeadings = []
            for i in range(self.grid.Columns.Count):
                allHeadings.append(self.grid.Columns.Item[i].HeaderText)
            string += "<tr>"
            for heading in allHeadings:
                string += "<th>" + str(heading) + "</th>"
            string += "</tr>"
            
            #If *args specified, format them
            if len(args) > 0:
                tempItems = []
                for bracket in args:
                    for item in bracket:
                        if item is not None:
                            tempItems.append(item)
                finalItems = []
                for item in tempItems:
                    newItem = []
                    for i, attr in enumerate(item):
                        #if self.checkboxes[i].Checked:
                        newItem.append(attr)
                    finalItems.append(newItem)
                allData = finalItems
            else:
                allData = self.grid.DataStore
            
            for row in allData:
                string += "<tr>"
                for item in row:
                    if item is None:
                        item = ""
                    string += "<td>" + str(item) + "</td>"
                string += "</tr>"
            string += "</table>"
            return string
        except:
            print "HTML Failed"

def main():
    dialog = LevelsDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

if __name__ == "__main__":
    main()