import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import os


class LevelsDialog(forms.Dialog):
    def __init__(self):
        #1 - Setup the dialog
        self.Title = "Project Levels"
        self.Size = drawing.Size(600,260)
        self.Padding = drawing.Padding(5, 5)
        
        data = self.GenData()
        
        
        grid = forms.GridView()
        grid.DataStore = data
        grid.BackgroundColor = drawing.Colors.LightGrey
        
        nameColumn = forms.GridColumn()
        nameColumn.HeaderText = "Name\t"
        nameColumn.DataCell = forms.TextBoxCell(0)
        
        levelColumn = forms.GridColumn()
        levelColumn.HeaderText = "Level\t"
        levelColumn.DataCell = forms.TextBoxCell(1)
        
        ftfColumn = forms.GridColumn()
        ftfColumn.HeaderText = "FTF\t"
        ftfColumn.DataCell = forms.TextBoxCell(2)
        ftfColumn.Editable = True
        
        grid.Columns.Add(nameColumn)
        grid.Columns.Add(levelColumn)
        grid.Columns.Add(ftfColumn)
        
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(grid, None)
        #layoutButtons.AddRow(None, btnCancel, btnApply)
        
        layout = forms.DynamicLayout()
        #layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)
        
        #5 - add the layout to the dialog
        self.Content = layout

    def OnBtnPressedApply(self, sender, e):
        self.Close()

    def OnCancelPressed(self, sender, e):
        self.Close()
    
    def GenData(self):
        

dialog = LevelsDialog()
dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)