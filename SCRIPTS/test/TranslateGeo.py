import rhinoscriptsyntax as rs
import Rhino as rc
import ast

def EncodeCurve(obj):
    def SaveCurveVertices(curve):
        vertices = []
        if rs.IsArc(curve):
            midPt = rs.ArcMidPoint(curve)
            stPt = rs.CurveStartPoint(curve)
            endPt = rs.CurveEndPoint(curve)
            pts = [stPt, midPt, endPt]
        else:
            pts = rs.CurveEditPoints(curve)
        for pt in pts:
            vertices.append([pt.X, pt.Y, pt.Z])
        return vertices
     
    try:
        fullList = []
        
        segments = rs.ExplodeCurves(obj)
        if len(segments) < 1:
            segments = [rs.CopyObject(obj)]
        
        for eachSeg in segments:
            vertices = []
            if rs.IsLine(eachSeg):
                fullList.append(["line", SaveCurveVertices(eachSeg)])
            elif rs.IsArc(eachSeg):
                fullList.append(["arc", SaveCurveVertices(eachSeg)])
            elif rs.IsCurve(eachSeg):
                fullList.append(["curve", SaveCurveVertices(eachSeg)])
            else:
                fullList.append(["error"])
            rs.DeleteObjects(segments)
        return fullList
    except:
        print "Error"
        return None

def DecodeCurve(string):
    try:
        fullList = ast.literal_eval(string)
        segList = []
        for eachSegment in fullList:
            if eachSegment[0] == "line":
                segList.append(rs.AddLine(eachSegment[1][0], eachSegment[1][1]))
            elif eachSegment[0] == "arc":
                segList.append(rs.AddArc3Pt(eachSegment[1][0], eachSegment[1][2], eachSegment[1][1]))
            elif eachSegment[0] == "curve":
                segList.append(rs.AddCurve(eachSegment[1]))
        if len(segList)<2:
            segList[0]
        else:
            return rs.JoinCurves(segList, True)
    except:
        print "Error"
        return None


def main():
    #1
    #obj = rs.GetObject()
    #if obj is None: return
    #print EncodeCurve(obj)
    
    #2
    test = r"[['arc', [[467.4407412344483, 1012.5211859316647, 0.0], [698.42505290447957, 1108.1980205208151, 0.0], [794.10188749359793, 1339.1823321908596, 0.0]]]]"
    DecodeCurve(test)

main()