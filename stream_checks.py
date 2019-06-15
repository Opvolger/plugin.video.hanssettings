import requests, queue, threading, sys, subprocess, csv, os, hashlib

from resources.lib.hanssettings import HansSettings
from streamcheck.lib.streamobject import StreamObject
from streamcheck.lib.checks.ffprobecheck import FFProbeCheck
from streamcheck.lib.checks.statuscodecheck import StatusCodeCheck
from streamcheck.lib.checks.m3u8redirector302 import M3u8RedirectOr302

_hanssettings = HansSettings()
# hier kan je proberen hoeveel threads / workers je tegelijk aan hebt.
_num_worker_threads = 50
_timeout = 5
_access_rights = 0o755

print(_hanssettings)

# we draaien #num_worker_threads van deze workers welke de queue leeg halen (tot None)
def worker():
    while True:
        stream = _q.get()
        if stream is None:
            break
        # We proberen een http status-code te bepalen
        try:
            StatusCodeCheck(stream, _timeout).run()
        except requests.ConnectionError:            
            print("Failed to connect - StatusCodeCheck - " + stream.stream_label)
        except:
            print("Error - StatusCodeCheck - " + stream.stream_label)
        # kijken of de stream wat oplevert met FFProbe
        try:
            #print('in: ' + stream.stream_url + ' ('+str(stream.id)+') ')
            FFProbeCheck(stream, _timeout).run()
            #print('out: ' + stream.stream_url + ' ('+str(stream.id)+') ' + stream.status)
        except subprocess.TimeoutExpired:
            print("Timeout - FFProbeCheck - " + stream.stream_label)
        except:
            print("Error - FFProbeCheck - " + stream.stream_label)
        # redirect goed zetten
        try:
            #print('in: ' + stream.stream_url + ' ('+str(stream.id)+') ')
            M3u8RedirectOr302(stream, _timeout).run()
            #print('out: ' + stream.stream_url + ' ('+str(stream.id)+') ' + stream.status)
        except requests.ConnectionError:
            print("Failed to connect - M3u8RedirectOr302 - " + stream.stream_label)
        except:
            print("Error - M3u8RedirectOr302 - " + stream.stream_label)
        # kijken of de new url stream wat oplevert met FFProbe
        try:
            #print('in: ' + stream.stream_url + ' ('+str(stream.id)+') ')
            FFProbeCheck(stream, _timeout).run_new()
            #print('out: ' + stream.stream_url + ' ('+str(stream.id)+') ' + stream.status)
        except subprocess.TimeoutExpired:
            print("Timeout - FFProbeCheck - " + stream.stream_label)
        except:
            print("Error - FFProbeCheck - " + stream.stream_label)
        # we zijn klaar met deze queue opdracht
        _q.task_done()

def loop():
    # we maken alvast wat workers welke wachten op vulling van de queue
    # https://docs.python.org/3/library/queue.html
    threads = []
    for i in range(_num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    # we hebben nu alle streams en gaan ze op een queue zetten
    for stream in [st for st in all_streams if st.status != 'OK']:
        _q.put(stream)

    # block until all tasks are done
    _q.join()

    # stop alle workers
    for i in range(_num_worker_threads):
        _q.put(None)
    for t in threads:
        t.join()

#print(h.get_overzicht(h.get_dataoverzicht()))
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

download_files = True
check_data_dir = os.path.join(current_path, 'check_data')
version_dir = os.path.join(check_data_dir, version)

if os.path.isdir(version_dir):
    download_files = False

if (download_files):
    if not os.path.isdir(check_data_dir):
        # maak de data dir aan als deze er nog niet is
        os.mkdir(check_data_dir, _access_rights)
    # maak de versie dir aan
    os.mkdir(version_dir, _access_rights)
    for filename in github_stream_filenames:
        datafile = _hanssettings.get_data_from_github_file(filename)
        file_on_disk = os.path.join(version_dir, filename)
        with open(file_on_disk, 'wb') as f:
            f.write(datafile.encode())
            

# we gaan alle streams per github-file toevoegen aan 1 grote lijst.
all_streams = list()
i = 0 # file teller
j = 0 # stream teller
for filename in github_stream_filenames:
    i = i + 1
    file_on_disk = os.path.join(version_dir, filename)
    openfile = open(file_on_disk,'r', encoding="utf-8")
    datafile = openfile.read()
    name = _hanssettings.get_name(datafile, filename)
    print(str(i) + ': ' + name)
    streams_datafile = _hanssettings.get_streams(datafile)
    for stream in streams_datafile:
        j = j + 1
        all_streams.append(StreamObject(j, filename, name, stream['label'], stream['url'], stream['header']))
    openfile.close()
    # voor testen even met 4 files
    # if (i == 1):
    #     break

sum_run0 = sum(st.status != 'OK' for st in all_streams)
print('Run0:' + str(sum_run0))
print('---')
_q = queue.Queue()
loop()

# sum_run1 = sum(st.status != 'OK' for st in all_streams)
# print('Run1:' + str(sum_run1))
# print('---')
# _q = queue.Queue()
# _timeout = 10
# loop()

# sum_run2 = sum(st.status != 'OK' for st in all_streams)
# print('Run2:' + str(sum_run2))
# print('---')
# _q = queue.Queue()
# _timeout = 30
# loop()

print('done queues')

# https://www.geeksforgeeks.org/working-csv-files-python/

filename_run = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run.csv'))
filename_run_not_ok = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run_notok.csv'))
create_run = open(filename_run, 'w', newline='')
create_run_not_ok = open(filename_run_not_ok, 'w', newline='')
# creating a csv writer object
csvwriter_run = csv.writer(create_run, delimiter = ';')
csvwriter_run_not_ok = csv.writer(create_run_not_ok, delimiter = ';')
# writing the fields
header = StreamObject.csvheader()
csvwriter_run.writerow(header)
csvwriter_run_not_ok.writerow(header)
for stream in all_streams:
    streamcsvdata = stream.csvrow()
    csvwriter_run.writerow(streamcsvdata)
    if (stream.status != 'OK'):
        csvwriter_run_not_ok.writerow(streamcsvdata)
#close
create_run.close()
create_run_not_ok.close()

for stream in all_streams:
    # laat alle vreemde eenden zien, welke nu nog niet wilde
    if (stream.status != 'OK'):
        print('---')
        print(stream.bouquet_name)
        print(stream.stream_label)
        print(stream.stream_url)
        print(stream.stream_header)
        print(stream.httpstatuscode)
        print('---')
print('---')
print('Run0')
print(sum_run0)
print('---')
# print('Run1')
# print(sum_run1)
# print('---')
# print('Run2')
# print(sum_run2)
# print('---')
# print('Run3')
# print(sum_run3)
# print('---')
