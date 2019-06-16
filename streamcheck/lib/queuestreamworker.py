import requests, subprocess, threading, sys, time, ctypes

from streamcheck.lib.streamobject import StreamObject

from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck
from streamcheck.lib.checks.m3u8redirector302 import M3u8RedirectOr302

class CheckThread(threading.Thread): 
    def __init__(self, worker_id, stream: StreamObject, queue_logging, timeout): 
        threading.Thread.__init__(self)         
        self.timeout =  timeout
        self.stream = stream
        self.worker_id = worker_id
        self.queue_logging = queue_logging
        self.stop = False
        self.current_check_name = None

    def run_check(self, check):
        try:               
            # self.queue_logging.put(str(self.worker_id) + " " + check.stream.debug_format("Start"))
            self.current_check_name = check.__class__.__name__
            check.run()
        except requests.ConnectionError:                
            self.queue_logging.put(str(self.worker_id) + " " + check.stream.debug_format("Failed to connect - " + self.current_check_name))
        except subprocess.TimeoutExpired:                
            self.queue_logging.put(str(self.worker_id) + " " + check.stream.debug_format( "Timeout - " + self.current_check_name))
        except:                
            self.queue_logging.put(str(self.worker_id) + " " + check.stream.debug_format("Error - " + self.current_check_name))
        if (self.stop):
            raise Exception("Ik moest al stoppen, ik ben timeout gegaan")

    def stop_run(self):
        self.stop = True
        self.stream.set_status('TT')
        self.stream.set_timeout_check(self.current_check_name)

    def run(self):
  
            # target function of the thread class 
            try:               
                # We doen een FFProbe controle
                check = FFProbeCheck(self.stream, self.timeout)
                self.run_check(check)

                # We proberen een http status-code te bepalen
                check = StatusCodeCheck(self.stream, self.timeout)
                self.run_check(check)

                # We kijken of er een redirect is in de M3U8-file
                check = M3u8RedirectOr302(self.stream, self.timeout)
                self.run_check(check)
                
                # we controleren de redirect, misschien werkt deze wel.
                check = FFProbeCheck(self.stream, self.timeout)                
                check.set_url(self.stream.new_stream_url)
                self.run_check(check)

                # we hebben alle checks gehad, we zijn dus NOK
                if (self.stream.status_is_check_it()):
                    self.stream.set_status('NOK')
            except:
                print(self.stream.debug_format("stuk gelopen"))


# Deze class haalt opdrachten van de queue af en gaat controles draaien op de streams
class QueueStreamWorker():

    def __init__(self, id, queue, queue_logging, timeout, workers_aantal):
        self.worker_id = id
        self.queue = queue
        self.queue_logging = queue_logging
        self.timeout = timeout
        self.workers_aantal = workers_aantal

    def quit_function(self, fn_name, check):
        # print to stderr, unbuffered in Python 2.
        self.queue_logging.put('{0} took too long'.format(fn_name))
        # ondanks de "kill" bij timeout, blijft de ffprobe "hangen", tot het process is gekilled.
        # daarom deze timer, dat de werker wel weer vrij komt en we niet wachten op de kill, maar deze op de achtergrond dus nog door gaat
        # dit is ook de reden dat het einde soms wat lang duurt. Er zit dan dus nog een process te wachten op zijn kill :)
        del check        
        sys.stderr.flush() # Python 3 stderr is likely buffered.

    def start(self):
        while True:
            stream = self.queue.get()
            if stream is None:
                self.queue_logging.put("QueueStreamWorker nummer (" + str(self.worker_id) + ") is gestopt: maar er zijn er wel " + str(self.workers_aantal))
                # De queue is leeg.
                break
            # we werken met een CheckThread, zodat we naar de timeout de nek om kunnen draaien van dit ding.
            try:
                t1 = CheckThread(self.worker_id, stream, self.queue_logging, self.timeout) 
                t1.start()
                t1.join(self.timeout)
                if t1.is_alive():
                    t1.stop_run()
                    self.queue_logging.put(stream.debug_format("Loopt buiten timeout"))
            except:
                self.queue_logging.put(stream.debug_format("CheckThread starten mislukt."))
            # we zijn klaar met deze queue opdracht
            self.queue.task_done()