import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import os


class SettingsDialog(forms.Dialog):
    def __init__(self):
        #1 - Setup the dialog
        self.Title = "Project Information"
        self.Size = drawing.Size(600,230)
        self.Padding = drawing.Padding(5, 5)
        
        self.GeoData()
        
        self.fileName1 = "Project Name"
        self.fileName2 = "Client Name"
        lightgrey = drawing.Colors.LightGrey
        darkgrey = drawing.Colors.DarkGray
        
        buttons = []
        txtBoxes = []
        
        #2 - make each controls
        lblProjName = forms.Label()
        lblProjName.Text = "Project Name"
        lblProjName.VerticalAlignment = forms.VerticalAlignment.Center
        lblProjName.TextAlignment = forms.TextAlignment.Right
        
        lblProjNum = forms.Label()
        lblProjNum.Text = "Project Number"
        lblProjNum.VerticalAlignment = forms.VerticalAlignment.Center
        lblProjNum.TextAlignment = forms.TextAlignment.Right
        
        lblClientName = forms.Label()
        lblClientName.Text = "Client Name"
        lblClientName.VerticalAlignment = forms.VerticalAlignment.Center
        lblClientName.TextAlignment = forms.TextAlignment.Right
        
        lblProjCity = forms.Label()
        lblProjCity.Text = "Project City"
        lblProjCity.VerticalAlignment = forms.VerticalAlignment.Center
        lblProjCity.TextAlignment = forms.TextAlignment.Right
        
        lblProjState = forms.Label()
        lblProjState.Text = "Project State"
        lblProjState.VerticalAlignment = forms.VerticalAlignment.Center
        lblProjState.TextAlignment = forms.TextAlignment.Right
        
        self.tBoxProjName = forms.TextBox()
        self.tBoxProjName.Text = self.fileName1
        txtBoxes.append(self.tBoxProjName)
        
        self.tBoxClientName = forms.TextBox()
        self.tBoxClientName.Text = self.fileName2
        txtBoxes.append(self.tBoxClientName)
        
        self.txtBox4 = forms.TextBox()
        self.txtBox4.Text = self.fileName2
        txtBoxes.append(self.txtBox4)
        
        
        for each in txtBoxes:
            each.Width = 400
            #each.TextColor = darkgrey
        
        btn1 = forms.Button()
        btn1.ID = "txtBox1"
        btn1.Click += self.OnBtnPressedFile
        buttons.append(btn1)
        
        btn2 = forms.Button()
        btn2.ID = "txtBox2"
        btn2.Click += self.OnBtnPressedFolder
        buttons.append(btn2)
        
        btn3 = forms.Button()
        btn3.ID = "txtBox3"
        btn3.Click += self.OnBtnPressedFolder
        buttons.append(btn3)
        
        btn4 = forms.Button()
        btn4.ID = "txtBox4"
        btn4.Click += self.OnBtnPressedFolder
        buttons.append(btn4)
        
        
        self.drpDwnProjNum = forms.DropDown()
        self.drpDwnProjNum.DataStore = self.GetProjectList(r'C:\Program Files')
        
        self.drpDwnProjState = forms.DropDown()
        self.drpDwnProjState.DataStore = self.states
        self.drpDwnProjState.SelectedKey = 'New York'
        
        btnApply = forms.Button(Text = "Apply")
        btnApply.Height = 25
        btnCancel = forms.Button(Text = "Cancel")
        btnCancel.Height = 25
        btnCancel.Click += self.OnCancelPressed
        for each in buttons:
            each.Text = "..."
            each.Width = 25
        
        #4 - add controls to a layout
        layoutFolder = forms.DynamicLayout()
        layoutFolder.Spacing = drawing.Size(2,2)
        layoutFolder.AddRow(None, lblProjName, self.tBoxProjName, btn1)
        layoutFolder.AddRow(None, lblProjNum, self.drpDwnProjNum, btn2)
        layoutFolder.AddRow(None, lblClientName, self.tBoxClientName, btn3)
        layoutFolder.AddRow(None, lblProjCity, self.txtBox4, btn4)
        layoutFolder.AddRow(None, lblProjState, self.drpDwnProjState, btn4)
        layoutFolder.AddRow(None)
        
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(None)
        layoutButtons.AddRow(None, btnCancel, btnApply)
        
        layout = forms.DynamicLayout()
        layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)
        
        #5 - add the layout to the dialog
        self.Content = layout
    
    def OnBtnPressedFile(self, sender, e):
        print "You pressed a button. Good for youuuu."
        
        baseDialog = forms.Dialog() 
        openDialog = forms.OpenFileDialog()
        openDialog.Title = "Choose ACADscheme"
        openDialog.ShowDialog(baseDialog)
        
        if sender.ID == "tBoxProjName":
            self.tBoxProjName.Text = openDialog.FileName
        if sender.ID == "txtBox2":
            self.txtBox2.Text = openDialog.FileName
        if sender.ID == "txtBox3":
            self.txtBox3.Text = openDialog.FileName
        if sender.ID == "txtBox4":
            self.txtBox4.Text = openDialog.FileName

    def OnBtnPressedFolder(self, sender, e):
        baseDialog = forms.Dialog()
        openDialog = forms.OpenFileDialog()
        openDialog = forms.SelectFolderDialog()
        openDialog.Title = "Choose ACADscheme"
        openDialog.ShowDialog(baseDialog)
        if sender.ID == "tBoxProjName":
            self.tBoxProjName.Text = openDialog.Directory
        if sender.ID == "txtBox2":
            self.txtBox2.Text = openDialog.Directory
        if sender.ID == "txtBox3":
            self.txtBox3.Text = openDialog.Directory
        if sender.ID == "txtBox4":
            self.txtBox4.Text = openDialog.Directory

    def OnBtnPressedApply(self, sender, e):
        self.Close()

    def OnCancelPressed(self, sender, e):
        self.Close()

    def GetProjectList(self, path):
        folders = []
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)):
                folders.append(name)
        return folders
    
    def GeoData(self):
        self.states = [
        'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
        'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho', 
        'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana',
        'Maine' 'Maryland','Massachusetts','Michigan','Minnesota',
        'Mississippi', 'Missouri','Montana','Nebraska','Nevada',
        'New Hampshire','New Jersey','New Mexico','New York',
        'North Carolina','North Dakota','Ohio',    
        'Oklahoma','Oregon','Pennsylvania','Rhode Island',
        'South  Carolina','South Dakota','Tennessee','Texas','Utah',
        'Vermont','Virginia','Washington','West Virginia',
        'Wisconsin','Wyoming'
        ]


dialog = SettingsDialog()
dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)