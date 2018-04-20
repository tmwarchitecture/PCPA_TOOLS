import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import os.path
import datetime
import sys
sys.path.append(r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA')
import PCPA

def GetDatePrefix():
    year = int(datetime.datetime.today().strftime('%Y'))-2000
    md = datetime.datetime.today().strftime('%m%d')
    return str(year) + str(md)

def AddTitleBlock(size):
    rs.EnableRedraw(False)
    fileLocations = PCPA.config.GetDict()
    if size == 11:
        ttlPathRaw = fileLocations['Titleblock 11x17L']
        if os.path.isfile(ttlPathRaw) == False:
            print "Titleblock file not found"
            return
        ttlPath = '"' + ttlPathRaw + '"'
        offset = .354
        row1 = offset
        row2 = row1*2
        row3 = row1*3
        row4 = row1*4
        leftEdge = offset
        middle = 17/2
        rightEdge = 17-offset
        
        pt1 = [leftEdge, row4]
        pt2 = [rightEdge, 11-row1]
        txtBase1 = [middle,row2]
        txtBase2 = [leftEdge,row2]
        txtBase3 = [rightEdge,row2]
        txtBase4 = [leftEdge,row1]
        txtBase5 = [rightEdge,row1]
        
        lineSt = [leftEdge, row3]
        lineEnd = [rightEdge, row3]
        
        txtSizeL = .125
        txtSizeM = .094
    
    elif size == 8:
        ttlPathRaw = fileLocations['Titleblock 8.5x11L']
        if os.path.isfile(ttlPathRaw) == False:
            print "Titleblock file not found"
            return
        ttlPath = '"' + ttlPathRaw + '"'
        
        offset = .229
        row1 = offset
        row2 = row1*2
        row3 = row1*3
        row4 = row1*4
        leftEdge = offset
        middle = 11/2
        rightEdge = 11-offset
        
        pt1 = [leftEdge, row4]
        pt2 = [rightEdge, 8.5-row1]
        txtBase1 = [middle,row2]
        txtBase2 = [leftEdge,row2]
        txtBase3 = [rightEdge,row2]
        txtBase4 = [leftEdge,row1]
        txtBase5 = [rightEdge,row1]
        
        lineSt = [leftEdge, row3]
        lineEnd = [rightEdge, row3]
        
        txtSizeL = .125
        txtSizeM = .063
        
    elif size == 18:
        ttlPathRaw = fileLocations['Titleblock 18x24L']
        if os.path.isfile(ttlPathRaw) == False:
            print "Titleblock file not found"
            return
        ttlPath = '"' + ttlPathRaw + '"'
        offset = .5
        row1 = offset
        row2 = row1*2
        row3 = row1*3
        row4 = row1*4
        leftEdge = offset
        middle = 24/2
        rightEdge = 24-offset
        
        pt1 = [leftEdge, row4]
        pt2 = [rightEdge, 18-row1]
        txtBase1 = [middle,row2]
        txtBase2 = [leftEdge,row2]
        txtBase3 = [rightEdge,row2]
        txtBase4 = [leftEdge,row1]
        txtBase5 = [rightEdge,row1]
        
        lineSt = [leftEdge, row3]
        lineEnd = [rightEdge, row3]
        
        txtSizeL = .250
        txtSizeM = .125
    
    layout = sc.doc.Views.GetPageViews()[-1]
    if layout is None:  return
    
    #Insert block
    #rs.Command("-_Insert f "+ttlPath+" Block Enter 0,0,0 1.0 0.0", False)
    #rs.Command("-_SelLast Enter")
    #rs.Command("_Cut ")
    sc.doc.Views.ActiveView = layout
    #rs.Command("_Paste ")
    #rs.UnselectAllObjects()
    
    projectTitle = rs.GetDocumentData(section = "PCPA", entry = "Project Title")
    if projectTitle is None:
        projectTitle = "Project Title"
    
    clientName = rs.GetDocumentData(section = "PCPA", entry = "Client Name")
    if clientName is None:
        clientName = "Client Name"
    
    #Add text
    rs.AddText("Title", txtBase1, txtSizeL, justification = 2)
    rs.AddText(projectTitle, txtBase2, txtSizeL, justification = 1)
    rs.AddText('%<Date("MMMM d, yyyy")>%', txtBase3, txtSizeM, justification = 4)
    
    rs.AddText(clientName, txtBase4, txtSizeM, justification = 1)
    rs.AddText('COPYRIGHT %<Date("yyyy")>% Pelli Clarke Pelli Architects', txtBase5, txtSizeM, justification = 4)
    
    rs.AddLine(lineSt, lineEnd)
    
    #Add detail
    rs.AddDetail(layout.ActiveViewportID, pt1, pt2, "PCPA " + str(layout.PageName), 7)
    
    rs.EnableRedraw(True)

def AddLayout(size):
    if size == 11:
        name = '11x17 '
        width = '17 '
        height = '11 '
    elif size == 8:
        name = '8.5x11 '
        width = '11 '
        height = '8.5 '
    elif size == 18:
        name = '18x24 '
        width = '24 '
        height = '18 '
    result = rs.Command('-_Layout ' + name + width + height + '0 ', False)
    
    if result:
        AddTitleBlock(size)

def BatchPrintLayouts():
    print "BatchPrintLayout is WIP. Use with caution."
    try:
        pages = sc.doc.Views.GetPageViews()
        if pages is None or len(pages) < 1:
            print "No layouts in file"
            return
        
        defaultPath = rs.DocumentPath()
        
        defaultName = GetDatePrefix() + "_Rhino"
        
        filename = rs.SaveFileName("Save", "PDF (*.pdf)|*.pdf||", folder = defaultPath, filename = defaultName)
        if filename is None: return
        
        names = []
        for page in pages:
            names.append([page.PageName, False])
        selectedLayouts = rs.CheckListBox(names, "Select Layouts to print", "Batch Print")
        if selectedLayouts is None: return
        
        stop = False
        for layout in selectedLayouts:
            if layout[1]==True:
                stop = True
                break
        if stop == False:
            print "No layouts selected"
            return
        try:
            pdf = Rhino.FileIO.FilePdf.Create()
        except:
            print "Failed to load Rhino.FileIO.FilePdf.Create()"
            return
        dpi = 300
        for i, page in enumerate(pages):
                if selectedLayouts[i][1]:
                    capture = Rhino.Display.ViewCaptureSettings(page, dpi)
                    pdf.AddPage(capture)
        pdf.Write(filename)
        print "PDF saved to {}".format(filename)
    except IOError, e:
        print str(e)
        return

def main(func):
    if func is None: return

    if func < 50:
        AddLayout(func)
    elif func == 90:
        BatchPrintLayouts()

if __name__ == "__main__":
    func = rs.GetInteger()
    main(func)