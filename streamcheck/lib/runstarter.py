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

        print('---')
        print('Run start met: ' + str(start_aantal) + ", timeout: " + str(self.timeout))
        print('---')

        # toevoegen counter (hoeveel zitten er nog op de queue)
        # queue_counter_worker = QueueCounterWorker(queue_streams, queue_logging, start_aantal, timeout)
        # t = threading.Thread(target=queue_counter_worker.start)
        # t.start()
        # threads.append(t)

        # toevoegen van logger, deze is gemaakt omdat meerdere QueueStreamWorkers niet naar 1 output kan wegschrijven. ze schrijven over elkaar heen (soms)    
        queue_logger_worker = QueueLoggerWorker(queue_logging)
        thread_logger = threading.Thread(target=queue_logger_worker.start)
        thread_logger.start()
        
        # block until all tasks are done
        queue_streams.join()

        # stop workers
        for i in range(self.num_worker_threads):
            queue_streams.put(None)
        for t in threads:
            t.join()

        # Wij zijn klaar met alle queue, maar hebben mogelijk nog wat "ffprobe" openstaan
        # kill deze even
        print('kill de ffprobe processen op de achtergrond.')
        if str(platform.system()) == 'Windows':
            cmd = ["taskkill", "/IM", "ffprobe.exe", "/F"]
        else:
            cmd = ["killall ffprobe"]
        subprocess.run(cmd, shell=True, timeout=15)

        # alle stream-workders staan uit, dus er kan geen logging meer komen, block zolang er nog logging is.
        queue_logging.join()
        # stop de logging worker
        queue_logging.put(None)
        # wacht tot thread_logger is gestopt
        thread_logger.join()
        print('---')
        print('Run Start/Stop: ' + str(start_aantal) + "/" + str(sum(st.status_is_check_it() for st in all_streams_in_run)) + " (check-voltooit) met timeout: " + str(self.timeout))
        print('Totaal Start/Stop: ' + str(len(self.all_streams)) + "/" + str(sum(st.status_is_check_it() for st in self.all_streams)) + " (check-voltooit) met timeout: " + str(self.timeout))
        print('---')
        print('We wachten nog even op de "stuk/timeout" gelopen checks')