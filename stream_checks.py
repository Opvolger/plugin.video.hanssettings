import requests, queue, threading, sys, csv, os, hashlib, pickle, json, time

from resources.lib.hanssettings import HansSettings

from streamcheck.lib.queuestreamworker import QueueStreamWorker
from streamcheck.lib.queuecountworker import QueueCounterWorker
from streamcheck.lib.queueloggerworker import QueueLoggerWorker

from streamcheck.lib.streamobject import StreamObject

_hanssettings = HansSettings()
_access_rights = 0o755
_stream_dump = 'all_stream_object_dump.xyz'
_stream_dump_json = 'all_stream_object_dump.json'

def save_all_streams_to_object_file(version_dir: str, stream_dump_full: str, stream_dump_full_json: str, all_streams: list):
    print("save object")
    # schrijf alles voor/na een run weg in een file
    if not os.path.isdir(version_dir):
        # maak de data dir aan als deze er nog niet is
        os.mkdir(version_dir, _access_rights)
    with open(stream_dump_full, 'wb') as stream_dump_file:
        pickle.dump(all_streams, stream_dump_file)
    with open(stream_dump_full_json, 'w') as stream_dump_file:  
        json.dump(all_streams, stream_dump_file, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def loop(timeout, num_worker_threads):
    queue_streams = queue.Queue()
    queue_logging = queue.Queue()

    sum_run0 = sum(st.status != 'OK' for st in all_streams)
 
    # we maken alvast wat workers welke wachten op vulling van de queue
    # https://docs.python.org/3/library/queue.html
    # https://docs.python.org/3/library/queue.html#queue.Queue.join
    threads = []
    for i in range(num_worker_threads):
        worker = QueueStreamWorker(i + 1, queue_streams, queue_logging, timeout, num_worker_threads)
        t = threading.Thread(target=worker.start)
        t.start()
        threads.append(t)

    # we hebben nu alle streams en gaan ze op een queue zetten als ze nog niet OK zijn
    start_nok_aantal = 0
    for stream in [st for st in all_streams if st.status != 'OK']:
        start_nok_aantal = start_nok_aantal + 1
        queue_streams.put(stream)

    print('---')
    print('Run start met: ' + str(start_nok_aantal) + " NOK timeout: " + str(timeout))
    print('---')

    # toevoegen counter (hoeveel zitten er nog op de queue)
    queue_counter_worker = QueueCounterWorker(queue_streams, queue_logging, start_nok_aantal, timeout)
    t = threading.Thread(target=queue_counter_worker.start)
    t.start()
    threads.append(t)

    # toevoegen van logger, deze is gemaakt omdat meerdere QueueStreamWorkers niet naar 1 output kan wegschrijven. ze schrijven over elkaar heen (soms)    
    queue_logger_worker = QueueLoggerWorker(queue_logging)
    thread_logger = threading.Thread(target=queue_logger_worker.start)
    thread_logger.start()    
    
    # block until all tasks are done
    queue_streams.join()

    # stop workers
    for i in range(num_worker_threads):
        queue_streams.put(None)
    for t in threads:
        t.join()

    # alle stream-workders staan uit, dus er kan geen logging meer komen, block zolang er nog logging is.
    queue_logging.join()
    # stop de logging worker
    queue_logging.put(None)
    # wacht tot thread_logger is gestopt
    thread_logger.join()
    print('---')
    print('Start/Stop: ' + str(start_nok_aantal) + "/" + str(sum(st.status != 'OK' for st in all_streams)) + " NOK timeout: " + str(timeout))
    print('---')

def write_to_csv():
    # https://www.geeksforgeeks.org/working-csv-files-python/

    filename_run = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run.csv'))
    filename_run_not_ok = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run_notok.csv'))
    create_run = open(filename_run, 'w', newline='')
    create_run_not_ok = open(filename_run_not_ok, 'w', newline='')
    # creating a csv writer object
    csv_writer_run = csv.writer(create_run, delimiter = ';')
    csv_writer_run_not_ok = csv.writer(create_run_not_ok, delimiter = ';')
    # writing the fields
    header = StreamObject.csvheader()
    csv_writer_run.writerow(header)
    csv_writer_run_not_ok.writerow(header)
    for stream in all_streams:
        stream_csv_data = stream.csvrow()
        csv_writer_run.writerow(stream_csv_data)
        if (stream.status != 'OK'):
            csv_writer_run_not_ok.writerow(stream_csv_data)
    #close
    create_run.close()
    create_run_not_ok.close()

start_time = time.time()

print('\n\n')
content_type = 'tv'

# ophalen alle bestandsnamen welke we kunnen ophalen in github.
stream_list_github = _hanssettings.get_data_from_github_file_bouquets(content_type)
github_stream_filenames = _hanssettings.get_stream_files_from_bouguet(stream_list_github, content_type)

# totaal aantal streambestanden welke zijn op te halen van github.
count_stream_filenames = len(github_stream_filenames)
print('totaal github-files: ' + str(count_stream_filenames))

# version wordt niet meer juist gevuld
# version = _hanssettings.get_version_from_bouquet(stream_list_github, content_type)
md5hash = hashlib.md5(stream_list_github.encode())
version = md5hash.hexdigest()

current_path = os.getcwd()

# data buiten de plugin directory
check_data_dir = os.path.join(current_path, '../hanssettings_check_data')
if not os.path.isdir(check_data_dir):
    # maak de data dir aan als deze er nog niet is
    os.mkdir(check_data_dir, _access_rights)

version_dir = os.path.join(check_data_dir, version)
stream_dump_full = os.path.join(version_dir, _stream_dump)
stream_dump_full_json = os.path.join(version_dir, _stream_dump_json)

# all_stream kan ook gehaald worden uit een voorgaande run of vanaf internet
if os.path.isfile(stream_dump_full):
    # haal alles weer op uit vorige run, met dus al resultaten
    with open(stream_dump_full, 'rb') as stream_dump_file:
        # Step 3
        all_streams = pickle.load(stream_dump_file)
else:
    # we gaan alle streams per github-file toevoegen aan 1 grote lijst.
    all_streams = list()
    i = 0 # file teller
    j = 0 # stream teller
    for filename in github_stream_filenames:
        i = i + 1
        datafile = _hanssettings.get_data_from_github_file(filename)
        name = _hanssettings.get_name(datafile, filename)
        print(str(i) + ': ' + name)
        streams_datafile = _hanssettings.get_streams(datafile)
        for stream in streams_datafile:
            j = j + 1
            all_streams.append(StreamObject(j, filename, name, stream['label'], stream['url'], stream['header']))
        # voor testen even met 4 files
        if (i == 4):
            break

# save alle data welke we nodig hebben, zodat we vanaf daar weer kunnen oppakken (als we crashen)
save_all_streams_to_object_file(version_dir, stream_dump_full, stream_dump_full_json, all_streams)

loop(30, 15)

# save alle data na een run
save_all_streams_to_object_file(version_dir, stream_dump_full, stream_dump_full_json, all_streams)

write_to_csv()

elapsed_time = time.time() - start_time

print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))