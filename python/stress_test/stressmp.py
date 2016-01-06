__author__ = 'ishekhtman'

# Multi-Processing version of HCC Stress Test

import stress
import multiprocessing
import threading

stress.Main("grinder0@apixio.net", 3)
stress.Main("grinder1@apixio.net", 4)
stress.Main("grinder2@apixio.net", 2)

