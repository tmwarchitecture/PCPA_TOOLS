import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino



def TestOffsetSubSrf():    
    msg="Select a surface or Brep face to offset"
    
    srf_filter= Rhino.DocObjects.ObjectType.Surface
    rc,objref=Rhino.Input.RhinoGet.GetMultipleObjects(msg,False,srf_filter)
    if rc!=Rhino.Commands.Result.Success: return
    
    offset=rs.GetReal("Offset value")
    if offset==None: return
    
    face=objref.Face()
    subSrf=face.ToNurbsSurface()
    
    oSrf=subSrf.Offset(offset,sc.doc.ModelAbsoluteTolerance)
    sc.doc.Objects.AddSurface(oSrf)
    sc.doc.Views.Redraw()

TestOffsetSubSrf()