'''
    resources.lib.hanssettings
    ~~~~~~~~~~~~~~~~~

    An XBMC addon for watching HansSettings
   
    :license: GPLv3, see LICENSE.txt for more details.

    Uitzendinggemist (NPO) = Made by Bas Magre (Opvolger)    
    based on: https://github.com/jbeluch/plugin.video.documentary.net

'''
import urllib2 ,re ,time ,json
from datetime import datetime

class HansSettings:
        #
        # Init
        #
        #def __init__( self):

        def get_overzicht(self):        
            req = urllib2.Request('https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/bouquets.tv')
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            response = urllib2.urlopen(req)
            linkdata=response.read()
            response.close()
            print(linkdata)
            itemlist = list()
            streamfiles = re.findall("(userbouquet.stream_.*.tv)", linkdata)
            for streamfile in streamfiles:
                hanssettingsitem = {
                    'label': streamfile,
                    'filename': streamfile
                }
                itemlist.append(hanssettingsitem)                
            return itemlist #sorted(itemlist, key=lambda x: x['label'], reverse=False)

        def get_items(self, file):
            req = urllib2.Request('https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/'+file)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            response = urllib2.urlopen(req)
            linkdata=response.read()
            response.close()
            # print(linkdata)
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
