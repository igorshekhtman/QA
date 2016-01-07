__author__ = 'ishekhtman'

# Multi-Processing version of HCC Stress Test

import stress
import multiprocessing
import threading


def worker(num):
    """thread worker function"""
    print 'Worker:', num
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()










stress.Main("grinder0@apixio.net", 3)
stress.Main("grinder1@apixio.net", 4)
stress.Main("grinder2@apixio.net", 2)

print "\n"
print ">>>>>>>>>> D O N E <<<<<<<<<<"
