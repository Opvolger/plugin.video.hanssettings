import queue, threading, platform, subprocess

from subprocess import PIPE, STDOUT, check_output

from streamcheck.lib.queuestreamworker import QueueStreamWorker
from streamcheck.lib.queuecountworker import QueueCounterWorker
from streamcheck.lib.queuekilltasksworker import QueueKillTasksWorker
from streamcheck.lib.queueloggerworker import QueueLoggerWorker

class RunStarter():
    def __init__(self, all_streams, timeout, num_worker_threads, queue_aantal, queue_logging):
        self.all_streams = all_streams
        self.timeout = timeout
        self.num_worker_threads = num_worker_threads
        self.queue_aantal = queue_aantal
        self.num_worker_threads = num_worker_threads
        self.queue_logging = queue_logging

    def start_run(self):
        queue_streams = queue.Queue()

        # we maken alvast wat workers welke wachten op vulling van de queue
        # https://docs.python.org/3/library/queue.html
        # https://docs.python.org/3/library/queue.html#queue.Queue.join
        threads = []
        for i in range(self.num_worker_threads):
            worker = QueueStreamWorker(i + 1, queue_streams, self.queue_logging, self.timeout, self.num_worker_threads)
            t = threading.Thread(target=worker.start, name='QueueStreamWorker %d' % (i +1))
            t.start()
            threads.append(t)

        # we hebben nu alle streams en gaan ze op een queue zetten als ze nog gecontroleerd moeten worden
        start_aantal = 0
        all_streams_in_run = list()
        for stream in [st for st in self.all_streams if st.status_is_check_it()]:
            start_aantal = start_aantal + 1
            all_streams_in_run.append(stream)
            queue_streams.put(stream)

        # toevoegen counter (hoeveel zitten er nog op de queue weergave)
        queue_counter_worker = QueueCounterWorker(queue_streams, self.queue_logging, start_aantal, self.timeout)
        counter_thread = threading.Thread(target=queue_counter_worker.start, name='QueueCounterWorker')
        counter_thread.start()

        # toevoegen om ffprobe te killen welke vast zitten
        queue_counter_worker = QueueKillTasksWorker(queue_streams, self.queue_logging, self.timeout)
        killer_thread = threading.Thread(target=queue_counter_worker.start, name='QueueKillTasksWorker')
        killer_thread.start()        

        self.queue_logging.put('---')
        self.queue_logging.put('Run start met: %d, timeout: %d' % (start_aantal, self.timeout))
        self.queue_logging.put('---')

        # block until all tasks are done
        queue_streams.join()

        # stop workers
        for i in range(self.num_worker_threads):
            queue_streams.put(None)
        self.queue_logging.put('---')
        # echt stoppen van threads (en sub-threads er onder)
        for t in threads:
            t.join()
        self.queue_logging.put("QueueStreamWorkers zijn gestopt")
        # counter zal ook wel gestopt zijn
        counter_thread.join()
        # taskkiller kan ook gestopt worden
        killer_thread.join()

        not_checked_run = sum(st.status_is_check_it() for st in all_streams_in_run)
        totaal_aantal_start = len(self.all_streams)
        not_checked_totaal =  sum(st.status_is_check_it() for st in self.all_streams)
        percentage_te_doen = int(100 / float(len(self.all_streams)) * sum(st.status_is_check_it() for st in self.all_streams))

        self.queue_logging.put('---')
        self.queue_logging.put('RunTotaal/NietVoltooit: %d/%d met timeout: %d' % (start_aantal, not_checked_run, self.timeout))
        self.queue_logging.put('Totaal/Nog Te doen in volgende run(s): %d/%d met timeout: %d' % (totaal_aantal_start, not_checked_totaal, self.timeout))
        self.queue_logging.put('%d%% te doen' % percentage_te_doen)
        self.queue_logging.put('%d aantal thread' % threading.active_count())
        self.queue_logging.put('---')