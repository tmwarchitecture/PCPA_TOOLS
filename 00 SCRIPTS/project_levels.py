import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import rhinoscriptsyntax as rs
import os
import database_tools as dt

__author__ = 'Tim Williams'
__version__ = "2.1.0"

def ConvertImperialLength(numberString, ToInches = True):
    """
    ConvertLength(numberString, ToInches = True)
    -Acceptable formats:
        4.5'
        36.1"
        4'6"
    """
    try:
        return float(numberString)
    except:
        if ToInches:
            footScale = 12
            inchScale = 1
        else:
            footScale = 1
            inchScale = 1/12
        if '"' in numberString and "'" in numberString:
            if numberString.find("'") < numberString.find('"'):
                try:
                    values = numberString.split("'")
                    feetInches = float(values[0])*footScale
                    inches = float(values[-1].split('"')[0])*inchScale
                    return feetInches + inches
                except:
                    pass
        elif "'" in numberString:
            try:
                return float(numberString.split("'")[0])*footScale
            except:
                pass
        elif '"' in numberString:
            try:
                return float(numberString.split('"')[0])*inchScale
            except:
                pass
        return None

class GetNumberOfFloors(forms.Dialog):
    def __init__(self):
        self.Title = "Insert Many Floors"
        #self.Size = drawing.Size(100,100)
        self.Padding = drawing.Padding(5)

        self.ApplyBoo = False
        self.NumFloors = 3

        self.numericButton = forms.NumericUpDown()
        self.numericButton.DecimalPlaces = 0
        self.numericButton.MinValue = 2.0
        self.numericButton.Value = self.NumFloors

        self.DefaultButton = forms.Button(Text = 'OK')
        self.DefaultButton.Click += self.OnOKButtonClick

        self.AbortButton = forms.Button(Text = 'Cancel')
        self.AbortButton.Click += self.OnCancelButtonClick

        layout = forms.DynamicLayout()
        layout.AddRow(self.numericButton, None)
        layout.AddSeparateRow(None, self.DefaultButton, self.AbortButton)
        self.Content = layout

    def OnOKButtonClick(self, sender, e):
        self.NumFloors = self.numericButton.Value
        #print self.NumFloors
        self.ApplyBoo = True
        self.Close()

    def OnCancelButtonClick(self, sender, e):
        self.Close()

class LevelsDialog(forms.Dialog):
    def __init__(self):
        self.Initialize()
        self.CreateControls()
        self.CreateLayouts()

    def Initialize(self):
        #Setup the dialog
        self.Title = "Project Levels"
        self.Size = drawing.Size(550,565)
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

            ctxtInsertManyRows = forms.ButtonMenuItem(Text = "Insert Many Floors")
            ctxtInsertManyRows.Click += self.OnInsertManyRowsAbove

            ctxtInsertRow = forms.ButtonMenuItem(Text = "Insert Floor")
            ctxtInsertRow.Click += self.OnInsertRowAbove

            ctxtDeleteRow = forms.ButtonMenuItem(Text = "Remove Floor")
            ctxtDeleteRow.Click += self.OnDeleteRow

            self.seperator1 = forms.SeparatorMenuItem()

            ctxtMnu.Items.Add(ctxtInsertManyRows)
            ctxtMnu.Items.Add(ctxtInsertRow)
            ctxtMnu.Items.Add(self.seperator1)
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
            mnuOpen = forms.ButtonMenuItem(Text = "Import from 3dm")
            #mnuOpen.Enabled = False
            mnuOpen.Click += self.OnFileOpenClick
            mnuClose = forms.ButtonMenuItem(Text = "Close")
            mnuClose.Click += self.OnFileCloseClick

            mnuEdit = forms.ButtonMenuItem(Text = "Edit")
            mnuCopy = forms.ButtonMenuItem(Text = "Copy")
            mnuCopy.Click += self.copyToClipboard
            mnuEdit.Items.Add(mnuCopy)

            mnuFile.Items.Add(mnuNew)
            mnuFile.Items.Add(mnuOpen)
            #mnuFile.Items.Add(mnuSave)
            #mnuFile.Items.Add(mnuSaveAs)
            #mnuFile.Items.Add(mnuClose)
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
                bldgNames = ['Sheet 1','--Create New--']

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

            self.DefaultButton = self.btnApply
            self.AbortButton = self.btnCancel
        def grid():
            self.grid = forms.GridView()
            self.grid.BackgroundColor = drawing.Colors.LightGrey
            self.grid.Size = drawing.Size(300,470)
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
            areaColumn.HeaderText = "GFA\t"
            areaColumn.Editable = True
            areaColumn.DataCell = forms.TextBoxCell(5)
            areaColumn.DataCell.TextAlignment = forms.TextAlignment.Right

            commentColumn = forms.GridColumn()
            commentColumn.HeaderText = "Comments\t\t"
            commentColumn.Editable = True
            commentColumn.DataCell = forms.TextBoxCell(6)
            commentColumn.DataCell.TextAlignment = forms.TextAlignment.Left

            self.grid.Columns.Add(numberColumn)
            self.grid.Columns.Add(nameColumn)
            self.grid.Columns.Add(funcColumn)
            self.grid.Columns.Add(ftfColumn)
            self.grid.Columns.Add(levelColumn)
            self.grid.Columns.Add(areaColumn)
            self.grid.Columns.Add(commentColumn)

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
        #layoutButtons.AddRow(self.tboxFileName)
        #layoutButtons.AddRow(self.comboBuildingNum)
        layoutButtons.AddRow(self.grid)
        layoutButtons.AddSeparateRow(None, self.btnCancel, self.btnApply)
        layoutButtons.Spacing = drawing.Size(1,1)
        layout = forms.DynamicLayout()
        #layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)

        #5 - add the layout to the dialog
        self.Content = layout

    #Cancel
    def OnCancelPressed(self, sender, e):
        self.Close()

    #New File
    def OnNewFileClick(self, sender, e):
        self.grid.DataStore = []
        print "New File"

    #Open File
    def OnFileOpenClick(self, sender, e):
        print "Begin"
        self.databaseFile = rs.OpenFileName("Open file", "Rhino 3DM Models (*.3dm)|*.3dm||")
        if self.databaseFile is None: return

        data = dt.GetLevelsFromAnotherRhinoDoc(self.databaseFile)
        if data is None: return

        self.grid.DataStore = data[::-1]

        self.RegenData()

        print "End"

    #Save
    def OnFileSaveAsClick(self, sender, e):
        newFile = rs.SaveFileName("Save", "YAML Files (*.yaml)|*.yaml||")
        dt.SaveProjectLevelData(self.grid.DataStore, self.databaseFile, newFile, 0)
        self.databaseFile = newFile
        rs.SetDocumentData('PCPA', 'Project_Database', self.databaseFile)
        self.UpdateFileLabel(newFile)

    def OnFileSaveClick(self, sender, e):
        data = self.grid.DataStore
        reversed(data)
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
            if self.comboBuildingNum.SelectedIndex == 1:
                print "Creating new!"
                print self.comboBuildingNum.DataStore

                data = self.comboBuildingNum.DataStore
                data.append('New Layout')
                self.comboBuildingNum.DataStore = data
                print data
                self.comboBuildingNum.UpdateBindings()
                self.comboBuildingNum.SelectedIndex = 0
        except:
            print "Error reading the database"

    #Grid editing
    def OnInsertManyRowsAbove(self, sender, e):
        numFloorsDialog = GetNumberOfFloors()
        numberOfFloors = numFloorsDialog.NumFloors
        applyBoo = numFloorsDialog.ApplyBoo
        numFloorsDialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
        numberOfFloors = int(numFloorsDialog.NumFloors)

        for i in range(numberOfFloors):
            self.OnInsertRowAbove(sender, e)
        #print "Inserting many rows"

    def OnInsertRowAbove(self, sender, e):
        data = self.grid.DataStore
        selectedRow = self.grid.SelectedRow
        if len(data) == 0:
            self.grid.DataStore = [[1,'L1','',10.0,0.0, '', '']]
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
            newRowComment = ''
        except:
            newRowFTF = ''
            newRowHeight = ''
            newRowFunc = ''
            newRowArea = ''
            newRowComment = ''
        blankRow = ['', newRowName, newRowFunc, newRowFTF, newRowHeight, newRowArea, newRowComment]
        data.insert(selectedRow, blankRow)

        self.grid.DataStore = data

        self.grid.SelectedRow = selectedRow
        self.RegenData()

    def OnDeleteRow(self, sender, e):
        data = self.grid.DataStore

        for row in self.grid.SelectedRows:
            del data[row]

        self.grid.DataStore = data
        self.RegenData()

    def OnCellEdited(self, sender, e):
        if e.Column == 4 or e.Column == 3:
            self.grid.DataStore[e.Row][e.Column] = ConvertImperialLength(self.grid.DataStore[e.Row][e.Column], False)
            self.CheckIfNumber(e.Row, e.Column)

            self.RegenData()

    def OnCellFormatting(self, sender, e):
        if e.Column.HeaderText == '#':
            e.ForegroundColor = drawing.Colors.DarkGray

    #Util functions
    def RenumberRows(self):
        data = list(self.grid.DataStore[::-1])
        for i, row in enumerate(data):
            row[0] = i+1
        self.grid.DataStore = list(data[::-1])

    def GenData(self):
        try:
            data = dt.GetLevelsFromRhinoDoc()
            self.grid.DataStore = data
        except:
            self.grid.DataStore = []

    def RegenData(self):
        self.RenumberRows()
        self.UpdateHeights()
        #self.ShowTotalsRow()

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

    def ShowTotalsRow(self):
        try:
            data = self.grid.DataStore

            print data
            emptyRow =  len(data[0]) * [' ']
            data.insert(-1, emptyRow)
            print data
            self.grid.DataStore = data
        except:
            print "ShowTotalsRow Failed"
            return

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
            #string += "table, th, td{border-collapse: collapse; border: 1px solid black;padding: 10px;}"
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
