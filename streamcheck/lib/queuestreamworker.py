import requests, subprocess, threading, sys

from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck
from streamcheck.lib.checks.m3u8redirector302 import M3u8RedirectOr302

# Deze class haalt opdrachten van de queue af en gaat controles draaien op de streams
class QueueStreamWorker():

    def __init__(self, id, queue, queue_logging, timeout, workers_aantal):
        self.worker_id = id
        self.queue = queue
        self.queue_logging = queue_logging
        self.timeout = timeout
        self.workers_aantal = workers_aantal

    def quit_function(self, fn_name):
        # print to stderr, unbuffered in Python 2.
        self.queue_logging.put('{0} took too long'.format(fn_name))
        sys.stderr.flush() # Python 3 stderr is likely buffered.

    def run_check(self, check):
        try:
            check.run()
        except requests.ConnectionError:                
            self.queue_logging.put(check.stream.debug_format("Failed to connect - " + check.__class__.__name__))
        except subprocess.TimeoutExpired:                
            self.queue_logging.put(check.stream.debug_format( "Timeout - " + check.__class__.__name__))
        except:                
            self.queue_logging.put(check.stream.debug_format("Error - " + check.__class__.__name__))

    def start(self):
        while True:
            stream = self.queue.get()
            if stream is None:
                self.queue_logging.put("QueueStreamWorker nummer (" + str(self.worker_id) + ") is gestopt: maar er zijn er wel " + str(self.workers_aantal))
                # De queue is leeg.
                break            
            timer = threading.Timer(self.timeout, self.quit_function, args=[stream.debug_format()])
            timer.start()
            check = None
            try:
                # We proberen een http status-code te bepalen
                check = StatusCodeCheck(stream, self.timeout)
                self.run_check(check)
                
                # We doen een FFProbe controle
                check = FFProbeCheck(stream, self.timeout)
                self.run_check(check)

                # We kijken of er een redirect is in de M3U8-file
                check = M3u8RedirectOr302(stream, self.timeout)
                self.run_check(check)
                
                # we controleren de redirect, misschien werkt deze wel.
                check = FFProbeCheck(stream, self.timeout)
                check.set_url(stream.new_stream_url)
                self.run_check(check)
            finally:
                timer.cancel()
                # ondanks de "kill" bij timeout, blijft de ffprobe "hangen", tot het process is gekilled.
                # daarom deze timer, dat de werker wel weer vrij komt en we niet wachten op de kill, maar deze op de achtergrond dus nog door gaat
                # dit is ook de reden dat het einde soms wat lang duurt. Er zit dan dus nog een process te wachten op zijn kill :)
                del check
            # we zijn klaar met deze queue opdracht
            self.queue.task_done()