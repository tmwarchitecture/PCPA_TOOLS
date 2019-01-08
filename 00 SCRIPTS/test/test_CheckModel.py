import rhinoscriptsyntax as rs


def main():
    print "Checking model"
    
    #Check model units
    if rs.UnitSystem() != 8:
        rs.MessageBox("Your model is not in inches.", 16)
        print "Unit warning"
    
    #Check bad objects
    rs.Command('-_SelBadObjects ')
    objs = rs.SelectedObjects()
    if len(objs)>0:
        message = "You have {} bad objects. Use SelBadObjects to delete them.".format(len(objs))
        rs.MessageBox(message, 16)
    rs.UnselectAllObjects()
    
    #SelDup
    rs.Command('-_SelDup ')
    objs = rs.SelectedObjects()
    if len(objs)>0:
        message = "You have {} duplicate objects. Use SelDup to delete them.".format(len(objs))
        rs.MessageBox(message, 16)
    rs.UnselectAllObjects()
    
    #SelSmall
    rs.Command('-_SelSmall .01 ')
    objs = rs.SelectedObjects()
    if len(objs)>0:
        message = "You have {} tiny objects. Use SelSmall to delete them.".format(len(objs))
        rs.MessageBox(message, 16)
    rs.UnselectAllObjects()
    
    #Far away objects
    
    #Check layer standards
    

if __name__ == "__main__":
    main()