'''
    Hans Settings
    ~~~~~~~

    An XBMC addon for watching hanssettings 
    :license: GPLv3, see LICENSE.txt for more details.
    
'''
import sys
try:
    # For Python 3.0 and later
    from urllib.parse import urlencode
    from urllib.parse import parse_qsl
    #File "*****\script.common.plugin.cache\default.py", line 30, in run
    #  sys.path = [settings.getAddonInfo('path').decode('utf-8') + "/lib"] + sys.path
    #  AttributeError: 'str' object has no attribute 'decode'    
    import storageserverdummy as StorageServer

except ImportError:
    # Fall back to Python 2's urllib2
    from urllib import urlencode
    from urlparse import parse_qsl
    try:
        import StorageServer
    except:
        import storageserverdummy as StorageServer

import resources.lib.hanssettings
import time
import xbmcplugin, xbmcgui

PLUGIN_NAME = 'hanssettings'
PLUGIN_ID = 'plugin.video.hanssettings'

hanssettings = resources.lib.hanssettings.HansSettings(sys.version_info[0] == 3)
_url = sys.argv[0]
_handle = int(sys.argv[1])

cache = StorageServer.StorageServer(PLUGIN_ID, 10) # (Your plugin name, Cache time in hours)

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_categories():
    githubfiles = cache.cacheFunction(hanssettings.get_dataoverzicht)
    return hanssettings.get_overzicht(githubfiles)

def get_videos(streamfile):
    streamsdatafile = cache.cacheFunction(hanssettings.get_datafromfilegithub,streamfile)
    return hanssettings.get_items(streamsdatafile)

def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Hans Settings Streams')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    for category in get_categories():
        datafile = cache.cacheFunction(hanssettings.get_datafromfilegithub,category)
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=hanssettings.get_name(datafile, category))
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        # list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                   'icon': VIDEOS[category][0]['thumb'],
        #                   'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.

        list_item.setInfo('video', {'title': hanssettings.get_name(datafile, category),
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def add_playable_listitem(video):
    list_item = xbmcgui.ListItem(label=video['label'])
    list_item.setInfo('video', {'title': video['label'],
                # 'genre': video['genre'],
                'mediatype': 'video'})
    list_item.setProperty('IsPlayable', 'true')
    url = get_url(action='play', video=video['stream'])
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

def list_videos_and_subfolder(category):
    """
    Create the list of playable videos in the Kodi interface.
    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    datafile = cache.cacheFunction(hanssettings.get_datafromfilegithub,category)
    xbmcplugin.setPluginCategory(_handle, hanssettings.get_name(datafile, category))
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Iterate through videos.
    for item in get_videos(category):
        if (item['subfolder']):
            list_item = xbmcgui.ListItem(label=item['label'])
            list_item.setInfo('video', {'title': item['label'],
                            # 'genre': video['genre'],
                            'mediatype': 'video'})
            url = get_url(action='subfolder', category=category, counter=item['counter'])
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        else:
            for stream in item['streams']:
                add_playable_listitem(stream)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_subfolder(category, counter):
    xbmc.log('counter: ' + counter, xbmc.LOGNOTICE)
    xbmc.log('category: ' + category, xbmc.LOGNOTICE)
    datafile = cache.cacheFunction(hanssettings.get_datafromfilegithub,category)
    item = hanssettings.get_items_subfolder(datafile, counter)
    xbmcplugin.setPluginCategory(_handle, item['label'])
    xbmcplugin.setContent(_handle, 'videos')
    for stream in item['streams']:
        add_playable_listitem(stream)
    xbmcplugin.endOfDirectory(_handle)

def play_video(path):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    if (path.find('?#User-Agent') > -1):
        path = path.partition('?#User-Agent')[0] + '|User-Agent'+path.partition('?#User-Agent')[2]
    xbmc.log('path: ' + path, xbmc.LOGNOTICE)
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

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
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos_and_subfolder(params['category'])
        elif params['action'] == 'subfolder':
            # Play a video from a provided URL.
            list_subfolder(params['category'], params['counter'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
