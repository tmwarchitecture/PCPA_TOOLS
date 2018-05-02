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
        self.Size = drawing.Size(500,545)
        self.Padding = drawing.Padding(5, 5)
        self.Spacing = drawing.Size(2,2)
        
        self.databasePath = r'C:\Users\twilliams\Desktop\TEMP\Database'
        self.versionName = r'Project_Info.yaml'
        
        try:
            self.databaseFile = rs.GetDocumentData('PCPA', 'Project_Database')
        except:
            self.databaseFile = ''
    
    def CreateControls(self):
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
            mnuNew.Click += self.OnFileSaveClick
            mnuSave = forms.ButtonMenuItem(Text = "Save")
            mnuSave.Click += self.OnFileSaveClick
            mnuSaveAs = forms.ButtonMenuItem(Text = "Save As...")
            mnuSaveAs.Click += self.OnFileSaveAsClick
            mnuOpen = forms.ButtonMenuItem(Text = "Open")
            mnuOpen.Click += self.OnFileOpenClick
            mnuClose = forms.ButtonMenuItem(Text = "Close")
            mnuClose.Click += self.OnFileCloseClick
            
            
            mnuFile.Items.Add(mnuOpen)
            mnuFile.Items.Add(mnuSave)
            mnuFile.Items.Add(mnuSaveAs)
            mnuFile.Items.Add(mnuClose)
            mnuBar = forms.MenuBar(mnuFile)
            #mnuBar.Spacing = drawing.Size(2,2)
            
            self.Menu = mnuBar
        def dropdown():
            #Dropdown
            data = dt.GetProjectDatabase(self.databaseFile)
            bldgNames = []
            try:
                bldgData = data['building']
                for i, key in enumerate(bldgData.keys()):
                    bldgNames.append(str(i) + " - " + bldgData[key]['name'])
            except:
                bldgNames = [''] 
            
            self.drpdwnBuildingNum = forms.DropDown()
            self.drpdwnBuildingNum.DataStore = bldgNames
            self.drpdwnBuildingNum.SelectedIndex = 0
            self.drpdwnBuildingNum.SelectedIndexChanged += self.OnBldgNumChanged
        def buttons():
            #BUTTONS
            self.btnApply = forms.Button()
            self.btnApply.Text = "Save"
            self.btnApply.Click += self.OnFileSaveClick
            
            self.btnCancel = forms.Button()
            self.btnCancel.Text = "Close"
            self.btnCancel.Click += self.OnCancelPressed
        def grid():
            self.grid = forms.GridView()
            self.grid.BackgroundColor = drawing.Colors.LightGrey
            self.grid.Size = drawing.Size(300,425)
            self.grid.GridLines = forms.GridLines.Both
            
            #COLUMNS
            numberColumn = forms.GridColumn()
            numberColumn.HeaderText = "#\t"
            numberColumn.DataCell = forms.TextBoxCell(0)
            
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
            
            self.grid.Columns.Add(numberColumn)
            self.grid.Columns.Add(nameColumn)
            self.grid.Columns.Add(funcColumn)
            self.grid.Columns.Add(ftfColumn)
            self.grid.Columns.Add(levelColumn)
        
        dropdown()
        buttons()
        grid()
        menuBar()
        contextMenu()
        self.GenData()
    
    def CreateLayouts(self):
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(self.drpdwnBuildingNum)
        layoutButtons.AddRow(self.grid)
        layoutButtons.AddSeparateRow(None, self.btnCancel, self.btnApply)
        
        layout = forms.DynamicLayout()
        #layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)
        
        #5 - add the layout to the dialog
        self.Content = layout
    
    def OnCancelPressed(self, sender, e):
        self.Close()
    
    #Open File
    def OnFileOpenClick(self, sender, e):
        self.databaseFile = rs.OpenFileName("Open file")
        if self.databaseFile is None: return
        self.OpenFile()
        rs.SetDocumentData('PCPA', 'Project_Database', self.databaseFile)
    
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
        
        self.drpdwnBuildingNum.DataStore = bldgNames
        self.drpdwnBuildingNum.SelectedIndex = 0
        
        self.GenData()
        
        print "Openig new file"
    
    #Save
    def OnFileSaveAsClick(self, sender, e):
        newFile = rs.SaveFileName("Save", "YAML Files (*.yaml)|*.yaml||")
        dt.SaveProjectLevelData(self.grid.DataStore, self.databaseFile, newFile, self.drpdwnBuildingNum.SelectedIndex)
        self.databaseFile = newFile
        rs.SetDocumentData('PCPA', 'Project_Database', self.databaseFile)
    
    def OnFileSaveClick(self, sender, e):
        dt.SaveProjectLevelData(self.grid.DataStore, self.databaseFile, self.databaseFile, self.drpdwnBuildingNum.SelectedIndex)
    
    #Close
    def OnFileCloseClick(self, sender, e):
        self.grid.DataStore = []
        self.drpdwnBuildingNum.DataStore = []
        self.databaseFile = None
    
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
        try:
            newRowFunc = data[self.grid.SelectedRow][2]
            newRowFTF = float(data[self.grid.SelectedRow][3])
            newRowHeight = newRowFTF + float(data[self.grid.SelectedRow][4])
        except:
            newRowFTF = ''
            newRowHeight = ''
            newRowFunc = ''
        blankRow = ['', '', newRowFunc, newRowFTF, newRowHeight]
        data.insert(self.grid.SelectedRow, blankRow)
        self.grid.DataStore = data
        self.RenumberRows()
    
    def OnDeleteRow(self, sender, e):
        data = self.grid.DataStore
        
        del data[self.grid.SelectedRow]
        
        self.grid.DataStore = data
        
        self.RenumberRows()
        
        print self.grid.DataStore
        #print "Deleteing row {}".format(self.grid.SelectedItem[0])
    
    #Util functions
    def RenumberRows(self):
        data = self.grid.DataStore
        data.reverse()
        for i, row in enumerate(data):
            row[0] = i
        data.reverse()
        self.grid.DataStore = data
        print "Renumbered"
    
    def GenData(self):
        bldgNum = self.drpdwnBuildingNum.SelectedIndex
        try:
            self.grid.DataStore = dt.GetProjectLevelData(self.databaseFile, bldgNum)[::-1]
        except:
            self.grid.DataStore = []

def main():
    dialog = LevelsDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

if __name__ == "__main__":
    main()
