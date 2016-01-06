__author__ = 'ishekhtman'

# Multi-Threading version of HCC Stress Test

import stress
import multiprocessing
import threading

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, usr, opps, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.usr = usr
        self.opps = opps
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        stress.Main (self.usr, self.opps)
        print "Exiting " + self.name

grinder0 = myThread(1, "grinder0@apixio.net", "grinder0@apixio.net", 1, 1)
grinder1 = myThread(2, "grinder1@apixio.net", "grinder1@apixio.net", 5, 2)
grinder2 = myThread(3, "grinder2@apixio.net", "grinder2@apixio.net", 6, 3)


grinder0.start()
grinder1.start()
grinder2.start()

print "Exiting Main Thread"


