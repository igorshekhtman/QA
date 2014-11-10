import json
from kafka import KafkaClient, SimpleProducer, SimpleConsumer

kafka = KafkaClient("kafka-prd-node1.apixio.net:9092")
consumer = SimpleConsumer(kafka, "pythonTestGroup", "production.dashboard_stats2")
for message in consumer:
    data = json.loads(message.message.value)
    if data["statType"] == "Collection":
        print str(data["unixtime"]) + "\t" + data["statName"] + "\t" + str(len(data["value"]))
kafka.close()