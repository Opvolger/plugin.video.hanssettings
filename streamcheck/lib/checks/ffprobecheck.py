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
        # tegen gaan van rtmp://kamera.task.gda.pl/rtplive playpath=k015.sdp swfUrl=http://task.gda.pl/tech/uslugi/stream/kamera_player/player.swf?213 pageUrl=http://www.task.gda.pl/uslugi/stream/kamera_gdynia_skwer_kosciuszki live=1        
        # if (self.url.startswith('rtmp://') and ' playpath=' in self.url):
        #    return
        if (self.run_check()):
            metadata=FFProbe(self.url, self.timeout)
            for probe_stream in metadata.streams:
                if probe_stream.is_video():
                    self.stream.set_status('OK')
