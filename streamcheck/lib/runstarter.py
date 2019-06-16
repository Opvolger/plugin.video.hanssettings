import requests, queue, threading

import platform, subprocess
from subprocess import PIPE, STDOUT, check_output

from streamcheck.lib.queuestreamworker import QueueStreamWorker
from streamcheck.lib.queuecountworker import QueueCounterWorker
from streamcheck.lib.queueloggerworker import QueueLoggerWorker

class RunStarter():
    def __init__(self, all_streams, timeout, num_worker_threads, queue_aantal):
        self.all_streams = all_streams
        self.timeout = timeout
        self.num_worker_threads = num_worker_threads
        self.queue_aantal = queue_aantal
        self.num_worker_threads = num_worker_threads

    def start_run(self):
        queue_streams = queue.Queue()
        queue_logging = queue.Queue()    
    
        # toevoegen van logger, deze is gemaakt omdat meerdere QueueStreamWorkers niet naar 1 output kan wegschrijven. ze schrijven over elkaar heen (soms)    
        queue_logger_worker = QueueLoggerWorker(queue_logging)
        thread_logger = threading.Thread(target=queue_logger_worker.start)
        thread_logger.start()

        # we maken alvast wat workers welke wachten op vulling van de queue
        # https://docs.python.org/3/library/queue.html
        # https://docs.python.org/3/library/queue.html#queue.Queue.join
        threads = []
        for i in range(self.num_worker_threads):
            worker = QueueStreamWorker(i + 1, queue_streams, queue_logging, self.timeout, self.num_worker_threads)
            t = threading.Thread(target=worker.start)
            t.start()
            threads.append(t)

        # we hebben nu alle streams en gaan ze op een queue zetten als ze nog niet OK zijn
        start_aantal = 0
        all_streams_in_run = list()
        for stream in [st for st in self.all_streams if st.status_is_check_it()]:
            start_aantal = start_aantal + 1
            all_streams_in_run.append(stream)
            if (start_aantal >= self.queue_aantal):
                # we stoppen met x items op de queue
                break
            queue_streams.put(stream)

        # toevoegen counter (hoeveel zitten er nog op de queue)
        # queue_counter_worker = QueueCounterWorker(queue_streams, queue_logging, start_aantal, timeout)
        # t = threading.Thread(target=queue_counter_worker.start)
        # t.start()
        # threads.append(t)

        queue_logging.put('---')
        queue_logging.put('Run start met: %d, timeout: %d' % (start_aantal, self.timeout))
        queue_logging.put('---')

        # block until all tasks are done
        queue_streams.join()

        # stop workers
        for i in range(self.num_worker_threads):
            queue_streams.put(None)
        for t in threads:
            t.join()
        queue_logging.put('---')
        queue_logging.put("QueueStreamWorkers zijn gestopt, we gaan nu ffprode-processen welke 'hangen' killen")
        # Wij zijn klaar met alle queue, maar hebben mogelijk nog wat "ffprobe" openstaan
        # kill deze even        
        if str(platform.system()) == 'Windows':
            cmd = ["taskkill", "/IM", "ffprobe.exe", "/F"]
        else:
            cmd = ["killall ffprobe"]
        subprocess.run(cmd, shell=True, timeout=15)
                
        not_checked_run = sum(st.status_is_check_it() for st in all_streams_in_run)
        totaal_aantal_start = len(self.all_streams)
        not_checked_totaal =  sum(st.status_is_check_it() for st in self.all_streams)
        percentage_te_doen = int(100 / float(len(self.all_streams)) * sum(st.status_is_check_it() for st in self.all_streams))

        queue_logging.put('---')
        queue_logging.put('RunTotaal/NietVoltooit: %d/%d met timeout: %d' % (start_aantal, not_checked_run, self.timeout))
        queue_logging.put('Totaal/Nog Te doen in volgende run(s): %d/%d met timeout: %d' % (totaal_aantal_start, not_checked_totaal, self.timeout))
        queue_logging.put('%d%% te doen' % percentage_te_doen)
        queue_logging.put('---')

        # alle stream-workders staan uit, dus er kan geen logging meer komen, block zolang er nog logging is.
        queue_logging.join()
        # stop de logging worker
        queue_logging.put(None)
        # wacht tot thread_logger is gestopt
        thread_logger.join()