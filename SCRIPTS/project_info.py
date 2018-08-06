import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.UI
import os
import rhinoscriptsyntax as rs
from layout import GetDatePrefix
from libs import yaml

__author__ = 'Tim Williams'
__version__ = "2.0.0"

class SettingsDialog(forms.Dialog):
    def __init__(self):
        self.Initialize()
        self.CreateControls()
        self.CreateLayout()

    def Initialize(self):
        #Setup the dialog
        self.Title = "Project Information"
        self.Size = drawing.Size(600,330)
        self.Padding = drawing.Padding(5, 5)

        self.lightgrey = drawing.Colors.LightGrey
        self.darkgrey = drawing.Colors.DarkGray

        self.InitVariables()

    def CreateControls(self):
        self.txtBoxList = []
        self.labelList = []

        #LABELS
        def labels():
            self.lblProj = forms.Label()
            self.lblProj.Text = "Project"
            self.labelList.append(self.lblProj)

            self.lblVersion = forms.Label()
            self.lblVersion.Text = "Version"
            self.labelList.append(self.lblVersion)

            self.lblProjName = forms.Label()
            self.lblProjName.Text = "Name"
            self.labelList.append(self.lblProjName)

            self.lblProjNum = forms.Label()
            self.lblProjNum.Text = "Number"
            self.labelList.append(self.lblProjNum)

            self.lblClientName = forms.Label()
            self.lblClientName.Text = "Client Name"
            self.labelList.append(self.lblClientName)

            self.lblProjCity = forms.Label()
            self.lblProjCity.Text = "City"
            self.labelList.append(self.lblProjCity)

            self.lblProjState = forms.Label()
            self.lblProjState.Text = "State"
            self.labelList.append(self.lblProjState)

            self.lblProjCountry = forms.Label()
            self.lblProjCountry.Text = "Country"
            self.labelList.append(self.lblProjCountry)

            for eachLabel in self.labelList:
                eachLabel.VerticalAlignment = forms.VerticalAlignment.Center
                eachLabel.TextAlignment = forms.TextAlignment.Right
                if eachLabel.Text == "Project" or eachLabel.Text == "Database Version":
                    continue
                eachLabel.Enabled = False

        #TEXT BOXES
        def textBoxes():
            self.tBoxProjName = forms.TextBox()
            self.tBoxProjName.Text = "Project Name"
            self.txtBoxList.append(self.tBoxProjName)

            self.tBoxProjNum = forms.TextBox()
            self.tBoxProjNum.Text = "Project Number"
            self.txtBoxList.append(self.tBoxProjNum)

            self.tBoxClientName = forms.TextBox()
            self.tBoxClientName.Text = "Client Name"
            self.txtBoxList.append(self.tBoxClientName)

            self.tBoxProjCity = forms.TextBox()
            self.tBoxProjCity.Text = "Project City"
            self.txtBoxList.append(self.tBoxProjCity)

            for eachtxtBox in self.txtBoxList:
                eachtxtBox.Width = 400
                eachtxtBox.Enabled = False

        #BUTTONS
        def buttons():
            self.btnApply = forms.Button(Text = "Apply")
            self.btnApply.Height = 25
            self.btnApply.Click += self.OnApplyPressed
            self.btnApply.Enabled = False

            self.btnCancel = forms.Button(Text = "Cancel")
            self.btnCancel.Height = 25
            self.btnCancel.Click += self.OnCancelPressed

            self.btnSave = forms.Button(Text = "Save")
            self.btnSave.Height = 25
            self.btnSave.Click += self.OnSavePressed
            self.btnSave.Enabled = False

            self.btnSaveAs = forms.Button(Text = "Save As...")
            self.btnSaveAs.Height = 25
            self.btnSaveAs.Click += self.OnSaveAsPressed
            self.btnSaveAs.Enabled = False

            self.btnTest = forms.Button(Text = "Test")
            self.btnTest.Height = 25
            self.btnTest.Click += self.OnTestPressed

        #DROP DOWNS
        def dropDowns():
            self.drpDwnProj = forms.DropDown()
            self.drpDwnProj.DataStore = self.GetProjectList(r'J:\\')
            self.drpDwnProj.SelectedIndexChanged += self.OnProjectChanged

            self.drpDwnVersion = forms.DropDown()
            self.drpDwnVersion.Enabled = False
            self.drpDwnVersion.DataStore = ['---CREATE NEW---', '180427_Stacking']
            self.drpDwnVersion.SelectedIndexChanged += self.OnVersionChanged

            self.drpDwnProjState = forms.DropDown()
            self.drpDwnProjState.DataStore = self.states
            self.drpDwnProjState.SelectedKey = 'New York'
            self.drpDwnProjState.Enabled = False

            self.drpDwnProjCountry = forms.DropDown()
            self.drpDwnProjCountry.DataStore = self.countries
            self.drpDwnProjCountry.SelectedKey = 'United States of America'
            self.drpDwnProjCountry.Enabled = False

        #Call them
        labels()
        textBoxes()
        buttons()
        dropDowns()

        #self.LoadExistingData()

    def CreateLayout(self):
        #Main Layout
        layoutFolder = forms.DynamicLayout()
        layoutFolder.Spacing = drawing.Size(2,2)
        layoutFolder.AddRow(None, self.lblProj, self.drpDwnProj)
        layoutFolder.AddRow(None, self.lblVersion, self.drpDwnVersion)
        layoutFolder.AddRow(None, self.lblProjName, self.tBoxProjName)
        layoutFolder.AddRow(None, self.lblProjNum, self.tBoxProjNum)
        layoutFolder.AddRow(None, self.lblClientName, self.tBoxClientName)
        layoutFolder.AddRow(None, self.lblProjCity, self.tBoxProjCity)
        layoutFolder.AddRow(None, self.lblProjState, self.drpDwnProjState)
        layoutFolder.AddRow(None, self.lblProjCountry, self.drpDwnProjCountry)
        layoutFolder.AddRow(None)

        #Bottom row
        layoutButtons = forms.DynamicLayout()
        layoutButtons.AddRow(None)
        layoutButtons.AddRow(None, self.btnTest, self.btnCancel, self.btnApply, self.btnSave, self.btnSaveAs)

        #Final Layout
        layout = forms.DynamicLayout()
        layout.AddSeparateRow(layoutFolder)
        layout.AddSeparateRow(layoutButtons)

        #Add the layout to the dialog
        self.Content = layout

    #Data
    def GetProjectList(self, path):
        folders = []
        try:
            for name in os.listdir(path):
                if os.path.isdir(os.path.join(path, name)):
                    folders.append(name)
            folders.sort()
        except:
            path = r'C:\Users\Tim\Desktop\temp'
            for name in os.listdir(path):
                if os.path.isdir(os.path.join(path, name)):
                    folders.append(name)
            folders.sort()
        return folders

    def InitVariables(self):
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

        self.countries = [
        'Afghanistan', 'Aland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra',
        'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia',
        'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh',
        'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia',
        'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island', 'Brazil', 'British Virgin Islands',
        'British Indian Ocean Territory', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso',
        'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands',
        'Central African Republic', 'Chad', 'Chile', 'China', 'Hong Kong, SAR China',
        'Macao, SAR China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia',
        'Comoros', 'Congo', 'Cook Islands', 'Costa Rica',
        'Cote dIvoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti',
        'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea',
        'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands (Malvinas)', 'Faroe Islands', 'Fiji',
        'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern Territories',
        'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland',
        'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau',
        'Guyana', 'Haiti', 'Heard and Mcdonald Islands', 'Holy See_(Vatican City State)', 'Honduras',
        'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran, Islamic Republic of', 'Iraq', 'Ireland',
        'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan',
        'Kenya', 'Kiribati', 'Korea_(North)', 'Korea_(South)', 'Kuwait', 'Kyrgyzstan', 'Lao PDR',
        'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
        'Macedonia, Republic of', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta',
        'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico',
        'Micronesia, Federated States of', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat',
        'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands',
        'Netherlands Antilles', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria',
        'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau',
        'Palestinian Territory', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn',
        'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Reunion', 'Romania', 'Russian Federation', 'Rwanda',
        'Saint-Barthelemy', 'Saint Helena', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint-Martin (French part)',
        'Saint Pierre and Miquelon', 'Saint Vincent and Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe',
        'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia',
        'Solomon Islands', 'Somalia', 'South Africa', 'South Georgia and the South Sandwich Islands', 'South Sudan',
        'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Svalbard and Jan Mayen Islands', 'Swaziland', 'Sweden', 'Switzerland',
        'Syrian Arab Republic_(Syria)', 'Taiwan, Republic of China', 'Tajikistan', 'Tanzania, United Republic of', 'Thailand', 'Timland',
        'Timor-Leste', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
        'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom',
        'United States of America', 'US Minor Outlying Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu',
        'Venezuela_(Bolivarian Republic)', 'Vietnam', 'Virgin Islands, US', 'Wallis and Futuna Islands', 'Western Sahara',
        'Yemen', 'Zambia', 'Zimbabwe',
        ]

    def LoadExistingData(self):
        dataBaseExists = False
        try:
            self.drpDwnProjNum.SelectedValue = rs.GetDocumentData('PCPA', 'Project_Folder')
            dataBaseExists = True
        except:
            pass

        if dataBaseExists:
            self.tBoxProjCity.Text = rs.GetDocumentData('PCPA', 'Project_City')
        #

    #Button Press Events
    def OnApplyPressed(self, sender, e):
        proj_Folder = self.drpDwnProjNum.SelectedValue
        #proj_Name = self.drpDwnProjNum.SelectedValue.split("_")[1]
        #proj_Number = self.drpDwnProjNum.SelectedValue.split("_")[0]
        rs.SetDocumentData('PCPA', 'Project_Folder', self.drpDwnProjNum.SelectedValue)
        #rs.SetDocumentData('PCPA', 'Project_Number', proj_Number)
        #rs.SetDocumentData('PCPA', 'Project_Name', proj_Name)
        #rs.SetDocumentData('PCPA', 'Project_City', self.tBoxProjCity.Text)
        self.Close()

    def OnCancelPressed(self, sender, e):
        self.Close()

    def OnTestPressed(self, sender, e):
        try:
            root = os.path.dirname(os.path.realpath(__file__))
            yamlPath = os.path.join(root, r'data\Project_Database.yaml')

            with open(yamlPath, 'r') as fileDescriptor:
                database = yaml.load(fileDescriptor)

            try:
                self.tBoxProjName.Text = database['Project']['Name']
            except:
                pass
            try:
                self.tBoxProjNum.Text = database['Project']['Number']
            except:
                pass
            try:
                self.tBoxClientName.Text = database['Project']['Client']['Name']
            except:
                pass
            try:
                self.tBoxProjCity.Text = database['Project']['Location']['City']
            except:
                pass
            try:
                self.drpDwnProjState.SelectedKey = database['Project']['Location']['State']
            except:
                pass
            try:
                self.drpDwnProjCountry.SelectedKey = database['Project']['Location']['Country']
            except:
                pass
        except:
            print "YAML Failed"

    def OnSavePressed(self, sender, e):
        print "Save"

    def OnSaveAsPressed(self, sender, e):
        print "Save As"
        path = rs.StringBox('Version Name', GetDatePrefix() + "_Version_01", 'Save new version')
        self.SaveToYaml(path)

    #Drop down Events
    def OnProjectChanged(self, sender, e):
        print "Changed the project"
        for eachLabel in self.labelList:
            eachLabel.Enabled = False
        for eachTextBox in self.txtBoxList:
            eachTextBox.Enabled = False
        try:
            print sender.SelectedValue
        except:
            print "fail"
        self.drpDwnVersion.Enabled = True
        self.lblVersion.Enabled = True

    def OnVersionChanged(self, sender, e):
        print "Changed the database version"
        for eachLabel in self.labelList:
            eachLabel.Enabled = True
        for eachTextBox in self.txtBoxList:
            eachTextBox.Enabled = True
        self.btnSave.Enabled = True
        self.btnSaveAs.Enabled = True
        self.drpDwnProjState.Enabled = True
        self.drpDwnProjCountry.Enabled = True

    #YAML
    def SaveToYaml(self, path):
        print "Saved" + str(path)
        #if already exists:
        #    import file
        #else:
        #    Import blank yaml
        #save Yaml data

def main():
    dialog = SettingsDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)

if __name__ == "__main__":
    main()
