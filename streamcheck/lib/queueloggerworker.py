# Deze class zorgt er voor dat de logging niet door elkaar loopt.
class QueueLoggerWorker():

    def __init__(self, queue):
        self.queue = queue

    def start(self):
        while True:
            logregel = self.queue.get()
            if logregel is None:
                print("QueueLoggerWorker - Er komt geen logging meer, ik ga uit")
                # De queue is leeg.
                break
            print(logregel)
            # we zijn klaar met deze queue opdracht
            self.queue.task_done()