class StreamObject(object):
    def __init__(self, id, bouquet_filename, bouquet_name, stream_label, stream_url, stream_header):
        self.id = id
        self.bouquet_filename = bouquet_filename
        self.bouquet_name = bouquet_name
        # split stream
        self.stream_header = stream_header
        self.stream_url = stream_url
        self.stream_label = stream_label
        self.status = 'DNC'
        self.httpstatuscode = None
        self.new_stream_url = None
        self.new_stream_label = None
        self.timeout_checks = list()
        # DNC = Did Not Check
        # CA = Check Again
        # NOK = Not Ok
        # OK = Ok
        # CT = CheckTimeout        
        self.status_list = self.get_status_list()
    
    @staticmethod
    def get_status_list():
        return ['DNC','CA','NOK','OK','CT']

    def debug_format(self, info=''):
        return '%d %s %s [%s]' % (self.id, self.stream_label, self.bouquet_name, info)        

    def status_is_check_it(self):
        status_to_check_list = ['DNC','CA','CT']
        if (self.status in status_to_check_list):
            return True
        return False

    def set_timeout_check(self, check_name):
        self.timeout_checks.append(check_name)

    def set_to_rerun(self):
        self.status = 'CA'
        self.timeout_checks = list()

    def set_status(self, status):        
        if (status in self.status_list):
            self.status = status
        else:
            raise Exception("Onbekende status")        

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
