'''
    Hans Settings
    ~~~~~~~

    An XBMC addon for watching hanssettings 
    :license: GPLv3, see LICENSE.txt for more details.
    
'''
from xbmcswift2 import Plugin, SortMethod
import resources.lib.hanssettings
import time
import xbmcplugin

PLUGIN_NAME = 'hanssettings'
PLUGIN_ID = 'plugin.video.hanssettings'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)

hanssettings = resources.lib.hanssettings.HansSettings()
subtitle = plugin.get_setting( "subtitle", bool )

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(PLUGIN_ID, 10) # (Your plugin name, Cache time in hours)

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
    return show_items(cache.cacheFunction(hanssettings.get_items, file))

@plugin.route('/lectures/<stream>/')
def play_lecture(stream):
	plugin.set_resolved_url(stream)

def show_items(opgehaaldeitemsclass):
    '''Lists playable videos for a given category url.'''
    items = [{
        'path': plugin.url_for('play_lecture', stream=item['stream']),
        'label': item['label'],
        'is_playable': True
    } for item in opgehaaldeitemsclass]
    return plugin.finish(items,sort_methods=[SortMethod.LABEL])

if __name__ == '__main__':
    plugin.run()
