import rhinoscriptsyntax as rs
import csv
import Rhino
import imp
#csv = imp.load_source('csv', r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\dependencies\csv.py')
import scriptcontext as sc

PCPA_Layers = r'C:\Users\Tim\Desktop\temp\template\PCPA LAYERS.csv'

layNumColumn = 0
nameColumn = 1
colorColumn = 2
materialColumn = 3
linetypeColumn = 4
printcolorColumn = 5
printwidthColumn = 6

#sc.doc.Materials.FindIndex(
#print "HERE: " + str(Rhino.DocObjects.Tables.MaterialTable.CurrentMaterialIndex)

def GetChildNumbers(parentNum):
    if parentNum%1000 == 0:
        print "Thousand series"
        return range(parentNum+1, parentNum+1000)
    elif parentNum%100 == 0:
        print "Hundred Series"
        return range(parentNum+1, parentNum+100)
    elif parentNum%10 == 0:
        print "Ten Series"
        #return range(parentNum, parentNum+10)
    else:
        print "One layer"
        return [parentNum]

def GetLayerData(fileName):
    
    with open(fileName, 'rb') as f:
        reader = csv.reader(f)
        layerData = list(reader)
    return layerData

def AddLayers(layerData, layerNumbers):
    #Delete non-number layers
    for i, row in enumerate(layerData):
        try:
            int(row[layNumColumn])
        except:
            del layerData[i]
    
    
    def translateColor(dashColor):
        if len(dashColor) < 1:
            return
        values = dashColor.split("-")
        finalValues = []
        for value in values:
            finalValues.append(int(value))
        return finalValues
    
    for eachRow in layerData:
        try:
            int(eachRow[layNumColumn])
            for eachNum in layerNumbers:
                if int(eachRow[layNumColumn]) == int(eachNum): #if this row is a requested number
                    name = eachRow[nameColumn]
                    color = translateColor(eachRow[colorColumn])
                    material = eachRow[materialColumn]
                    linetype = eachRow[linetypeColumn]
                    printcolor = translateColor(eachRow[printcolorColumn])
                    printwidth = eachRow[printwidthColumn]
                    try:
                        float(eachRow[printwidthColumn])
                    except:
                        printwidth = 0
                    
                    print "Found layer num {} in CSV file".format(eachNum)
                    
                    newLayer = rs.AddLayer(eachRow[nameColumn], color)
                    rs.LayerLinetype(newLayer, linetype)
                    rs.LayerPrintColor(newLayer, printcolor)
                    rs.LayerPrintWidth(newLayer, float(printwidth))
                    #rs.AddMaterialToLayer(newLayer)
                    break
        except:
            print "Row failed"
            pass

def test():
    print "Test finished"

def main():
    rs.EnableRedraw(False)
    layerNumRequested = rs.GetInteger("Enter layer number to add to the document", minimum = 1)
    if layerNumRequested is None: return
    layerData = GetLayerData(PCPA_Layers)
    layerNums = GetChildNumbers(layerNumRequested)
    AddLayers(layerData, layerNums)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()
    