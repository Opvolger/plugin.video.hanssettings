import requests, re
from urllib.parse import urlsplit

class M3u8RedirectOr302():
    def __init__(self, stream, timeout):
        self.stream = stream
        self.timeout = timeout

    def run(self):
        if (self.stream.status != 'OK'):
            if (self.stream.stream_header):
                _key, _value = self.stream.stream_header.split('=')
                headers = {_key : _value}
                response = requests.get(self.stream.stream_url, timeout=self.timeout, headers=headers)
            else:
                response = requests.get(self.stream.stream_url, timeout=self.timeout)

            # http://webcamserverdh.dyndns-remote.com:1935/live/ehtx2.stream/&mp4:playlist.m3u8
            if (response.status_code == 200 and "&" in self.stream.stream_url):
                self.split_m3u8("&", response)
            # http://srv13.arkasis.nl:/721/default.stream/.m3u8
            # deze geeft weer een m3u8 met ts bestanden... geen idee...
            elif (response.status_code == 200 and ".m3u8" in self.stream.stream_url):
                self.split_m3u8(".m3u8", response)
            if (response.status_code == 302):
                # redirect, we schrijven de nieuwe url alvast weg
                self.stream.new_stream_url = response.url

    def split_m3u8(self, split, response):
        regex = r'^[^#].*'
        matches = re.finditer(regex, response.content.decode('utf-8', 'backslashreplace'), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            # we verwijderen de query                
            self.stream.new_stream_url = self.stream.stream_url.split(split)[0] + match.group()