import urllib2 as web

r=web.urlopen('https://raw.githubusercontent.com/tmwarchitecture/PCPA_TOOLS/master/00%20SCRIPTS/config.py')
print r.read()