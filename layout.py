import rhinoscriptsyntax as rs


def AddLayout():
    size = '11x17 '
    width = '17 '
    height = '11 '
    rs.Command('-_Layout ' + size + width + height + '0 ', False)

def BatchPrintLayouts():
    print "BatchPrintLayouts WIP"

if __name__ == "__main__":
    AddLayout()