import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rc

def main():
    path = rs.SaveFileName('Save view location', "JPEG (*.jpg; *.jpeg)|")
    if path is None: return
    
    
    origWidth = sc.doc.Views.ActiveView.ActiveViewport.Size.Width
    origHeight = sc.doc.Views.ActiveView.ActiveViewport.Size.Height
    
    if 'safeCapture-width' in sc.sticky:
        defaultWidth = sc.sticky['safeCapture-width']
    else:
        defaultWidth = 5100
    if 'safeCapture-height' in sc.sticky:
        defaultHeight = sc.sticky['safeCapture-height']
    else:
        defaultHeight = 3300
    
    
    width =  rs.GetInteger('Width', defaultWidth, 200, 10000 )
    if width is None: return
    
    sc.sticky['safeCapture-width'] = width
    
    height = rs.GetInteger('Height', defaultHeight, 200, 10000 )
    if height is None: return
    
    rs.EnableRedraw(False)
    
    sc.sticky['safeCapture-height'] = height
    
    rs.Command('-_ViewportProperties s ' + str(width) +  ' ' + str(height) + ' Enter', False)
    
    rs.Command('-_ViewCaptureToFile u p _Width=' + str(width) + ' _Height=' + str(height) + ' _Scale=1 _LockAspectRatio=No _DrawGrid=No _DrawWorldAxes=No _TransparentBackground=No "' + path + '" _Enter', False)
    
    rs.Command('-_ViewportProperties s ' + str(origWidth) +  ' ' + str(origHeight) + ' Enter', False)
    
    rs.EnableRedraw(True)
    
    print "Image saved as {}".format(path)

if __name__ == "__main__":
    main()