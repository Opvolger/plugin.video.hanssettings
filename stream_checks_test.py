from streamcheck.lib.streamobject import StreamObject
from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck

import re

#url = 'https://hls.streamonecloud.net/livestream/amlst:fDa32BaPi9r3/chunklist_b596.m3u8'
url = 'http://109.236.85.100:8081/SilenceTV/live/playlist.m3u8'
#url = 'rtmp://84.22.97.59:80/beverwijk/studio'
#url = 'http://streams.uitzending.tv/centraal/centraal/chunklist_w1734214400.m3u8'
#url = 'http://talparadiohls-i.akamaihd.net/hls/live/585615/VR-Veronica-1/Q5.m3u8'
#url = 'https://558bd16067b67.streamlock.net/radionl/radionl/chunklist_w1478214221.m3u8'
#url = 'https://558bd16067b67.streamlock.net/radionl/radionl/chunklist_w1527483009.m3u8'
#url = 'http://cdn15.streampartner.nl:1935/rtvnof2/live/playlist.m3u8'
#url = 'https://593aed234297b.streamlock.net/visual_radio/visual_radio/playlist.m3u8'
#url = 'http://hls.streamonecloud.net/livestream/amlst:FiK93m7AaqQ2/playlist.m3u8'
#url = 'http://hls2.slamfm.nl/content/slamwebcam/slamwebcam.m3u8'
#url = 'https://hls.streamonecloud.net/livestream/amlst:fDa32BaPi9r3/chunklist_b596.m3u8'
#url = 'https://558bd16067b67.streamlock.net/rtvemmen_cam/rtvemmen_cam/chunklist.m3u8'

stream = StreamObject(1, 'test','test','label',url,None)

FFProbeCheck(stream, 1).run()
print(stream.status)
