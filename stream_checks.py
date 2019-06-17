import queue, threading, sys, csv, os, hashlib, pickle, json, time

from resources.lib.hanssettings import HansSettings

from streamcheck.lib.queuestreamworker import QueueStreamWorker
from streamcheck.lib.queuecountworker import QueueCounterWorker
from streamcheck.lib.queueloggerworker import QueueLoggerWorker
from streamcheck.lib.runstarter import RunStarter

from streamcheck.lib.streamobject import StreamObject

_hanssettings = HansSettings()
_access_rights = 0o755
_stream_dump = 'all_stream_object_dump.xyz'
_stream_dump_json = 'all_stream_object_dump.json'

def save_all_streams_to_object_file(version_dir: str, stream_dump_full: str, stream_dump_full_json: str, all_streams: list):
    queue_logging.put("save object")
    # schrijf alles voor/na een run weg in een file
    if not os.path.isdir(version_dir):
        # maak de data dir aan als deze er nog niet is
        os.mkdir(version_dir, _access_rights)
    with open(stream_dump_full, 'wb') as stream_dump_file:
        pickle.dump(all_streams, stream_dump_file)
    with open(stream_dump_full_json, 'w') as stream_dump_file:  
        json.dump(all_streams, stream_dump_file, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def write_to_csv():
    # https://www.geeksforgeeks.org/working-csv-files-python/

    filename_run = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run.csv'))
    filename_run_not_ok = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run_notok.csv'))
    kw_args={'newline' : '','encoding' : 'utf_8_sig'}
    create_run = open(filename_run, 'w', **kw_args)
    create_run_not_ok = open(filename_run_not_ok, 'w', **kw_args)
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

queue_logging = queue.Queue()
start_time = time.time()

# toevoegen van logger, deze is gemaakt omdat meerdere QueueStreamWorkers niet naar 1 output kan wegschrijven. ze schrijven over elkaar heen (soms)    
queue_logger_worker = QueueLoggerWorker(queue_logging)
thread_logger = threading.Thread(target=queue_logger_worker.start, name='QueueLoggerWorker')
thread_logger.start()

queue_logging.put('\n\n')
content_type = 'tv'

# ophalen alle bestandsnamen welke we kunnen ophalen in github.
stream_list_github = _hanssettings.get_data_from_github_file_bouquets(content_type)
github_stream_filenames = _hanssettings.get_stream_files_from_bouguet(stream_list_github, content_type)

# totaal aantal streambestanden welke zijn op te halen van github.
count_stream_filenames = len(github_stream_filenames)
queue_logging.put('totaal github-files: %d' % (count_stream_filenames))

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
        queue_logging.put('%d: %s' % (i, name))
        streams_datafile = _hanssettings.get_streams(datafile)
        for stream in streams_datafile:
            j = j + 1
            all_streams.append(StreamObject(j, filename, name, stream['label'], stream['url'], stream['header']))
        # voor testen even met 4 files
        # if (i == 4):
        #     break

# save alle data welke we nodig hebben, zodat we vanaf daar weer kunnen oppakken (als we crashen)
save_all_streams_to_object_file(version_dir, stream_dump_full, stream_dump_full_json, all_streams)

# soms loopt de thread met ffprobe even door. ffprode commando blijt hangen.
# zoals op: ffprobe -show_streams http://ssh101.com/m3u8/dyn/HALStadCentraal/index.m3u8 -loglevel verbose
# zie: https://docs.python.org/3/library/subprocess.html#module-subprocess stukje over timeout
# hierdoor lopen de threads vol. Vandaar deze tussen pauzes.

timeout = 30
workers = 30
#aantal_in_bulk = 5545

aantal_welke_nog_gechecked_moeten_worden = sum(st.status_is_check_it() for st in all_streams)

# mogelijk nog een dump doen om de x items
while (aantal_welke_nog_gechecked_moeten_worden > 0):
    runner = RunStarter(all_streams, timeout, workers, aantal_welke_nog_gechecked_moeten_worden, queue_logging)
    runner.start_run()
    # save alle data na een run
    save_all_streams_to_object_file(version_dir, stream_dump_full, stream_dump_full_json, all_streams)
    aantal_welke_nog_gechecked_moeten_worden = sum(st.status_is_check_it() for st in all_streams)

queue_logging.put('Na checkes van in totaal: %d' % len(all_streams))
for status in StreamObject.get_status_list():
    status_aantal = sum(st.status == status for st in all_streams)
    queue_logging.put('Status %s: %d' % (status, status_aantal))

# tijdelijk alles alvast op rerun
# for stream in [st for st in all_streams if st.status_is_rerun_candidate()]:
#     stream.set_to_rerun()
# save_all_streams_to_object_file(version_dir, stream_dump_full, stream_dump_full_json, all_streams)

# we hebben alles verzameld, maak een csv
write_to_csv()

elapsed_time = time.time() - start_time

queue_logging.put(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

# alle runs zijn klaar, dus er kan geen logging meer komen, block zolang er nog logging is.
# stop de logging worker
queue_logging.put(None)
# wacht tot thread_logger is gestopt
thread_logger.join()