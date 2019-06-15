from streamcheck.lib.ffprobe import FFProbe
import _thread as thread
import threading, sys
from streamcheck.lib.checks.basecheck import BaseCheck

class FFProbeCheck(BaseCheck):
    def __init__(self, stream, timeout):
        super().__init__(stream, timeout)
        self.url = stream.stream_url

    def set_url(self, url):
        self.url = url
    
    def run(self):
        if (self.url and self.stream.status != 'OK'):
            metadata=FFProbe(self.url, self.timeout)
            for probe_stream in metadata.streams:
                if probe_stream.is_video():
                    self.stream.status = 'OK'
