'''
    resources.lib.hanssettings
    ~~~~~~~~~~~~~~~~~

    An XBMC addon for watching HansSettings
   
    :license: GPLv3, see LICENSE.txt for more details.

    Uitzendinggemist (NPO) = Made by Bas Magre (Opvolger)    
    based on: https://github.com/jbeluch/plugin.video.documentary.net

'''
try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request    
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request    

import re ,time ,json
from datetime import datetime
PY3 = False

class HansSettings:
        #
        # Init
        #
        def __init__(self, py3):
            self.PY3 = py3


        def get_dataoverzicht(self):
            return self.get_datafromurl('https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/bouquets.tv')

        def get_datafromfilegithub(self, file):
            return self.get_datafromurl('https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/' + file)
        
        def get_datafromurl(self, url):
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            req.add_header('Content-Type', 'text/html; charset=utf-8')
            response = urlopen(req)
            if (self.PY3):
                linkdata=response.read().decode('utf-8')
            else:
                linkdata=response.read()
            response.close()
            return linkdata

        def get_overzicht(self, linkdata):
            itemlist = list()
            streamfiles = re.findall("(userbouquet.stream_.*.tv)", linkdata)               
            return streamfiles #sorted(itemlist, key=lambda x: x['label'], reverse=False)

        def get_name(self, linkdata, filename):
            try:
                names = re.findall("^#NAME (.*)", linkdata)
                return names[0]
            except:
                return filename

        def get_items(self, linkdata):
            streamsandnames = re.findall("([a-z]*%3a.*:.*)", linkdata)
            # print(streamsandnames)
            itemlist = list()
            i = 0
            for streamandname in streamsandnames:
                i = i + 1
                streamadres,streamname = streamandname.split(':')
                item = { 'label': streamname, 'stream': streamadres.replace('%3a',':'), 'i': i}
                itemlist.append(item)
            return itemlist
