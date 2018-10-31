import rhinoscriptsyntax as rs
import ast

def EncodeCurve(obj):
    def SaveCurveVertices(curve):
        vertices = []
        pts = rs.CurveEditPoints(curve)
        for pt in pts:
            vertices.append([pt.X, pt.Y, pt.Z])
        return vertices
    
    fullList = []
    
    segments = rs.ExplodeCurves(obj)
    
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

def DecodeCurve(string):
    fullList = ast.literal_eval(string)
    for eachSegment in fullList:
        if eachSegment[0] == "line":
            rs.AddLine(eachSegment[1][0], eachSegment[1][1])
        elif eachSegment[0] == "arc":
            rs.AddArc3Pt(eachSegment[1][0], eachSegment[1][2], eachSegment[1][1])
        elif eachSegment[0] == "curve":
            rs.AddCurve(eachSegment[1])

#obj = rs.GetObject()
#print EncodeCurve(obj)

test = r"[['arc', [[-55.255517226136632, 15.487086341931672, 0.0], [-53.412062437138239, 11.036592788710117, 0.0], [-48.961568883916691, 9.1931379997117091, 0.0]]], ['line', [[-48.961568883916691, 9.1931379997117091, 0.0], [-35.412008630829121, 9.1931379997117091, 0.0]]], ['arc', [[-35.412008630829121, 9.1931379997117091, 0.0], [-30.09214102122769, 6.9895766857854555, 0.0], [-27.888579707301449, 1.6697090761840341, 0.0]]], ['line', [[-27.888579707301453, 1.6697090761840343, 0.0], [-27.888579707301453, -16.829155011010577, 0.0]]], ['line', [[-27.888579707301453, -16.829155011010577, 0.0], [-40.75866133382376, -16.829155011010577, 0.0]]], ['curve', [[-40.75866133382376, -16.829155011010577, 0.0], [-44.803578867535016, -13.854573156053108, 0.0], [-46.151884712105435, -4.9308275911807016, 0.0]]], ['line', [[-46.151884712105435, -4.9308275911807016, 0.0], [-72.840501343091404, -4.9308275911807016, 0.0]]], ['line', [[-72.840501343091404, -4.9308275911807016, 0.0], [-72.840501343091404, 40.41890996475567, 0.0]]], ['line', [[-72.840501343091404, 40.41890996475567, 0.0], [-55.255517226136632, 40.41890996475567, 0.0]]], ['line', [[-55.255517226136632, 40.41890996475567, 0.0], [-55.255517226136632, 15.487086341931672, 0.0]]]]"
print DecodeCurve(test)
