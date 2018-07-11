import rhinoscriptsyntax as rs

def ExportAndLinkBlock():
    name = rs.ListBox(rs.BlockNames(True))
    if name is None: return
    
    path = rs.SaveFileName('Title', "Rhino 6 3D Models|.3dm||")
    if path is None: return
    
    try:
        rs.Command("_-BlockManager e " + '"' + name + '" ' + path + ' Enter', False)
        rs.Command("_-BlockManager _Properties " + '"' + name + '"' + " _UpdateType i " + path + " _UpdateType _Linked _Enter _Enter", False)
    except:
        pass
if __name__ == "__main__":
    ExportAndLinkBlock()