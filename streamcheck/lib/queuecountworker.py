import time


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
            self.queue_logging.put("Aantal op de queue (bij benadering) is: " + str(size) + "/" + str(self.totaal))
            time.sleep(30)
            if (size == 0):
                self.queue_logging.put("QueueCounterWorker gaat stoppen: maar er is nog een timeout van " + str(self.timeout) + " seconden per worker!")
                self.queue_logging.put("QueueCounterWorker stopt")
                break