from streamcheck.lib.streamobject import StreamObject
from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck
from streamcheck.lib.checks.m3u8redirector302 import M3u8RedirectOr302

import re

url = 'https://dpp-aldag-ochtendshow.akamaized.net/streamx/DeOchtendshow_540p.m3u8'
#url = 'http://109.236.85.100:8081/SilenceTV/live/playlist.m3u8'
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

#ffprobe -show_streams http://webcamserverdh.dyndns-remote.com:1935/live/ehtx2.stream/&mp4:playlist.m3u8
#http://webcamserverdh.dyndns-remote.com:1935/live/ehtx2.stream/&mp4:playlist.m3u8

#stream = StreamObject(1, 'test','test','label',url,None)

#FFProbeCheck(stream, 5).run()
#print(stream.status)



stream = StreamObject(1, 'test','test','label','http://ssh101.com/m3u8/dyn/HALStadCentraal/index.m3u8',None)
url = 'rtmp://kamera.task.gda.pl/rtplive playpath=k015.sdp swfUrl=http://task.gda.pl/tech/uslugi/stream/kamera_player/player.swf?213 pageUrl=http://www.task.gda.pl/uslugi/stream/kamera_gdynia_skwer_kosciuszki live=1'
#url = 'rtmp://cam.nsprozor.com/kamere/live/BeogradskiKej.2.stream'
#stream = StreamObject(1, 'test','test','label','http://srv13.arkasis.nl:/566/default.stream/masterchunklist_w1920042569.m3u8', None)
#stream = StreamObject(1, 'test','test','label','http://ipv4.api.nos.nl/resolve.php/livestream?url=/live/npo/thematv/journaal24/journaal24.isml/.m3u8',None) #OK
#url = 'http://ipv4.api.nos.nl/resolve.php/livestream?url=/live/npo/thematv/journaal24/journaal24.isml/.m3u8' # OK
url = 'https://streaming01.divercom.be/notele_live/_definst_/direct.stream/chunklist_w1342170057.m3u8'
stream = StreamObject(1, 'test','test','label',url,None) 

#print(stream.httpstatuscode)
print(stream.new_stream_url)
FFProbeCheck(stream, 30).run()
StatusCodeCheck(stream, 30).run()
M3u8RedirectOr302(stream, 5).run()
check = FFProbeCheck(stream, 30)
check.set_url(stream.new_stream_url)
check.run()
print(stream.status)