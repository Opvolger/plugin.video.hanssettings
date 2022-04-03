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
import re
import time
import json
from datetime import datetime
if (sys.version_info[0] == 3):
    # For Python 3.0 and later
    from urllib.request import urlopen, Request, HTTPError
else:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError

PY3 = False

# hierin geen logica van kodi, zodat dit los testbaar is.


class HansSettings:
    #
    # Init
    #
    def __init__(self):
        self.PY3 = sys.version_info[0] == 3

    @staticmethod
    def get_soort(content_type):
        if content_type == 'audio':
            return 'radio'
        return 'tv'

    def get_data_from_github_file(self, github_file):
        url = 'https://raw.githubusercontent.com/Opvolger/kanalenlijst_hans_sync/master/e2_hanssettings_kabelNL/'
        req = Request(url + github_file)
        req.add_header(
            'User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
        req.add_header('Content-Type', 'text/html; charset=utf-8')

        for attempt in range(10):
            try:
                response = urlopen(req)
            except HTTPError as err:
                if err.code == 404:
                    return '' # kan voorkomen als de file niet aanwezig is op de github repo
            except:
                continue
            else:
                break
        else:
            # we failed all the attempts - deal with the consequences.
            response = urlopen(req)
        filedata = response.read()
        if (self.PY3):
            filedata = filedata.decode('utf-8', 'backslashreplace')
        response.close()
        return filedata

    def get_data_from_github_file_bouquets(self, content_type):
        # ophalen van bouquet met daarin alle stream files.
        return self.get_data_from_github_file('bouquets.%s' % self.get_soort(content_type))

    def get_stream_files_from_bouguet(self, filedata, content_type):
        # het uitlezen van de githubfiles met streams erin (deze staan in de bouquets.* file)
        # deze los aanroep is gemaakt om caching mogelikj te maken.
        streamfiles = re.findall(
            '(userbouquet.stream_.*.%s)' % self.get_soort(content_type), filedata)
        return streamfiles

    def get_version_from_bouquet(self, filedata, content_type):
        # ophalen van de versie. zodat je de caching niet hoeft te versen.
        # niet meer ingebruik, nadat ik een standaard lin heb gebruikt voor caching.
        versions = re.findall('userbouquet[.]gemaakt_(.*).%s' % self.get_soort(content_type), filedata)
        return versions[0]

    def get_name(self, filedata, filename):
        try:
            # ophalen naam van de filestream bestand
            names = re.findall("^#NAME (.*)", filedata)
            return names[0]
        except:
            return filename

    def get_items_subfolder(self, filedata, counter):
        # we halen de data net zo op als in get_items
        # waar we willen alleen de sub-folder met een bepaalde waarde (de counter)
        items = self.get_items(filedata)
        for item in items:
            if (item['subfolder'] and item['counter'] == counter):
                return item
        return

    def get_items(self, filedata):
        # we delen alle data in alle "blokken".
        blokken = re.compile("#SERVICE 1:64:[a-z0-9]*[:0]*").split(filedata)
        itemlist = list()
        i = 0
        for blok in blokken:
            # elk blok wat een sub-folder is begint met "DESCRIPTION"
            # als dit dus niet het geval is, dan zijn er dus direct items.
            if blok.find("#DESCRIPTION ++") == -1:
                # we hebben geen subfolder alleen maar NAME of NAME met streams
                itemlist.append(
                    {'subfolder': False, 'streams': self.get_streams(blok)})
            else:
                # we hebben een sub folder met streams
                # we nummeren alle sub-folders, zodat we deze data weer op de zelfde manier kunnen ophalen.
                i = i + 1
                itemlist.append({'subfolder': True, 'streams': self.get_streams(
                    blok), 'label': self.get_desciptionfolder(blok), 'counter': str(i)})
        return itemlist

    def get_desciptionfolder(self, data):
        # hier halen we de naam van het blok op.        
        matches = re.findall("#DESCRIPTION ([+][+].*[+][+])", data)
        return matches[0]

    def get_streams(self, data):
        # alle data is gescheiden met :, dus een echte ":" is vertaalt naar "%3a"
        # we zoeken op deze regular expression, zodat we de naam en url hebben ":" gescheiden.
        streamsandnames = re.findall("([a-z]*%3a.*:.*)", data)
        itemlist = list()
        for streamandname in streamsandnames:
            # we splitten de regular expression data op : (naam en url)
            streamadres, streamname = streamandname.split(':')
            url = streamadres.replace('%3a', ':')
            
            streamheader = None
            if "#" in streamadres:
                streamadres, streamheader = streamadres.split('#')
                url = streamadres.replace('%3a', ':')
                stream_play = '%s|%s' % (url,streamheader)
            else:
                stream_play = '%s|User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36' % url
            item = {'label': streamname,
                    'header': streamheader,
                    'stream': stream_play,
                    'url': url}
            itemlist.append(item)
        return itemlist
