import datetime
import rhinoscriptsyntax as rs

def timeTilHappyHour():
    now     = datetime.datetime.now()
    hour = str(datetime.time(now.hour, now.minute, now.second))
    
    list = hour.split(":")
    if (17-int(list[0])<0):
        rs.MessageBox("ITS HAPPY HOUR!!!!! \nHead to the bar for a drink!")
    else:
        rs.MessageBox( "Only {} hours, {} minutes, and {} seconds, until happy hour!".format(17-int(list[0]), 59-int(list[1]), 60-int(list[2])))

timeTilHappyHour()