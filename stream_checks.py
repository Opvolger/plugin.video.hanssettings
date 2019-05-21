import requests, queue, threading

from resources.lib.hanssettings import HansSettings
from streamcheck.lib.streamobject import StreamObject

_hanssettings = HansSettings()
_num_worker_threads = 500
_timeout = 1

print(_hanssettings)

# we draaien #num_worker_threads van deze workers welke de queue leeg halen (tot None)
def worker():
    while True:
        stream = _q.get()
        if stream is None:
            break
        try:
            if (stream.stream_header):
                _key, _value = stream.stream_header.split('=')
                headers = {_key : _value}
                r = requests.head(stream.stream_url, timeout=_timeout, headers=headers)
            else:
                r = requests.head(stream.stream_url, timeout=_timeout)
            stream.httpstatuscode = r.status_code
            # print(r.status_code)
            if (r.status_code != 200):
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.head(stream.stream_url, timeout=_timeout, headers=headers)
                # print(r.status_code)
                if (r.status_code != stream.httpstatuscode):
                    print('new:' + str(r.status_code))
            if (r.status_code == 302):
                # redirect, we schrijven de nieuwe url al vast weg
                stream.new_stream_url = r.url
                # print('new url: ' + r.url)
        except requests.ConnectionError:
            print('---')
            print(stream.bouquet_name)
            print(stream.stream_label)
            print(stream.stream_url)
            # print(stream.stream_header)
            # print(stream.httpstatuscode)
            print("failed to connect")
            # print('---')
        except:
            print('---')
            print(stream.bouquet_name)
            print(stream.stream_label)
            print(stream.stream_url)
            # print(stream.stream_header)
            # print(stream.httpstatuscode)
            print("Error!")
            # print('---')
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
    for stream in [st for st in all_streams if st.httpstatuscode == None]:
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

# we gaan alle streams per github-file toevoegen aan 1 grote lijst.
all_streams = list()
i = 0
for filename in github_stream_filenames:
    i = i + 1
    datafile = _hanssettings.get_data_from_github_file(filename)
    name = _hanssettings.get_name(datafile, filename)
    print(str(i) + ': ' + name)
    streams_datafile = _hanssettings.get_streams(datafile)
    for stream in streams_datafile:
        all_streams.append(StreamObject(filename, name, stream['label'], stream['url'], stream['header']))
    # voor testen even met 4 files
    if (i == 10):
        break

sum_run0 = sum(st.httpstatuscode == None for st in all_streams)

_q = queue.Queue()
loop()
sum_run1 = sum(st.httpstatuscode == None for st in all_streams)

_q = queue.Queue()
_timeout = 5
loop()
sum_run2 = sum(st.httpstatuscode == None for st in all_streams)

_q = queue.Queue()
_timeout = 10
loop()
sum_run3 = sum(st.httpstatuscode == None for st in all_streams)

print('done queues')
for stream in all_streams:
    # laat alle vreemde eenden zien, welke nu nog niet wilde
    if (stream.httpstatuscode != 200):
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
print('Run1')
print(sum_run1)
print('---')
print('Run2')
print(sum_run2)
print('---')
print('Run3')
print(sum_run3)
print('---')
