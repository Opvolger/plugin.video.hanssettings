from streamcheck.lib.ffprobe import FFProbe
import _thread as thread
import threading, sys

from streamcheck.lib.checks.basecheck import BaseCheck
from streamcheck.lib.streamobject import StreamObject

class FFProbeCheck(BaseCheck):
    def __init__(self, stream: StreamObject, timeout):
        super().__init__(stream, timeout)
        self.url = stream.stream_url

    def set_url(self, url):
        self.url = url
    
    def run(self):
        if (self.url and self.run_check()):
            metadata=FFProbe(self.url, self.timeout)
            for probe_stream in metadata.streams:
                if probe_stream.is_video():
                    self.stream.set_status('OK')
