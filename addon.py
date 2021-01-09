import xbmcaddon
import xbmcgui
import xbmcplugin
import time
import resources.lib.hanssettings
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
    from urllib.parse import parse_qs
    # File "*****\script.common.plugin.cache\default.py", line 30, in run
    #  sys.path = [settings.getAddonInfo('path').decode('utf-8') + "/lib"] + sys.path
    #  AttributeError: 'str' object has no attribute 'decode'
    import storageserverdummy as StorageServer
else:
    # Fall back to Python 2's urllib2
    from urllib import urlencode
    from urlparse import parse_qs
    try:
        import StorageServer
    except:
        xbmc.log('Using storageserverdummy', xbmc.LOGINFO)
        import storageserverdummy as StorageServer

PLUGIN_NAME = 'hanssettings'
PLUGIN_ID = 'plugin.video.hanssettings'

_hanssettings = resources.lib.hanssettings.HansSettings()
_url = sys.argv[0]
_handle = int(sys.argv[1])
# (Your plugin name, Cache time in hours)
_cache = StorageServer.StorageServer(PLUGIN_ID, 24)
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


def get_github_streamfilenames_list(content_type):
    # cache bouquet-github-file
    stream_list_github = _cache.cacheFunction(
        _hanssettings.get_data_from_github_file_bouquets, content_type)
    return _hanssettings.get_stream_files_from_bouguet(stream_list_github, content_type)


def get_items(github_streamfile):
    # cache github-file
    streamsdatafile = _cache.cacheFunction(
        _hanssettings.get_data_from_github_file, github_streamfile)
    return _hanssettings.get_items(streamsdatafile)


def list_categories(content_type):
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(32004))
    xbmcplugin.setContent(_handle, 'files')

    # ophalen alle bestandsnamen welke we kunnen ophalen in github.
    github_stream_filenames = get_github_streamfilenames_list(content_type)

    # totaal aantal streambestanden welke zijn op te halen van github.
    count_stream_filenames = len(github_stream_filenames)

    # setup progress bar
    progress = xbmcgui.DialogProgress()
    progress.create(_addon.getLocalizedString(32002),
                    _addon.getLocalizedString(32001))

    # init teller voor progress bar
    i = 0
    for filename in github_stream_filenames:
        i = i + 1

        # tekst prgress-bar, met met netjes voorgang er in met:  "files: x/y gehad"
        progressText = _addon.getLocalizedString(
            32003) % (i, count_stream_filenames)

        # python2 int delen door int = altijd een int, dus eerst omzetten naar een float
        # percentage bepaling
        if (sys.version_info[0] == 3):
            progress.update(int(100 / float(count_stream_filenames) * i),
                            progressText)
        else:
            progress.update(int(100 / float(count_stream_filenames) * i),
                            "",progressText)
        if progress.iscanceled():
            # als iemand de progress-bar stopt, dan alleen laten zien wat je al hebt, spring uit deze loop.
            break

        # we gaan file voor file ophalen in deze loop
        datafile = _cache.cacheFunction(
            _hanssettings.get_data_from_github_file, filename)

        # na de file ophalen gaan we hem in een item stoppen
        name = _hanssettings.get_name(datafile, filename)
        list_item = xbmcgui.ListItem(label=name)
        list_item.setInfo(get_context(content_type), {'title': name,
                                                      'mediatype': get_context(content_type)})

        # url voor navigeren.
        url = get_url(action='listing', filename=filename,
                      content_type=content_type)

        # alles in deze loop in een folder
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # we hebben alles geladen, de progress bar kan gesloten worden
    progress.close()
    del progress
    xbmcplugin.endOfDirectory(_handle)


def add_playable_listitem(item, content_type):
    list_item = xbmcgui.ListItem(label=item['label'])
    list_item.setInfo(get_context(content_type), {
                      'title': item['label'], 'mediatype': get_context(content_type)})
    list_item.setProperty('IsPlayable', 'true')
    url = get_url(
        action='play', item=item['stream'], content_type=content_type)
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)


def list_items_and_subfolder(filename, counter, content_type):
    datafile = _cache.cacheFunction(
        _hanssettings.get_data_from_github_file, filename)
    category_name = ''
    itemlist = list()    
    if (counter == None):
        # we openen een hoofdfile, dus alle items
        itemlist = get_items(filename)
        # naam van github-file overnemen
        category_name = _hanssettings.get_name(datafile, filename)
    else:
        # we openen een sub-folder, dus alleen deze item toevoegen
        item = _hanssettings.get_items_subfolder(datafile, counter)
        # nu even niet als een subfolder gedragen, we willen nu de stream hier van hebben
        item['subfolder'] = False
        itemlist.append(item)
        # naam overnemen van sub-folder
        category_name = item['label']
    xbmcplugin.setContent(_handle, 'files')
    xbmcplugin.setPluginCategory(_handle, category_name)

    # langs gaan van alle items
    for item in itemlist:
        if (item['subfolder']):
            # we hebben een subfolder te pakken.
            # deze zijn allemaal genummerd.
            list_item = xbmcgui.ListItem(label=item['label'])
            list_item.setInfo(get_context(content_type), {
                              'title': item['label'], 'mediatype': get_context(content_type)})
            url = get_url(action='subfolder', filename=filename,
                          counter=item['counter'], content_type=content_type)
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        else:
            # we hebben een directe stream te pakken, geef deze weer.
            for stream in item['streams']:
                add_playable_listitem(stream, content_type)
    xbmcplugin.endOfDirectory(_handle)


def play_item(path):
    # als er een user-agent moet worden meegeven, dit moet iets anders onder kodi.
    if (path.find('?#User-Agent') > -1):
        path = path.partition(
            '?#User-Agent')[0] + '|User-Agent'+path.partition('?#User-Agent')[2]
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def get_context(content_type):
    if content_type == 'audio':
        return 'music'
    if content_type == 'music':
        return 'music'
    return 'video'


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    args = parse_qs(paramstring)
    # Check the parameters passed to the plugin
    content_type = args.get('content_type', ['video'])[0]
    # xbmc.log('content_type: ' + content_type, xbmc.LOGNOTICE)
    action = args.get('action', ['list'])[0]
    if action == 'listing':
        # we openen een filestream
        list_items_and_subfolder(args.get('filename', None)[
                                 0], None, content_type)
    elif action == 'subfolder':
        # we openen een sub-sectie van een file stream
        list_items_and_subfolder(args.get('filename', None)[
                                 0], args.get('counter', None)[0], content_type)
    elif action == 'play':
        # we gaan afspelen
        play_item(args.get('item', None)[0])
    else:
        # standaard gaan we naar de hoofdpagina met alle filestreams uit de bouquet-file van het juiste type (audio/video)
        list_categories(content_type)


if __name__ == '__main__':
    router(sys.argv[2][1:])
