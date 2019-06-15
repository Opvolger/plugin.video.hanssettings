import requests

class StatusCodeCheck():
    def __init__(self, stream, timeout):
        self.stream = stream
        self.timeout = timeout

    def run(self):
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