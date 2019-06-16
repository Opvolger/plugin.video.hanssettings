# https://github.com/DheerendraRathor/ffprobe3/blob/master/ffprobe3/ffprobe.py
"""
Python wrapper for ffprobe command line tool. ffprobe must exist in the path.
"""
import os, sys
import pipes
import platform
import re
import subprocess

from threading import Timer

from subprocess import PIPE, STDOUT, check_output

#from ffprobe3.exceptions import FFProbeError
class FFProbeError(Exception):
    pass

class FFProbe:
    """
    FFProbe wraps the ffprobe command and pulls the data into an object form::
        metadata=FFProbe('multimedia-file.mov')
    """

    def add_stream_from_output(self, output):
        # https://regex101.com/codegen?language=python
        regex = r'\[STREAM\](.*?)\[\/STREAM\]'
        output_str = output.decode('ascii').replace('\n','\\n').replace('\r','\\r') # eng
        matches = re.finditer(regex, output_str)
        for matchNum, match in enumerate(matches, start=1):    
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1        
                match_with_line_end = match.group(groupNum).replace('\\n','\n').replace('\\r','\r') #eng
                arraylist = match_with_line_end.splitlines()
                arraylist = list(filter(None, arraylist))
                self.streams.append(FFStream(arraylist))            

    def __init__(self, video_file, timeout):
        self.video_file = video_file
        try:
            with open(os.devnull, 'w') as tempf:
                subprocess.check_call(["ffprobe", "-h"], stdout=tempf, stderr=tempf)
        except:
            raise IOError('ffprobe not found.')
        if str(platform.system()) == 'Windows':
            cmd = ["ffprobe", "-show_streams", self.video_file]
        else:
            cmd = ["ffprobe -show_streams " + pipes.quote(self.video_file)]

        # https://www.blog.pythonlibrary.org/2016/05/17/python-101-how-to-timeout-a-subprocess/
        # https://docs.python.org/3/library/subprocess.html#subprocess.run
        # p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        p = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, timeout=timeout)
        #p = check_output(cmd, stderr=STDOUT, timeout=timeout)
        self.format = None
        self.created = None
        self.duration = None
        self.start = None
        self.bitrate = None
        self.streams = []
        self.video = []
        self.audio = []
        data_lines = []
        
        self.add_stream_from_output(p.stdout)
        self.add_stream_from_output(p.stderr)

        for a in self.streams:
            if a.is_audio():
                self.audio.append(a)
            if a.is_video():
                self.video.append(a)


class FFStream:
    """
    An object representation of an individual stream in a multimedia file.
    """

    def __init__(self, data_lines):
        for a in data_lines:
            kvPair = a.strip().split('=')
            if len(kvPair) > 1 :
                self.__dict__[kvPair[0]] = kvPair[1]

    def is_audio(self):
        """
        Is this stream labelled as an audio stream?
        """
        val = False
        if self.__dict__['codec_type']:
            if str(self.__dict__['codec_type']) == 'audio':
                val = True
        return val

    def is_video(self):
        """
        Is the stream labelled as a video stream.
        """
        val = False
        if self.__dict__['codec_type']:
            if self.__dict__['codec_type'] == 'video':
                val = True
        return val

    def is_subtitle(self):
        """
        Is the stream labelled as a subtitle stream.
        """
        val = False
        if self.__dict__['codec_type']:
            if self.__dict__['codec_type'] == 'subtitle':
                val = True
        return val

    def frame_size(self):
        """
        Returns the pixel frame size as an integer tuple (width,height) if the stream is a video stream.
        Returns None if it is not a video stream.
        """
        size = None
        if self.is_video():
            width = self.__dict__['width']
            height = self.__dict__['height']
            if width and height:
                try:
                    size = (int(width), int(height))
                except ValueError:
                    raise FFProbeError("None integer size %s:%s" % (width, height))

        return size

    def pixel_format(self):
        """
        Returns a string representing the pixel format of the video stream. e.g. yuv420p.
        Returns none is it is not a video stream.
        """
        f = None
        if self.is_video():
            if self.__dict__['pix_fmt']:
                f = self.__dict__['pix_fmt']
        return f

    def frames(self):
        """
        Returns the length of a video stream in frames. Returns 0 if not a video stream.
        """
        frame_count = 0
        if self.is_video() or self.is_audio():
            if self.__dict__['nb_frames']:
                try:
                    frame_count = int(self.__dict__['nb_frames'])
                except ValueError:
                    raise FFProbeError('None integer frame count')
        return frame_count

    def duration_seconds(self):
        """
        Returns the runtime duration of the video stream as a floating point number of seconds.
        Returns 0.0 if not a video stream.
        """
        duration = 0.0
        if self.is_video() or self.is_audio():
            if self.__dict__['duration']:
                try:
                    duration = float(self.__dict__['duration'])
                except ValueError:
                    raise FFProbeError('None numeric duration')
        return duration

    def language(self):
        """
        Returns language tag of stream. e.g. eng
        """
        lang = None
        if self.__dict__['TAG:language']:
            lang = self.__dict__['TAG:language']
        return lang

    def codec(self):
        """
        Returns a string representation of the stream codec.
        """
        codec_name = None
        if self.__dict__['codec_name']:
            codec_name = self.__dict__['codec_name']
        return codec_name

    def codec_description(self):
        """
        Returns a long representation of the stream codec.
        """
        codec_d = None
        if self.__dict__['codec_long_name']:
            codec_d = self.__dict__['codec_long_name']
        return codec_d

    def codec_tag(self):
        """
        Returns a short representative tag of the stream codec.
        """
        codec_t = None
        if self.__dict__['codec_tag_string']:
            codec_t = self.__dict__['codec_tag_string']
        return codec_t

    def bit_rate(self):
        """
        Returns bit_rate as an integer in bps
        """
        b = 0
        if self.__dict__['bit_rate']:
            try:
                b = int(self.__dict__['bit_rate'])
            except ValueError:
                raise FFProbeError('None integer bit_rate')
        return b