import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing

def rCommonCap1(filePath, viewportName,width, height):
    RhinoDocument = rc.RhinoDoc.ActiveDoc
    view = RhinoDocument.Views.Find(viewportName, False)
    
    origWidth = view.ActiveViewport.Size.Width
    origHeight = view.ActiveViewport.Size.Height
    
    rs.Command('-_ViewportProperties s ' + str(width) +  ' ' + str(height) + ' Enter', False)
    
    size = System.Drawing.Size(width, height)
    capture = view.CaptureToBitmap(size)
    capture.Save(filePath);
    
    rs.Command('-_ViewportProperties s ' + str(origWidth) +  ' ' + str(origHeight) + ' Enter', False)

def rCommonCap2(filePath, viewportName, width, height):
    #Get active doc
    RhinoDocument = rc.RhinoDoc.ActiveDoc
    
    #Get namedview index
    index = sc.doc.NamedViews.FindByName(viewportName)
    
    #Get active viewport
    activeView = sc.doc.Views.ActiveView.ActiveViewport
    if activeView is None: return
    
    #Set the current viewport (activeView) to namedView (viewportName)
    sc.doc.NamedViews.Restore(index, activeView)
    
    
    #Get the view
    view = RhinoDocument.Views.Find(viewportName, False)
    
    #Create the capture
    size = System.Drawing.Size(width,height)
    capture = view.CaptureToBitmap(size)
    
    #Save image
    capture.Save(filePath)

def SafeCapture(filePath, width, height):
    """
    Saves the active viewport to png
    """
    #Get the view
    view = sc.doc.Views.ActiveView
    
    #Get sizes
    size = System.Drawing.Size(width,height)
    origSize = view.ActiveViewport.Size
    
    #Change viewport size
    view.Size = size
    
    #Create the capture
    mainCapture = rc.Display.ViewCapture()
    mainCapture.DrawAxes = False
    mainCapture.DrawGridAxes = False
    mainCapture.TransparentBackground = True
    mainCapture.Width = width
    mainCapture.Height = height
    capture = mainCapture.CaptureToBitmap(view)
    capture.Save(filePath)
    
    #Restore viewport size
    view.Size = origSize
    return True

def main():
    filePath = rs.SaveFileName('Save file name', "PNG (*.png; *.png)|")
    filePath += '.png'
    
    #rCommonCap1(filePath, viewport, 3300, 5100)
    #rCommonCap2(filePath, viewport, 5100, 3300)
    SafeCapture(filePath, 5100, 3300)

main()