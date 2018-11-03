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

@plugin.route('/lectures/<stream>')
def play_lecture(stream):
    xbmc.log(buffer, xbmc.LOGNOTICE)
    label = 'Test'
    listitem = xbmcgui.ListItem(label)
    listitem.setInfo('video', {'Title': label})
    xbmc.Player().play(stream, listitem)
    # for item in buffer:
    #     xbmc.log('i :', item['i'], xbmc.LOGNOTICE)
    #     xbmc.log('i2 :', i, xbmc.LOGNOTICE)
    #     if (item['i'] == i):
    #         listitem = xbmcgui.ListItem(item['label'])
    #         listitem.setInfo('video', {'Title': item['label']})
    #         xbmc.Player().play(item['stream'], listitem)

def show_items(opgehaaldeitemsclass, file):
    buffer = list()
    buffer = opgehaaldeitemsclass
    items = list()
    for item in opgehaaldeitemsclass:
        path = __getpath(item)
        xbmc.log(path, xbmc.LOGNOTICE)
        items.append({
            'path': path,
            'label': item['label'],
            'is_playable': True
            })
    for item in buffer:
        xbmc.log('i : i', xbmc.LOGNOTICE)
    return plugin.finish(items,sort_methods=[SortMethod.LABEL])

def __getpath(item):
    if (item['stream'].find('?#User-Agent') > -1):
        return item['stream'].partition('?#User-Agent')[0] + '|Referer='+item['stream'].replace('?#User-Agent','&User-Agent')
    return plugin.url_for('play_lecture', stream=item['stream'])

if __name__ == '__main__':
    plugin.run()
