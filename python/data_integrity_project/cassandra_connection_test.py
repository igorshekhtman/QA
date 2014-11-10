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

session = cluster.connect()

session.set_keyspace('apixio')

#results = session.execute("""SELECT * FROM simplex.playlists WHERE id = 2cc9ccb7-6221-4ccb-8387-f22b6a1b354d;""")

results = session.execute("""SELECT * FROM apixio.cf381 WHERE rowkey='pat_f5bd251e-750b-4a01-9246-fcd90167f81c';""")

for row in results:
    print str(row)


# show tables;

cluster.shutdown()

print "The End ..."