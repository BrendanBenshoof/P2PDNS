#worker handler
import threading
from Queue import PriorityQueue, Empty
class WorkerManager(object):
    def __init__(self):
        self.running_threads = []
        self.ideal_threads = 0
        self.target = None
        self.inbox = PriorityQueue()
        self.running = False
        self.ishandler = True

    def set_target(self,t):
        self.target = t

    def threadloop(self):
        #print "threadloop started"
        while self.running:
            if self.ishandler:
                try:
                    x = self.inbox.get(False)
                    #print "calling handler"
                    self.target(x)
                    self.inbox.task_done()
                except Empty:
                    pass
            else:
                self.target()

    def start(self):
        self.running = True
        while(len(self.running_threads) < self.ideal_threads):
            t = threading.Thread(target=self.threadloop)
            t.daemon = True
            t.start()
            self.running_threads.append(t)

    def stop(self):
        self.running = False

    def checkup(self):
        for t in self.running_threads:
            if not t.isAlive():
                del t
            self.start()

    def putjob(self, datum):
        if self.running:
            self.inbox.put(datum, True)
            self.checkup()
        else:
            raise Error("added job to dead worker")
