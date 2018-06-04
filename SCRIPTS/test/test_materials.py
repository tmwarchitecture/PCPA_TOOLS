import rhinoscriptsyntax as rs
import os

def MaterialToLayer(matName, layer):
    def loadMatFromPath(path):
        if os.path.isfile(path):
            rdk = rs.GetPlugInObject("Renderer Development Kit")
            rc = rdk.ContentLoadFromFile(path)
            return rc
        else: return None
    
    def ApplyMaterialToLayer(material, layer):
        matName = '"' + str(material) + '"'
        layName = '"' + layer + '"'
        rs.Command("-_RenderAssignMaterialToLayer " + str(matName) + " " + str(layName) + " ", False)
    
    def getMaterialNames():
        rdk = rs.GetPlugInObject("Renderer Development Kit")
        rdkALL = rdk.FactoryList()
        arrMatIDList = rdk.ContentList("material") 
        arrMatNames = []
        for i in range(len(arrMatIDList)):
            arrMatNames.append(rdk.ContentInstanceName(arrMatIDList[i]))
        return arrMatNames
    
    def IsMaterial(materialName):
        matNames = getMaterialNames()
        for name in matNames:
            if name == materialName:
                return True
        return False
    
    def ForceMaterialToLayer(materialName, mylayer):
        """
        Applies material by name to layer. If no layer found, it is imported.
            materialName: str
            mylayer: str
        """
        materialNameFull = materialName + '.rmtl'
        dir = r'C:\Users\Tim\Desktop\temp\mats'
        matpath = os.path.join(dir, materialNameFull)
        
        if IsMaterial(materialName):
            ApplyMaterialToLayer(materialName, mylayer)
        else:
            result = loadMatFromPath(matpath)
            if result is None:
                print "Material {} not found".format(materialName)
            else:
                ApplyMaterialToLayer(materialName, mylayer)
    
    ForceMaterialToLayer(matName, layer)

if __name__ == "__main__":
    MaterialToLayer('Chicken', rs.AddLayer())