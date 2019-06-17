import sys, threading
import _thread as thread
from abc import ABC, abstractmethod

from streamcheck.lib.streamobject import StreamObject

# omdat een worker wel eens vast wil lopen, ondanks de timeouts.
# https://stackoverflow.com/questions/492519/timeout-on-a-function-call
def quit_function(fn_name):
    # print to stderr, unbuffered in Python 2.
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    #thread.interrupt_main() # raises KeyboardInterrupt
    thread.exit()

def exit_after(s):
    '''
    use as decorator to exit process if 
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer

class BaseCheck(ABC):    
    def __init__(self, stream: StreamObject, timeout):
        self.stream = stream
        self.timeout = timeout
    
    @abstractmethod
    def run(self):
        pass

    def run_check(self):
        classname =  self.__class__.__name__
        if (self.stream.status == 'CT' and classname in self.stream.timeout_checks):
            return False
        if (self.stream.status != 'OK'):
            return True
        return False # Dus OK!
