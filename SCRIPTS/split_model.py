import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

def SplitBREPwithCurve(brep, plane):
    interCrvs = rc.Geometry.Intersect.Intersection.BrepPlane(brep, plane, rs.UnitAbsoluteTolerance())[1]
    
    if interCrvs is None:
        testPt = brep.Vertices[0].Location
        dist =  plane.DistanceTo(testPt)
        print dist
        if dist < 0:
            print "Side A"
            #sc.doc.Objects.AddBrep(brep)
        else:
            print "Side B"
    
    for numFaces, each in enumerate(brep.Faces): pass
    numFaces += 1
    
    for i in range(0, numFaces):
        brep = brep.Faces[i].Split(interCrvs, rs.UnitAbsoluteTolerance())
        print ""
    sc.doc.Objects.AddBrep(brep)

###############################################################################

def GetSectionCutSrfs(brep, plane):
    interCrvs = rc.Geometry.Intersect.Intersection.BrepPlane(brep, plane, rs.UnitAbsoluteTolerance())[1]
    return rc.Geometry.Brep.CreatePlanarBreps(interCrvs)

def IsBrepAbovePlane(brep, plane):
    intersection = rc.Geometry.Intersect.Intersection.BrepPlane(brep, plane, rs.UnitAbsoluteTolerance())
    interCrvs = intersection[1]
    if interCrvs is None:
        testPt = brep.Vertices[0].Location
        dist =  plane.DistanceTo(testPt)
        if dist < 0:
            return True
        else:
            return False
    if len(interCrvs) < 1:
        testPt = brep.Vertices[0].Location
        dist =  plane.DistanceTo(testPt)
        print dist
        if dist < 0:
            return True
        else:
            return False

def IsBrepIntersectingPlane(brep, plane):
    interCrvs = rc.Geometry.Intersect.Intersection.BrepPlane(brep, plane, rs.UnitAbsoluteTolerance())[1]
    if interCrvs:
        return True
    else:
        return False

def SplitObject(obj, plane):
    #EXTRUSIONS
    if isinstance(obj, rc.Geometry.Extrusion):
        obj = obj.ToBrep(False)
        print "converted extrusion"
    
    #BREPS
    if isinstance(obj, rc.Geometry.Brep):
        if IsBrepIntersectingPlane(obj, plane): #object intersects plane
            print "Intersecting"
            trimObjs = []
            sectionSrfs = []
            splitObjects = obj.Trim(plane, rs.UnitAbsoluteTolerance())
            for eachSplitObj in splitObjects:
                trimObjs.append(sc.doc.Objects.AddBrep(eachSplitObj))
            if obj.IsSolid: #interecting object is solid
                tempSecSrfs = GetSectionCutSrfs(obj, plane)
                for eachSection in tempSecSrfs:
                    sectionSrfs.append(sc.doc.Objects.AddBrep(eachSection))
            return [trimObjs, sectionSrfs]
        else: #object above the plane
            if IsBrepAbovePlane(obj, plane):
                print "Above plane"
                return [sc.doc.Objects.AddBrep(obj)]
    
    #CURVES
    if isinstance(obj, rc.Geometry.Curve):
        intersection = rc.Geometry.Intersect.Intersection.CurvePlane(obj, plane, rs.UnitAbsoluteTolerance())
        if intersection is None: 
            return None
        params = []
        for each in intersection:
            params.append(each.ParameterA)
        
        splitCrvs = obj.Split(params)
        for eachCrv in splitCrvs:
            testPt = eachCrv.GetBoundingBox(False).Center
            dist = plane.DistanceTo(testPt)
            if dist < 0:
                return [sc.doc.Objects.AddCurve(eachCrv)]


###############################################################################
#MAIN
def SplitModel(objs, srf):
    rhSrf = rs.coercesurface(srf)
    plane = rhSrf.TryGetPlane()[1]
    group = rs.AddGroup('Split Model')
    
    
    #rs.HideObject(objs)
    
    for obj in objs:
        #BLOCKS
        if rs.IsBlockInstance(obj):
            matrix = rs.BlockInstanceXform(obj)
            blockObjs = rs.BlockObjects(rs.BlockInstanceName(obj))
            for eachBlockObj in blockObjs:
                xformedObj = rs.TransformObject(eachBlockObj, matrix, True)
                print ""
                rhobj = rs.coercegeometry(xformedObj)
                newObj = SplitObject(rhobj, plane)
                print ""
                if newObj is not None:
                    rs.MatchObjectAttributes(newObj, eachBlockObj)
                    #rs.ShowObject(newObj)
                    rs.AddObjectToGroup(newObj, group)
                print ""
                #rs.DeleteObject(xformedObj)
        
        #GEOMETRY
        else:
            rhobj = rs.coercegeometry(obj)
            newObj = SplitObject(rhobj, plane)
            if newObj is not None:
                print ""
                rs.MatchObjectAttributes(newObj, obj)
                rs.ShowObject(newObj)
                #rs.AddObjectToGroup(newObj, group)

def main():
    objs = rs.GetObjects("Select objects to split")
    if objs is None: return
    
    srf = rs.GetObject("Select split surface", rs.filter.surface)
    if srf is None: return
    
    #rs.EnableRedraw(False)
    SplitModel(objs, srf)
    #rs.EnableRedraw(True)

if __name__ == "__main__":
    main()