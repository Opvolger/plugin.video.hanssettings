'''
    resources.lib.hanssettings
    ~~~~~~~~~~~~~~~~~

    An XBMC addon for watching HansSettings
   
    :license: GPLv3, see LICENSE.txt for more details.

    Uitzendinggemist (NPO) = Made by Bas Magre (Opvolger)    
    based on: https://github.com/jbeluch/plugin.video.documentary.net

'''
import sys
import os
import re ,time ,json
from datetime import datetime
if (sys.version_info[0] == 3):
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
else:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request

PY3 = False

# hierin geen logica van kodi, zodat dit los testbaar is.

class HansSettings:
        #
        # Init
        #
        def __init__(self):
            self.PY3 = sys.version_info[0] == 3

        def get_datafromfilegithub(self, file):    
            url = 'https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/'
            req = Request(url + file)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            req.add_header('Content-Type', 'text/html; charset=utf-8')
            response = urlopen(req)
            linkdata=response.read()
            if (self.PY3):
                linkdata=linkdata.decode('utf-8', 'backslashreplace')
            response.close()
            return linkdata

        def get_dataoverzicht(self):
            return self.get_datafromfilegithub('bouquets.tv')

        def get_overzicht(self, linkdata):
            streamfiles = re.findall("(userbouquet.stream_.*.tv)", linkdata)               
            return streamfiles

        def get_version(self, linkdata):
            versions = re.findall("userbouquet[.]gemaakt_(.*).tv", linkdata)               
            return versions[0]

        def get_name(self, linkdata, filename):
            try:
                names = re.findall("^#NAME (.*)", linkdata)
                return names[0]
            except:
                return filename

        def get_items_subfolder(self, linkdata, counter):
            items = self.get_items(linkdata)
            for item in items:
                if (item['subfolder'] and item['counter'] == counter):
                    return item
            return

        def get_items(self, linkdata):
            blokken = re.compile("#SERVICE 1:64:[a-z0-9]*[:0]*").split(linkdata)
            itemlist = list()
            i = 0
            for blok in blokken:
                if blok.find("#DESCRIPTION ++") == -1:
                    # we hebben geen subfolder alleen maar NAME of NAME met streams
                    itemlist.append({'subfolder': False, 'streams': self.get_streams(blok)})
                else:
                    # we hebben een sub folder met streams
                    i = i + 1
                    itemlist.append({'subfolder': True, 'streams': self.get_streams(blok), 'label': self.get_desciptionfolder(blok), 'counter': str(i)})
            return itemlist

        def get_desciptionfolder(self, data):
            matches = re.findall("#DESCRIPTION ([+][+].*[+][+])", data)
            return matches[0]

        def get_streams(self, data):
            streamsandnames = re.findall("([a-z]*%3a.*:.*)", data)
            itemlist = list()
            for streamandname in streamsandnames:
                streamadres,streamname = streamandname.split(':')
                item = { 'label': streamname, 'stream': streamadres.replace('%3a',':')}
                itemlist.append(item)
            return itemlist
