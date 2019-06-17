import time, platform, subprocess


# Deze class laat elke 30 seconden zien hoeveel items er nog op de queue staan
class QueueKillTasksWorker():

    def __init__(self, queue, queue_logging, timeout):
        self.queue = queue
        self.timeout = timeout
        self.queue_logging = queue_logging

    def start(self):
        while True:
            size = self.queue.qsize()
            time.sleep(self.timeout + 3) # zodat hij ook nog de processen killed welke worden opgepakt als size == 0
            # dit hoort hier niet, maar af en toe hangende ffprobe killen
            try:
                self.queue_logging.put("we gaan nu ffprode-processen welke 'hangen' killen")
                if str(platform.system()) == 'Windows':
                    cmd = ["powershell", "-command", "Get-Process ffprobe | Where StartTime -lt (Get-Date).AddMinutes(-%d) | Stop-Process -Force" % (self.time * 2)]
                else:
                    cmd = ["killall ffprobe --older-than %dm" % (self.timeout * 2)]
                subprocess.run(cmd, shell=True, timeout=15)
            except:
                self.queue_logging.put('killen van ffprode mislukt')
            if (size == 0):
                # we hebben al een sleep en kill gedaan, dus moet nu wel kunnen stoppen
                break                