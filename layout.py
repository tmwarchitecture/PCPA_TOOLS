import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import os.path
import datetime

def GetDatePrefix():
    year = int(datetime.datetime.today().strftime('%Y'))-2000
    md = datetime.datetime.today().strftime('%m%d')
    return str(year) + str(md)

def AddTitleBlock(size):
    rs.EnableRedraw(False)
    if size == 11:
        ttlPathRaw = r'C:\Users\Tim\Google Drive\180413\PROJ_TBLK 11x17L.dwg'
        if os.path.isfile(ttlPathRaw) == False:
            print "Titleblock file not found"
            return
        ttlPath = '"' + ttlPathRaw + '"'
        pt2 = [16.646, 10.646]
    elif size == 8:
        print "Titleblock not setup"
        return
    elif size == 18:
        print "Titleblock not setup"
        return
    
    layout = sc.doc.Views.GetPageViews()[-1]
    if layout is None:  return
    
    #Insert block
    rs.Command("-_Insert f "+ttlPath+" Block Enter 0,0,0 1.0 0.0", False)
    rs.Command("-_SelLast Enter")
    rs.Command("_Cut ")
    sc.doc.Views.ActiveView = layout
    rs.Command("_Paste ")
    rs.UnselectAllObjects()
    
    #Add detail
    pt1 = [.354, 1.417]
    
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
        
        defaultName = GetDatePrefix() + "_Rhino"
        
        filename = rs.SaveFileName("Save", "PDF (*.pdf)|*.pdf||", filename = defaultName)
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
        
        pdf = Rhino.FileIO.FilePdf.Create()
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
