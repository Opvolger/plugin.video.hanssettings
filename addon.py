'''
    Hans Settings
    ~~~~~~~

    An XBMC addon for watching hanssettings 
    :license: GPLv3, see LICENSE.txt for more details.
    
'''
from xbmcswift2 import Plugin, SortMethod
import resources.lib.hanssettings
import time
import xbmcplugin, xbmcgui

PLUGIN_NAME = 'hanssettings'
PLUGIN_ID = 'plugin.video.hanssettings'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)

hanssettings = resources.lib.hanssettings.HansSettings()
addon_handle = int(sys.argv[1])

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(PLUGIN_ID, 10) # (Your plugin name, Cache time in hours)
buffer = 'leeg'


@plugin.route('/')
def index():
    ##main, alle shows
    items = [{
        'path': plugin.url_for('show_streams', file=item['filename']),
        'label': item['label']
    } for item in cache.cacheFunction(hanssettings.get_overzicht)]    
    return plugin.finish(items)

@plugin.route('/streams/<file>/')
def show_streams(file):
    return show_items(hanssettings.get_items(file), file)

@plugin.route('/lectures/<fileandstream>')
def play_lecture(fileandstream):
    filename,stream = fileandstream.split('-:-:-')
    items = hanssettings.get_items(filename)
    for item in items:
        if (item['stream'] == stream):
            listitem = xbmcgui.ListItem(item['label'])
            listitem.setInfo('video', {'Title': item['label']})
            xbmc.Player().play(stream, listitem)

def show_items(opgehaaldeitemsclass, file):
    items = list()
    for item in opgehaaldeitemsclass:
        path = __getpath(item, file)
        xbmc.log(path, xbmc.LOGNOTICE)
        items.append({
            'path': path,
            'label': item['label'],
            'is_playable': True
            })
    return plugin.finish(items,sort_methods=[SortMethod.LABEL])

def __getpath(item, file):
    if (item['stream'].find('?#User-Agent') > -1):
        return item['stream'].partition('?#User-Agent')[0] + '|Referer='+item['stream'].replace('?#User-Agent','&User-Agent')
    return plugin.url_for('play_lecture', fileandstream=file + '-:-:-' + item['stream'])
if __name__ == '__main__':
    plugin.run()
