import Rhino
import scriptcontext

def ExportAsObj():
    
    filepath = r"C:\Users\Tim\Desktop\temp\xa.obj"
    
    
    
    write_options = Rhino.FileIO.FileWriteOptions()
    write_options.WriteSelectedObjectsOnly = True
    
    obj_options = Rhino.FileIO.FileObjWriteOptions(write_options)
    obj_options.UseSimpleDialog = True

    rc = Rhino.FileIO.FileObj.Write(filepath, scriptcontext.doc.ActiveDoc, obj_options)
    print ""
    if rc == Rhino.PlugIns.WriteFileResult.Success:
        print "Success, file saved:", filepath
    else:
        print "Error saving file:", filepath

ExportAsObj()