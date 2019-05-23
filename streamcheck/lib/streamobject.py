class StreamObject(object):
    def __init__(self, id, bouquet_filename, bouquet_name, stream_label, stream_url, stream_header):
        self.id = id
        self.bouquet_filename = bouquet_filename
        self.bouquet_name = bouquet_name
        # split stream
        self.stream_header = stream_header
        self.stream_url = stream_url
        self.stream_label = stream_label
        self.status = 'NOK'
        self.httpstatuscode = None
        self.new_stream_url = None
        self.new_stream_label = None
    
    def csvrow(self):
        csvrowlist = list()
        csvrowlist.append(self.bouquet_filename)
        csvrowlist.append(self.bouquet_name)
        csvrowlist.append(self.stream_header)
        csvrowlist.append(self.stream_label)
        csvrowlist.append(self.stream_url)
        csvrowlist.append(self.status)
        csvrowlist.append(self.httpstatuscode)
        csvrowlist.append(self.new_stream_label)
        csvrowlist.append(self.new_stream_url)
        return csvrowlist

    @staticmethod
    def csvheader():
        csvrowlist = list()
        csvrowlist.append('bouquet_filename')
        csvrowlist.append('bouquet_name')
        csvrowlist.append('stream_header')
        csvrowlist.append('stream_label')
        csvrowlist.append('stream_url')
        csvrowlist.append('status')
        csvrowlist.append('httpstatuscode')
        csvrowlist.append('new_stream_label')
        csvrowlist.append('new_stream_url')
        return csvrowlist
