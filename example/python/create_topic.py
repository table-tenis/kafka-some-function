"""create topic"""
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
import threading
import pickle
import cv2
admin_client = AdminClient({
    'bootstrap.servers': '172.21.100.154:9092',
})

config = {'flush.messages': 30000, 
          'segment.bytes': 1073741824, #1GB #333894336, # 336MB, maximum 2147483647 bytes = 2GB
          'retention.ms': 300000, # 5 minutes'
        #   'retention.bytes': 1033894336,
          'max.message.bytes': 20970880
        #   'retention.bytes': 1887436800
          }
topic_list = []
topic_list.append(NewTopic(topic="HDImage", num_partitions=1, replication_factor=1, config=config))

# validate before doing anything
# try:
#     admin_client.create_topics(new_topics=topic_list, validate_only=True)
# except KafkaException:
#     import sys
#     sys.exit(1)

# # now create the topic actually
# topic_creation_results = admin_client.create_topics(new_topics=topic_list, validate_only=True)

# # Wait for each operation to finish.
# for topic, f in topic_creation_results.items():
#     try:
#         f.result()  # The result itself is None
#         print(f"Topic {topic} created")
#     except KafkaException as e:
#         print(f"Failed to create topic {topic}: {e}")
fs = admin_client.create_topics(topic_list)

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic {} created".format(topic))
    except Exception as e:
        print("Failed to create topic {}: {}".format(topic, e))

frame = cv2.imread("/home/vietph/Pictures/skynight.jpg", 1)
    # cv2.imshow('frame', frame)
    # cv2.waitKey(10000)
    # frame = cv2.resize(image, (10000, 2500),
    #            interpolation = cv2.INTER_NEAREST)
imgbyte = pickle.dumps(cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1])
print(type(imgbyte), len(imgbyte))