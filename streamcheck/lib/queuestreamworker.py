import requests, subprocess, threading, sys, time, ctypes

from streamcheck.lib.streamobject import StreamObject

from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck
from streamcheck.lib.checks.m3u8redirector302 import M3u8RedirectOr302

class ChecksThreadTimeoutException(Exception):
    pass

class ChecksThread(threading.Thread): 
    def __init__(self, worker_id, stream: StreamObject, queue_logging, timeout): 
        threading.Thread.__init__(self, name='ChecksThread-stream: %d' % stream.id)
        self.timeout =  timeout
        self.stream = stream
        self.worker_id = worker_id
        self.queue_logging = queue_logging
        self.stop = False
        self.current_check_name = None

    def run_check(self, check):
        """Functie zal de uitvoer doen van de check en alle foutmeldingen afvangen
        """
        try:               
            if (self.stop):
                raise ChecksThreadTimeoutException("Ik moest al stoppen, ik ben timeout gegaan")
            # self.queue_logging.put(str(self.worker_id) + " " + check.stream.debug_format("Start"))
            self.current_check_name = check.__class__.__name__
            check.run()
        except ChecksThreadTimeoutException:
            self.queue_logging.put('%d %s' % (self.worker_id, check.stream.debug_format('ChecksThreadTimeoutException')))
        except requests.ConnectionError:                
            self.queue_logging.put('%d %s' % (self.worker_id, check.stream.debug_format("Failed to connect - %s" % self.current_check_name)))
        except subprocess.TimeoutExpired:                
            self.queue_logging.put('%d %s' % (self.worker_id, check.stream.debug_format("Timeout - %s" % self.current_check_name)))
        except:
            self.queue_logging.put('%d %s' % (self.worker_id, check.stream.debug_format("Error - %s" % self.current_check_name)))
        self.current_check_name = None

    def stop_run(self):
        """Functie welke de ChecksThread doet stoppen (als dat nog niet zo is)

        Zal de ChecksThread stoppen en de stream op de status 'CT' (CheckTimeout) zetten.
        De huidige check word toegevoegd in de lijst timeout_checks van het stream object, 
        zo kunnen we zien welke checks niet werken voor deze stream

        """        
        self.stop = True
        if (self.current_check_name != None):
            self.stream.set_status('CT')
            self.stream.set_timeout_check(self.current_check_name)
            self.queue_logging.put(self.stream.debug_format("Loopt buiten timeout"))
            # raise ChecksThreadTimeoutException("Ik moest al stoppen, ik ben timeout gegaan")

    def run(self):
        """Functie welke de ChecksThread start

        Hier worden de verschillende checks gedaan. Mocht er buiten de checks om een error optreden.
        Dan zal de stream op status 'CT' (CheckTimeout) gezet worden.
        De huidige check word toegevoegd in de lijst timeout_checks van het stream object, 
        zo kunnen we zien welke checks niet werken voor deze stream

        """
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
            self.queue_logging.put(self.stream.debug_format("stuk gelopen (was ooit timeout gegaan, mogelijk ffprobe kill gehad), kan van voorgaande run zijn!"))


# Deze class haalt opdrachten van de queue af en gaat controles draaien op de streams
class QueueStreamWorker():
    """Een Worker welke streams van de queue afhaald en checks zal uitvoeren
    """
    def __init__(self, id, queue, queue_logging, timeout, workers_aantal):
        self.worker_id = id
        self.queue = queue
        self.queue_logging = queue_logging
        self.timeout = timeout
        self.workers_aantal = workers_aantal

    def start(self):
        """Deze start zal een ChecksThread starten met een timeout.
        """
        while True:
            stream = self.queue.get()
            if stream is None:
                # De queue is leeg.
                break
            # we werken met een ChecksThread, zodat we naar de timeout de nek om kunnen draaien van dit ding.
            t1 = ChecksThread(self.worker_id, stream, self.queue_logging, self.timeout)
            try:                
                t1.start()
                t1.join(self.timeout)
                t1.stop_run()
            except:
                self.queue_logging.put(stream.debug_format("ChecksThread starten/uitvoeren mislukt. (Timeout?)"))
            finally:                
                # we zijn klaar met deze queue opdracht
                self.queue.task_done()
                t1.join() # queue taak is klaar, maar we wachten nog even op thread