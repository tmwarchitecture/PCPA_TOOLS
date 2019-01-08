import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import rhinoscriptsyntax as rs

def main():
    obj = rs.GetObject()
    
    #address_book = ['twilliams@pcparch.com', 'wwang@pcparch.com', 'SRestrepo@pcparch.com', 'RSteenblik@pcparch.com']
    address_book = ['twilliams@pcparch.com']
    msg = MIMEMultipart()    
    sender = 'test@pcparch.com'
    subject = "Email sent from Rhino"
    body = '<html>'
    body += "<p>Here are the points from a polyline: \n" + str([(pt.X, pt.Y, pt.Z) for pt in rs.CurveEditPoints(obj)]) + '</p> '
    
    #body += ' <a href="file://datafiles/reference/22_REACH">Link</a>'
    
    body+= '</html>'
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    text=msg.as_string()
    #print text
    # Send the message via our SMTP server
    s = smtplib.SMTP('pny-ex.pelli-ny.local')
    s.sendmail(sender,address_book, text)
    s.quit()        

main()