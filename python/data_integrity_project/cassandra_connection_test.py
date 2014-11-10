from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from ssl import PROTOCOL_TLSv1
import logging
import ssl
import os

os.system('clear')
log = logging.getLogger()
log.setLevel('INFO')


#cluster = Cluster(['10.199.22.32', '10.196.81.90', '10.198.2.83', '10.196.100.53', '10.197.91.36', '10.199.52.19'])

cluster = Cluster(['10.199.22.32', '10.196.81.90', '10.198.2.83', '10.196.100.53', '10.197.91.36', '10.199.52.19'], port=9042)

session = cluster.connect('apixio')

cluster.shutdown()

print "The End ..."