import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import os

class LevelsDialog(forms.Dialog):
    def __init__(self):
        #1 - Setup the dialog
        self.Title = "Project Levels"
        self.Size = drawing.Size(500,500)
        self.Padding = drawing.Padding(5, 5)
        
        data = self.GenData()
        
        grid = forms.GridView()
        grid.DataStore = data
        grid.BackgroundColor = drawing.Colors.LightGrey
        grid.Size = drawing.Size(300,425)
        
        nameColumn = forms.GridColumn()
        nameColumn.HeaderText = "Name\t"
        nameColumn.DataCell = forms.TextBoxCell(0)
        
        funcColumn = forms.GridColumn()
        funcColumn.HeaderText = "Function\t\t"
        funcColumn.DataCell = forms.TextBoxCell(1)
        funcColumn.Editable = True
        funcColumn.DataCell.TextAlignment = forms.TextAlignment.Right
        
        ftfColumn = forms.GridColumn()
        ftfColumn.HeaderText = "FTF\t"
        ftfColumn.DataCell = forms.TextBoxCell(3)
        ftfColumn.Editable = True
        ftfColumn.DataCell.TextAlignment = forms.TextAlignment.Right
        
        levelColumn = forms.GridColumn()
        levelColumn.HeaderText = "Level\t"
        levelColumn.DataCell = forms.TextBoxCell(2)
        levelColumn.DataCell.TextAlignment = forms.TextAlignment.Right
        #levelColumn.TextAlignment = forms
        
        
        btnApply = forms.Button()
        btnApply.Text = "Apply"
        btnApply.Click += self.OnBtnPressedApply
        
        btnCancel = forms.Button()
        btnCancel.Text = "Cancel"
        btnCancel.Click += self.OnCancelPressed
        
        
        grid.Columns.Add(nameColumn)
        grid.Columns.Add(funcColumn)
        grid.Columns.Add(ftfColumn)
        grid.Columns.Add(levelColumn)
        
        
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(grid)
        layoutButtons.AddSeparateRow(None, btnCancel, btnApply)
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
       return [['', '', '', ''],['TOB', '', '+30.00', ''],['L3', '', '+20.00', '10.00'], ['L2','', '+10.00', '10.00'], ['L1','', '+0.00', '10.00']]

def main():
    dialog = LevelsDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

if __name__ == "__main__":
    main()
