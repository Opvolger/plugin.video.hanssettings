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