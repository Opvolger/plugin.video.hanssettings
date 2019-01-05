'''
    Hans Settings
    ~~~~~~~

    An XBMC addon for watching hanssettings 
    :license: GPLv3, see LICENSE.txt for more details.
    
'''
import sys
if (sys.version_info[0] == 3):
    # For Python 3.0 and later
    from urllib.parse import urlencode
    from urllib.parse import parse_qsl
    #File "*****\script.common.plugin.cache\default.py", line 30, in run
    #  sys.path = [settings.getAddonInfo('path').decode('utf-8') + "/lib"] + sys.path
    #  AttributeError: 'str' object has no attribute 'decode'    
    import storageserverdummy as StorageServer    
else:
    # Fall back to Python 2's urllib2
    from urllib import urlencode
    from urlparse import parse_qsl
    try:
        import StorageServer
    except:
        import storageserverdummy as StorageServer    

import resources.lib.hanssettings
import time
import xbmcplugin, xbmcgui, xbmcaddon

PLUGIN_NAME = 'hanssettings'
PLUGIN_ID = 'plugin.video.hanssettings'

_hanssettings = resources.lib.hanssettings.HansSettings()
_url = sys.argv[0]
_handle = int(sys.argv[1])
_cache = StorageServer.StorageServer(PLUGIN_ID, 24) # (Your plugin name, Cache time in hours)
_addon = xbmcaddon.Addon()

# In deze file heb ik alle logica van kodi zitten.
# hier worden alle files ook gecached, want dat is een kodi addon.

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_categories(content_type):
    soort = get_soort(content_type)
    githubfiles = _cache.cacheFunction(_hanssettings.get_dataoverzicht, soort)
    return _hanssettings.get_overzicht(githubfiles, soort)

def get_items(streamfile):
    streamsdatafile = _cache.cacheFunction(_hanssettings.get_datafromfilegithub,streamfile)
    return _hanssettings.get_items(streamsdatafile)

def list_categories(content_type):
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(32004))
    xbmcplugin.setContent(_handle, 'files')
    i = 0
    categories = get_categories(content_type)
    categoriesLength = len(categories)
    progress = xbmcgui.DialogProgress()
    progress.create(_addon.getLocalizedString(32002), _addon.getLocalizedString(32001))
    for category in categories:
        i = i + 1
        progressText = _addon.getLocalizedString(32003) % (i, categoriesLength)
        progress.update( 100 / categoriesLength * i, "", progressText)
        if progress.iscanceled():
            break
        datafile = _cache.cacheFunction(_hanssettings.get_datafromfilegithub,category)
        list_item = xbmcgui.ListItem(label=_hanssettings.get_name(datafile, category))
        list_item.setInfo(get_context(content_type), {'title': _hanssettings.get_name(datafile, category),
                                    'mediatype': get_context(content_type)})
        url = get_url(action='listing', category=category, content_type=content_type)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    progress.close()
    del progress
    xbmcplugin.endOfDirectory(_handle)

def add_playable_listitem(item, content_type):
    list_item = xbmcgui.ListItem(label=item['label'])
    list_item.setInfo(get_context(content_type), {'title': item['label'], 'mediatype': get_context(content_type)})
    list_item.setProperty('IsPlayable', 'true')
    url = get_url(action='play', item=item['stream'], content_type=content_type)
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

def list_items_and_subfolder(category, content_type):
    datafile = _cache.cacheFunction(_hanssettings.get_datafromfilegithub,category)
    xbmcplugin.setPluginCategory(_handle, _hanssettings.get_name(datafile, category))
    xbmcplugin.setContent(_handle, 'files')
    for item in get_items(category):
        if (item['subfolder']):
            list_item = xbmcgui.ListItem(label=item['label'])
            list_item.setInfo(get_context(content_type), {'title': item['label'], 'mediatype': get_context(content_type)})
            url = get_url(action='subfolder', category=category, counter=item['counter'], content_type=content_type)
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        else:
            for stream in item['streams']:
                add_playable_listitem(stream, content_type)
    xbmcplugin.endOfDirectory(_handle)

def list_subfolder(category, counter, content_type):
    datafile = _cache.cacheFunction(_hanssettings.get_datafromfilegithub,category)
    item = _hanssettings.get_items_subfolder(datafile, counter)
    xbmcplugin.setPluginCategory(_handle, item['label'])
    xbmcplugin.setContent(_handle, 'files')
    for stream in item['streams']:
        add_playable_listitem(stream, content_type)
    xbmcplugin.endOfDirectory(_handle)

def play_item(path):
    if (path.find('?#User-Agent') > -1):
        path = path.partition('?#User-Agent')[0] + '|User-Agent'+path.partition('?#User-Agent')[2]
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def get_context(content_type):
    if content_type == 'audio':
        return 'music'
    return 'video'

def get_soort(content_type):
    if content_type == 'audio':
        return 'radio'
    return 'tv'

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    content_type = params['content_type']
    xbmc.log('content_type: ' + content_type, xbmc.LOGNOTICE)
    if 'action' in params:
        if params['action'] == 'listing':
            list_items_and_subfolder(params['category'], content_type)
        elif params['action'] == 'subfolder':
            list_subfolder(params['category'], params['counter'], content_type)
        elif params['action'] == 'play':
            play_item(params['item'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters
        list_categories(content_type)


if __name__ == '__main__':
    router(sys.argv[2][1:])
