import sys
import json

if sys.version_info.major == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen

class BouquetHelper():

    @staticmethod
    def create_url_for_bouquet(url, header = None):
        url = url.replace(':','%3a')
        if header != None:
            header = header.replace(':','%3a')
            return '%s#%s' % (url, header)
        return url
    
    @staticmethod
    def text_for_bouquet(text):
        # python2 bytes to string
        if sys.version_info.major == 2:
            text = text.encode('utf-8')
        # escape
        text = text.replace(':','%3a')
        return text

def get_steam_objects(url):
    response = urlopen(url)

    plain_data = response.read()

    json_object = json.loads(plain_data, strict=False)

    # we gaan eerst alle elements "plat slaan"
    stream_elements = []
    for element_pluto in json_object:
        stream_elements.append(json_object[element_pluto])
    return stream_elements

def pluto_tv():
    pluto_tv_elements = get_steam_objects("https://i.mjh.nz/PlutoTV/all.json")

    # nu sorteren we de plat geslagen data
    pluto_tv_elements.sort(key=lambda x: (x['group'], x['name']))

    with open('output_pluto.tv', 'w') as f:
        f.write('#NAME Stream Pluto TV USA\n')
        f.write('#SERVICE 1:64:197a:0:0:0:0:0:0:0:\n')
        group = None
        for item in pluto_tv_elements:
            chno = str(item['chno'])
            if group != item['group']:
                group = item['group']
                f.write('#DESCRIPTION %s\n' % (BouquetHelper.text_for_bouquet(group)))
            f.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s %s\n' % (BouquetHelper.create_url_for_bouquet(BouquetHelper.text_for_bouquet(item['url'])), chno, BouquetHelper.text_for_bouquet(item['name'])))
            f.write('#DESCRIPTION %s %s\n' % (chno, BouquetHelper.text_for_bouquet(item['name'])))

def stirr():
    stirr_elements = get_steam_objects("https://i.mjh.nz/Stirr/stations.json")

    # nu sorteren we de plat geslagen data
    stirr_elements.sort(key=lambda x: (x['chno']))

    with open('output_stirr.tv', 'w') as f:
        f.write('#NAME Stream STIRR TV\n')
        f.write('#SERVICE 1:64:197a:0:0:0:0:0:0:0:\n')
        for item in stirr_elements:
            chno = str(item['chno'])
            f.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s %s\n' % (BouquetHelper.create_url_for_bouquet(BouquetHelper.text_for_bouquet(item['url'])), chno, BouquetHelper.text_for_bouquet(item['name'])))
            f.write('#DESCRIPTION %s %s\n' % (chno, BouquetHelper.text_for_bouquet(item['name'])))

if __name__ == "__main__":
    pluto_tv()
    stirr()
