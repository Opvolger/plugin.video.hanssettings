import resources.lib.hanssettings
import shutil
from urllib.request import urlretrieve
from urllib.request import urlopen, Request
import os

h = resources.lib.hanssettings.HansSettings()
url = 'https://raw.githubusercontent.com/haroo/HansSettings/master/e2_hanssettings_kabelNL/'

def get_datafromurl():    
    req = Request(url + 'bouquets.tv')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
    req.add_header('Content-Type', 'text/html; charset=utf-8')
    response = urlopen(req)
    linkdata=response.read().decode('utf-8', 'backslashreplace')    
    response.close()
    return linkdata

def main():
    dirgithubfiles = os.path.join(os.path.dirname(__file__), 'resources', 'githubfiles')
    if not os.path.exists(dirgithubfiles):
        pluginversion = ''
    else:
        dataoverzichtplugin = h.get_dataoverzicht()
        pluginversion = h.get_version(dataoverzichtplugin)
    dataoverzichturl = get_datafromurl()
    githubversion = h.get_version(dataoverzichturl)    
    
    if (pluginversion != githubversion):
        # We hebben een update, of nog geen files
        shutil.rmtree('resources/githubfiles', ignore_errors=True)        
        if not os.path.exists(dirgithubfiles):
            os.makedirs(dirgithubfiles)
        bouquetsfile = os.path.join(dirgithubfiles, 'bouquets.tv')
        urlretrieve (url + 'bouquets.tv', bouquetsfile)
        for stream in h.get_overzicht(dataoverzichturl):
            streamfile = os.path.join(dirgithubfiles, stream)
            urlretrieve (url + stream, streamfile)

main()

