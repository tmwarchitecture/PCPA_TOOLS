import rhinoscriptsyntax as rs
import random

def RandomRotate(obj, plane, domainSt, domainEnd):
    angle = random.uniform(domainSt,domainEnd)
    rs.RotateObject(obj, plane, angle)
    print "rotating"
    return obj

def RandomScaling(obj, plane, domainSt, domainEnd):
    scale = random.uniform(domainSt,domainEnd)
    rs.ScaleObject(obj, plane, (scale,scale,scale ))
    print "rotating"
    return obj

def main():
    objs = rs.GetObjects()
    
    for obj in objs:
        pts = rs.BoundingBox(obj)
        ctrPt = (pts[0] + pts[2]) / 2
        RandomRotate(obj, ctrPt, 0, 360)
        RandomScaling(obj, ctrPt, .8, 1.2)

if __name__ ==  "__main__":
    main()    