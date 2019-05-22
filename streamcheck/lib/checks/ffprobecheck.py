from streamcheck.lib.ffprobe import FFProbe

class FFProbeCheck():
    def __init__(self, stream, timeout):
        self.stream = stream
        self.timeout = timeout 
        #print(self.stream.stream_url)

    def run(self):
        metadata=FFProbe(self.stream.stream_url, self.timeout)
        for probe_stream in metadata.streams:
            if probe_stream.is_video():
                #print('Stream contains {} frames.'.format(probe_stream.frames()))
                self.stream.status = 'OK'