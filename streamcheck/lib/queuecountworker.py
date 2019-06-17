import time, platform, subprocess


# Deze class laat elke 30 seconden zien hoeveel items er nog op de queue staan
class QueueCounterWorker():

    def __init__(self, queue, queue_logging, totaal, timeout):
        self.queue = queue
        self.totaal = totaal
        self.timeout = timeout
        self.queue_logging = queue_logging

    def start(self):
        while True:
            size = self.queue.qsize()
            self.queue_logging.put("Aantal op de queue (bij benadering) is: %d/%d" % (size, self.totaal))
            percentage_te_doen = int(100 / float(self.totaal) * size)
            self.queue_logging.put('%d%% te doen' % percentage_te_doen)
            time.sleep(15)
            # dit hoort hier niet, maar af en toe hangende ffprobe killen
            self.queue_logging.put("we gaan nu ffprode-processen welke 'hangen' killen")
            if str(platform.system()) == 'Windows':
                cmd = ["powershell", "-command", "Get-Process ffprobe | Where StartTime -lt (Get-Date).AddMinutes(-2) | Stop-Process -Force"]
            else:
                cmd = ["killall ffprobe --older-than 2m"]
            subprocess.run(cmd, shell=True, timeout=15)        
            if (size == 0):
                break