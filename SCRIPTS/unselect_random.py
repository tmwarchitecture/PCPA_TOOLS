import rhinoscriptsyntax as rs
import scriptcontext as sc
import random
import utils

__author__ = 'Tim Williams'
__version__ = "2.0.1"

def RandomUnselect():
    try:
        ids = rs.GetObjects("Select objects to unselect", preselect = True)
        if not ids: return


        if len(ids) == 1: return

        rs.SelectObjects(ids)

        if sc.sticky.has_key("RandomUnselect_percent"):
            percent_default = sc.sticky["RandomUnselect_percent"]
        else:
            percent_default = 50

        percent = rs.GetInteger("Percent to deselect", percent_default, 1, 99)
        if not percent: return
        objs = random.sample(ids, int(percent*len(ids)/100))

        rs.UnselectObjects(objs)

        sc.sticky["RandomUnselect_percent"] = percent
        return True
    except :
        return False

if __name__=="__main__":
    result = RandomUnselect()
    if result:
        utils.SaveToAnalytics('legacy_random unselect')
