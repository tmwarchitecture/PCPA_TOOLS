import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

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
    rs.Command('-_Layout ' + name + width + height + '0 ', False)

def BatchPrintLayouts():
    print "BatchPrintLayout is WIP. Use with caution."
    try:
        pages = sc.doc.Views.GetPageViews()
        if pages is None or len(pages) < 1:
            print "No layouts in file"
            return
        
        filename = rs.SaveFileName("Save", "PDF (*.pdf)|*.pdf||")
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
    