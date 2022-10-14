import cv2
from confluent_kafka import Consumer
import numpy as np
from time import time
import pickle
from json import loads
import base64
import numpy as np
def decode_byte_to_frame(byte):
    # frame = cv2.imdecode(byte, cv2.IMREAD_UNCHANGED)
    print(type(byte), len(byte))
    print(pickle.loads(byte))
    frame = cv2.imdecode(pickle.loads(byte), -1)
    return frame

def main():
    # Set kafka params
    # Initialize consumer
    consumer = Consumer({
    'bootstrap.servers': '172.21.100.167:9092',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': 'true',
    'auto.commit.interval.ms': 500,
    'message.max.bytes': 10485880,
    'fetch.min.bytes': 1000000,
    'group.id': 'mygroup'
    })

    consumer.subscribe(['HDImage'])
    counter = 0
    while True:
        start = time()
        msg = consumer.poll(1.0)

        if msg is None:
            print("not found message")
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        # print(msg)
        # print(msg.topic)
        # print(msg.timestamp)
        # print(msg.value)
        # data = loads(msg.value())
        # print(data)
        # frame = decode_byte_to_frame(bytes.fromhex(data['bytes']))
        data = loads(msg.value())
        if data['camera_id'] == 'TDQD_15fps':
            bytes_data = base64.b64decode(data['frame'])
            # print(type(bytes_data))
            deserialized_bytes = np.frombuffer(bytes_data, dtype=np.int8)
            frame = cv2.imdecode(deserialized_bytes, -1)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # data = pickle.loads(msg.value())
            # frame = cv2.imdecode(data, -1)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
        # cv2.imwrite(f"./data/{msg.offset()}.jpg", frame)
        # end = time() - start
        # counter += 1
        # print('consume time = ', end*1000.0, ' ms, offset = ', msg.offset())
        

if __name__ == "__main__":
    main()