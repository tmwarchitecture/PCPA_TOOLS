import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

from string import ascii_letters as letters
import datetime
import os
from libs import csv
from libs import encrypt
import getpass
import config
import random
import hashlib

__author__ = 'Tim Williams'
__version__ = "2.2.0"

#############################################################################
#AUTHORIZATION
def Authorize():
    root = os.path.join(os.environ['appdata'], "PCPA")
    if not os.path.isdir(root):
        os.makedirs(root)
    authFile = os.path.join(root, 'authorize.pcpa')
    file = open(authFile,'w')
    file.write("True")
    file.close()
    print "Computer Authorized"
    return True

def GetAuthorization():
    root = os.path.join(os.environ['appdata'], "PCPA")
    if not os.path.isdir(root):
        os.makedirs(root)
    while True:
        password = rs.GetString("Enter PCPA Rhino Toolbar license key")
        if password is None: return False
        hash = hashlib.sha224(password).hexdigest()
        key = '7bce017b9e1c5f1a3a73d8edfb7e47505a39375cb0f83e89c48f9c55'

        if hash == key:
            Authorize()
        else:
            print "Incorrect password"

def IsAuthorized():
    authFile = os.path.join(os.environ['appdata'], "PCPA", 'authorize.pcpa')
    if os.path.isfile(authFile):
        file = open(authFile,'rb')
        if file.readline() == "True":
            file.close()
            return True
        file.close()
        return False
    else:
        location = GetNetworkLocation()
        if location == 0 or location == 1:
            return Authorize()
        if location == 2:
            return GetAuthorization()


#############################################################################
#DATE/LOCATION
def GetDatePrefix():
    """Gets todays date and returns it in the format of YYMMDD
    returns:
        date(String): YYMMDD, e.g. 180706
    """
    year = int(datetime.datetime.today().strftime('%Y'))-2000
    md = datetime.datetime.today().strftime('%m%d')
    return str(year) + str(md)

def IsScriptLocal():
    drive, path_and_file = os.path.splitdrive(os.path.realpath(__file__))
    if drive == r'C:':
        return True
    else: return False

def GetNetworkLocation():
    """Checks the network to see if X: or H: exist. If X:, then returns 0 (for New York). If H: then returns 1 (for New Haven), 2 for Unknown
    """
    NYPath = r'X:\22_REACH'
    NHPath = r'D:\PCPA_TOOLS'

    if os.path.isdir(NYPath):
        location = "New York"
        return 0
    elif os.path.isdir(NHPath):
        location = "New Haven"
        return 1
    else:
        return 2

def IsSavedInProjectFolder():
    """Checks if Rhino file is saved in a project folder
    """
    fileLocations = config.GetDict()
    if rs.DocumentPath()[:2] == fileLocations['Project Folders'][:2]: return True
    else: return False

#############################################################################
#ANALYTICS
def SaveToAnalyticsOLD(funcName):
    """SaveToAnalytics(funcName)
    Inputs:
        funcName(str): The functions name
    returns:
        None
    """
    try:
        fileLocations = config.GetDict()
        filepath = fileLocations['Analytics']


        #filepath = 'data\Analytics.csv'

        with open(filepath, 'rb') as File:
            reader = csv.reader(File)
            data = list(reader)

        #Update date
        data[0][1] = 'Last Updated: ' + GetDatePrefix()

        #Username
        userName = encrypt.encrypt(getpass.getuser())

        #Update Column
        colPos = None
        for i,item in enumerate(data[1]):
            if item == funcName:
                colPos = i
        if colPos is None:
            colPos = len(data[1])
            data[1].append(funcName)

        rowPos = None
        for i,item in enumerate(data):
            if item[0] == userName:
                rowPos = i
        if rowPos is None:
            rowPos = len(data)
            data.append([userName])

        newCells = (colPos+1) - len(data[rowPos])
        for i in range(newCells):
            data[rowPos].append('')

        try:
            data[rowPos][colPos] = int(data[rowPos][colPos]) + 1
        except:
            data[rowPos][colPos] = 1

        myFile = open(filepath, 'wb')
        with myFile:
            csvwriter = csv.writer(myFile)
            csvwriter.writerows(data)
    except:
        print "Analytics failed"

def SaveToAnalytics(funcName):
    """SaveToAnalytics(funcName)
    Inputs:
        funcName(str): The functions name
    returns:
        None
    """
    try:
        now=datetime.datetime.now()
        monthString=('%02d%02d'%(now.year, now.month))[2:]

        fileLocations = config.GetDict()
        filepath = fileLocations['Data Folder']

        fileName = monthString + '_Analytics.csv'
        fullName = os.path.join(filepath, fileName)

        dateString='%02d-%02d-%02d'%(now.year, now.month, now.day)
        if not os.path.isfile(fullName):
            data = [[funcName , 'Last Updated']]
            myFile = open(fullName, 'wb')
            with myFile:
                csvwriter = csv.writer(myFile)
                csvwriter.writerows(data)
            myFile.close()

        with open(fullName, 'rb') as File:
            reader = csv.reader(File)
            data = list(reader)
            File.close()
        #Update date
        data[0][1] = 'Last Updated: ' + GetDatePrefix()

        #Username
        userName = encrypt.encrypt(getpass.getuser())

        #Update Column
        colPos = None
        if len(data)>1: #If there is a second row:
            for i,item in enumerate(data[1]):
                if item == funcName:
                    colPos = i
            if colPos is None:
                colPos = len(data[1])
                data[1].append(funcName)
        else: #If there is not a second row
            colPos = 1
            data.append(['User', funcName])

        rowPos = None
        for i,item in enumerate(data):
            if item[0] == userName:
                rowPos = i
        if rowPos is None:
            rowPos = len(data)
            data.append([userName])

        newCells = (colPos+1) - len(data[rowPos])
        for i in range(newCells):
            data[rowPos].append('')

        try:
            data[rowPos][colPos] = int(data[rowPos][colPos]) + 1
        except:
            data[rowPos][colPos] = 1
        with open(fullName, 'wb') as myFile:
            csvwriter = csv.writer(myFile)
            csvwriter.writerows(data)
    except:
        print "Analytics failed"

def SaveFunctionData(funcName, funcData):
    """
    SaveFunctionData(funcName, funcData)
    funcName = name of function(str)
    funcData = data to save [list]
    """
    try:
        now=datetime.datetime.now()
        monthString=('%02d%02d'%(now.year, now.month))[2:]

        fileLocations = config.GetDict()
        filepath = fileLocations['Data Folder']

        fileName = monthString + '_' + funcName + '.csv'
        fullName = os.path.join(filepath, fileName)

        userName = encrypt.encrypt(getpass.getuser())
        now=datetime.datetime.now()
        dateString='%02d-%02d-%02d'%(now.year, now.month, now.day)
        timeString= '%02d:%02d:%02d'%(now.hour, now.minute,now.second)

        if not os.path.isfile(fullName):
            data = [[funcName],['Date', 'Time', 'User', 'Version']]
            myFile = open(fullName, 'wb')
            with myFile:
                csvwriter = csv.writer(myFile)
                csvwriter.writerows(data)

        with open(fullName, 'rb') as File:
            reader = csv.reader(File)
            data = list(reader)
        row = [dateString, timeString, userName] + funcData
        data.append(row)

        myFile = open(fullName, 'wb')
        with myFile:
            csvwriter = csv.writer(myFile)
            csvwriter.writerows(data)
    except:
        print "SaveFunctionData failed"

#############################################################################
#NUMBERS
def RoundNumber(number, decPlaces):
    """Rounds numbers and adds ',' thousand seperator. Returns string. -1 rounds to 10, 0 leaves no decimals, 1 has one decimal place"""
    if decPlaces < 0:
        result = int(round(number, decPlaces))
        result = "{:,}".format(result)
    else:
        result = format(float(number), ',.'+str(decPlaces)+'f')
    return result

def RemapList(values, newMin, newMax):
    origMin = min(values)
    origMax = max(values)
    OldRange = (origMax - origMin)
    NewRange = (newMax - newMin)
    newValues = []
    for value in values:
        newValues.append((((value - origMin  ) * NewRange) / OldRange) + newMin)
    return newValues

#############################################################################
#GEOMETRY
def FindMostDistantPointInCurve(obj, resolution = 20):
    """
    Returns the approximately most distant point within a closed curve
    inputs:
        obj (curve): closed planar curves
        resolution (int)[optional]: numbers of sample points in a resolutionXresolution grid
    returns:
        point (point): point furthest from curve
    """
    if rs.IsCurve(obj) == False:
        print "Curves supported only"
        return None
    if rs.IsCurvePlanar(obj) == False:
        print "Curve not planar"
        return None
    if rs.IsCurveClosed(obj) == False:
        print "Curve not closed"
        return None


    rhobj = rs.coercecurve(obj)
    bbox = rhobj.GetBoundingBox(rs.WorldXYPlane())

    minX = bbox.Min[0]
    minY = bbox.Min[1]
    minZ = bbox.Min[2]

    maxX = bbox.Max[0]
    maxY = bbox.Max[1]
    maxZ = bbox.Max[2]

    xVals = []
    yVals = []

    for i in range(resolution):
        xVals.append(i)
        yVals.append(i)

    newXvals = RemapList(xVals, minX, maxX)
    newYvals = RemapList(yVals, minY, maxY)

    furthestPt = None
    furthestDist = 0
    maxDist = 99999
    for xVal in newXvals:
        for yVal in newYvals:
            newPt = rc.Geometry.Point3d(xVal, yVal, minZ)
            result =  rhobj.Contains(newPt, rs.WorldXYPlane())
            if result == rc.Geometry.PointContainment.Inside:
                param = rhobj.ClosestPoint(newPt, maxDist)
                crvPt = rhobj.PointAt(param[1])
                dist = rs.Distance(crvPt, newPt)
                if dist > furthestDist:
                    furthestPt = newPt
                    furthestDist = dist
    if furthestDist == 0:
        return None
    return furthestPt

def FindMostDistantPointOnSrf(obj, resolution = 20):
    """
    Returns the approximately most distant point within a closed curve
    inputs:
        obj (curve): closed planar curves
        resolution (int)[optional]: numbers of sample points in a resolutionXresolution grid
    returns:
        point (point): point furthest from curve
    """
    #HATCH
    if rs.IsHatch(obj):
        rhobj = rs.coercegeometry(obj)
        boundaryCrvs = []
        crvs = rhobj.Get3dCurves(False)
        for crv in crvs:
            boundaryCrvs.append(crv)
        for crv in rhobj.Get3dCurves(True):
            boundaryCrvs.append(crv)
        obj = sc.doc.Objects.AddBrep(rc.Geometry.Brep.CreatePlanarBreps(boundaryCrvs)[0])
        rhobj = rs.coercesurface(obj)
        brep = rs.coercebrep(obj)
        rs.DeleteObject(obj)
    else:
        rhobj = rs.coercesurface(obj)
        brep = rs.coercebrep(obj)
    edges = brep.Edges
    duplEdgs = [edg.DuplicateCurve() for edg in edges]
    duplEdgs = rc.Geometry.Curve.JoinCurves(duplEdgs)

    uDir = rhobj.Domain(0)
    vDir = rhobj.Domain(1)

    uVals = []
    vVals = []
    for i in range(resolution):
        uVals.append(i)
        vVals.append(i)

    newUvals = RemapList(uVals, uDir[0], uDir[1])
    newVvals = RemapList(vVals, vDir[0], vDir[1])

    furthestPt = None
    furthestDist = 0
    maxDist = 999999
    for uVal in newUvals:
        for vVal in newVvals:
            u = uVal
            v = vVal
            srf_pt = rhobj.PointAt(u,v)
            result = rhobj.IsPointOnFace(u,v) != rc.Geometry.PointFaceRelation.Exterior
            if result:
                thisPtsDistances = []
                for eachEdge in duplEdgs:
                    param = eachEdge.ClosestPoint(srf_pt, maxDist)
                    crvPt = eachEdge.PointAt(param[1])
                    thisPtsDistances.append(rs.Distance(crvPt, srf_pt))

                dist = min(thisPtsDistances)
                if dist > furthestDist:
                    furthestPt = srf_pt
                    furthestDist = dist
    if furthestDist == 0:
        return None
    return furthestPt

def FindMostDistantPointRand(obj, resolution = 20):
    """
    Returns the approximately most distant point within a closed curve
    inputs:
        obj (curve): closed planar curves
        resolution (int)[optional]: numbers of sample points in a resolutionXresolution grid
    returns:
        point (point): point furthest from curve
    """
    if rs.IsCurvePlanar(obj) == False:
        print "Curve not planar"
        return None
    if rs.IsCurveClosed(obj) == False:
        print "Curve not closed"
        return None

    rhobj = rs.coercecurve(obj)
    bbox = rhobj.GetBoundingBox(rs.WorldXYPlane())

    minX = bbox.Min[0]
    minY = bbox.Min[1]
    minZ = bbox.Min[2]

    maxX = bbox.Max[0]
    maxY = bbox.Max[1]
    maxZ = bbox.Max[2]

    #########################
    xVals = []
    yVals = []

    random.seed(1)
    for i in range(resolution):
        xVals.append(random.uniform(0,1))
        yVals.append(random.uniform(0,1))

    newXvals = RemapList(xVals, minX, maxX)
    newYvals = RemapList(yVals, minY, maxY)

    furthestPt = None
    furthestDist = 0
    maxDist = 99999
    for xVal in newXvals:
        for yVal in newYvals:
            newPt = rc.Geometry.Point3d(xVal, yVal, minZ)
            result =  rhobj.Contains(newPt, rs.WorldXYPlane())
            if result == rc.Geometry.PointContainment.Inside:
                param = rhobj.ClosestPoint(newPt, maxDist)
                crvPt = rhobj.PointAt(param[1])
                dist = rs.Distance(crvPt, newPt)
                if dist > furthestDist:
                    furthestPt = newPt
                    furthestDist = dist
    if furthestDist == 0:
        return None
    return furthestPt

def IsRectangle(obj):
    """
    Checks if a curve is a rectangle. Must be closed, planar, 4 line segments, all 90 degrees. Uses UnitAngleTolerance
    inputs:
        obj (curve): curve to evaluate
    returns (list):
        [0] (Boolean): If rectangle
        [1] (String): explaination of why it failed
    """
    explaination = ''
    tol = rs.UnitAngleTolerance()
    rhobj = rs.coercecurve(obj)
    if rs.IsCurveClosed(obj):
        if rs.IsCurvePlanar(obj):
            segments = rhobj.DuplicateSegments()
            if len(segments) == 4:
                for segment in segments:
                    if segment.Degree != 1:
                        explaination = "Not all segments are lines"
                        return [False, explaination]
                for i in range(3):
                    angle = rs.Angle2(segments[i], segments[i+1])
                    dist1 = abs(abs(180 - angle[0])-90)
                    dist2 = abs(abs(180 - angle[1])-90)
                    if dist1 > tol or dist2 > tol:
                        explaination = "Angle not 90"
                        return [False, explaination]
                angle = rs.Angle2(segments[-1], segments[0])
                dist1 = abs(abs(180 - angle[0])-90)
                dist2 = abs(abs(180 - angle[1])-90)
                if dist1 > tol or dist2 > tol:
                    explaination = "Final angle not 90"
                    return [False, explaination]
                explaination = "ITS A RECTANGLE"
                return [True, explaination]
            else:
                explaination = "Curve does not have 4 sides"
                return [False, explaination]
        else:
            explaination = "Curve not planar"
            return [False, explaination]
    else:
        explaination = "Curve not closed"
        return [False, explaination]

def GetUphillVectorFromPlane(obj, u = 0, v = 0):
    """Gets the uphill vector from a surface, with optional u, v
    Parameters:
      surface (surface): surface to test
      u (float)[optional]: u parameter
      v (float)[optional]: v parameter
    Returns:
      vector(guid, ...): identifiers of surfaces created on success
    """
    rhobj = rs.coercesurface(obj)
    frame = rhobj.FrameAt(u,v)[1]
    pt0 = rhobj.PointAt(u,v)
    pt1 = rc.Geometry.Point3d.Add(pt0, rc.Geometry.Vector3d(0,0,10))
    projPoint = frame.ClosestPoint(pt1)
    vec = rs.VectorCreate(projPoint, pt0)
    if rs.VectorLength(vec) < rs.UnitAbsoluteTolerance():
        uphillVec = rc.Geometry.Vector3d(0,0,1)
    else:
        uphillVec = rs.VectorUnitize(vec)
    return uphillVec

def GetAllBlockObjectsInPosition(obj):
    """Recursively get all objects from a block (and blocks in blocks)
    inputs:
        obj (block instance)
    returns:
        objs (list guids): Geometry is a copy of the instance geometry
    """
    blockObjs = rs.BlockObjects(rs.BlockInstanceName(obj))
    xform = rs.BlockInstanceXform(obj)
    objList = []
    for eachblockObj in blockObjs:
        if rs.IsBlockInstance(eachblockObj):
            thisBlockObjects = GetAllBlockObjectsInPosition(eachblockObj)
            for eachObject in thisBlockObjects:
                transformedObj = rs.TransformObject(eachObject, xform, False)
                objList.append(transformedObj)
        else:
            transformedObj = rs.TransformObject(eachblockObj, xform, True)
            objList.append(transformedObj)
    return objList

#############################################################################
#STRINGS
def StringPlusOne(word):
    """Adds one to the last numbers in a string.
    Parameters:
      word (str): String to process.
    Returns:
      word(str): String thats been iterated
    """
    try:
        if word[-2] == ' ' or word[-2] == '-' or word[-2] == '_' or word[-2].isdigit():
            if word[-1] in letters:
                s = word[-1]
                word = word[:-1]
                s=letters[(letters.index(s)+1)%len(letters)]
                word += s
                return word

        suffixNumber = ''
        splitIndex = 0
        for i, l in enumerate(word[::-1]):
            try: #check if suffix is number
                int(l)
                suffixNumber += l
            except:
                splitIndex = i
                break
        suffixNumber = suffixNumber[::-1]
        if len(suffixNumber) < 1:
            return word
        newNum = int(suffixNumber)+1
        finalNum = (len(suffixNumber)-len(str(newNum)))*'0' + str(newNum)
        return word[:len(word)-splitIndex] + finalNum

        s='a'
        if s in letters:
            s=letters[(letters.index(s)+1)%len(letters)]
    except:
        print "StringPlusOne Error"
        return None

def UpdateString(word):
    try:
        prefix = word[:6]
        int(prefix)
        curDate = GetDatePrefix()
        if prefix == curDate:
            return StringPlusOne(word)
        else:
            return  curDate + word[6:]
    except:
        return StringPlusOne(word)

#############################################################################
#COLOR
def GetRandomColor():
    """
    Returns tuple in format (r,g,b) with range 100-230
    """
    r = random.randint(100,230)
    g = random.randint(100,230)
    b = random.randint(100,230)
    return (r, g, b)

def StepColor(prevColor):
    maxStepSize = 40
    minStepSize = 30

    rF = random.randint(minStepSize, maxStepSize)
    gF = random.randint(minStepSize, maxStepSize)
    bF = random.randint(minStepSize, maxStepSize)

    if random.randint(0,1):
        rF *= -1
    if random.randint(0,1):
        gF *= -1
    if random.randint(0,1):
        bF *= -1

    newR = prevColor.R + rF
    if newR <100:
        newR = 100 + abs(rF)
    if newR >255:
        newR = 255 - (abs(rF))

    newG = prevColor.G + gF
    if newG <100:
        newG = 100 + abs(gF)
    if newG >255:
        newG = 255 - (abs(gF))

    newB = prevColor.B + bF
    if newB <100:
        newB = 100 + abs(bF)
    if newB >255:
        newB = 255 - (abs(bF))

    newColor = [newR, newG, newB]
    return newColor

if __name__ == "__main__":
    #print IsSavedInProjectFolder()
    test = '181008_option_01-A'
    print test
    print StringPlusOne(test)
    #obj = rs.GetObject()
    #print GetUphillVectorFromPlane(obj)
    pass
