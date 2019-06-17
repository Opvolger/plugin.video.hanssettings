import requests

from streamcheck.lib.checks.basecheck import BaseCheck
from streamcheck.lib.streamobject import StreamObject

class StatusCodeCheck(BaseCheck):
    def __init__(self, stream: StreamObject, timeout):
        super().__init__(stream, timeout)

    def run(self):
        # voorkom: No connection adapters were found for 'rtmp://cam.nsprozor.com/kamere/live/BeogradskiKej.2.stream'
        if (self.stream.stream_url.startswith('rtmp://')):
            return
        if (self.run_check()):
            if (self.stream.stream_header):
                _key, _value = self.stream.stream_header.split('=')
                headers = {_key : _value}
                response = requests.head(self.stream.stream_url, timeout=self.timeout, headers=headers)
            else:
                response = requests.head(self.stream.stream_url, timeout=self.timeout)
            self.stream.httpstatuscode = response.status_code
            # print(r.status_code)
            # if (r.status_code != 200):
            #     headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            #     r = requests.head(stream.stream_url, timeout=_timeout, headers=headers)
            #     # print(r.status_code)
            #     if (r.status_code != stream.httpstatuscode):
            #         print('new:' + str(r.status_code))
            if (response.status_code == 302):
                # redirect, we schrijven de nieuwe url al vast weg
                self.stream.new_stream_url = response.url
                # print('new url: ' + r.url)
            response.close()