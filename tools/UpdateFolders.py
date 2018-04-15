import shutil
import os
import distutils.dir_util

def UpdateFolders(source, target):
    if not os.path.isdir(source):
        print "Source folder not found"
        return
    if not os.path.isdir(target):
        print "Target folder not found"
        return
    srcFiles = os.listdir(source)
    
    for file in srcFiles:
        try:
            fullSourceName = os.path.join(source, file)
            fullTargetName = os.path.join(target, file)
            if os.path.isdir(fullSourceName):
                if not os.path.isdir(fullTargetName):
                    os.makedirs(fullTargetName)
                else:
                    shutil.rmtree(fullTargetName)
                    os.makedirs(fullTargetName)
                distutils.dir_util.copy_tree(fullSourceName, fullTargetName)
        except:
            print "One file failed"
            
    print "Loaded " + str(os.path.basename(os.path.normpath(target)))

source = r'C:\Users\Tim\Desktop\temp\orig'
target = r'C:\Users\Tim\Desktop\temp\target'

print target
UpdateFolders(source,target)