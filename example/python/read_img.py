import cv2
from confluent_kafka import Consumer
import numpy as np
from time import time
import pickle
from json import loads
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
    'bootstrap.servers': 'localhost:29092',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'true',
    'auto.commit.interval.ms': 1000,
    'message.max.bytes': 10485880,
    'group.id': 'mygroup1'
    })

    consumer.subscribe(['jpg_image_14'])
    counter = 0
    while True:
        start = time()
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        # print(msg)
        # print(msg.topic)
        # print(msg.timestamp)
        # print(msg.value)
        # data = loads(msg.value())
        # frame = decode_byte_to_frame(bytes.fromhex(data['bytes']))
        frame = decode_byte_to_frame(msg.value())
        # cv2.imwrite(f"./data/{msg.offset()}.jpg", frame)
        end = time() - start
        counter += 1
        print('consume time = ', end*1000.0, ' ms, offset = ', msg.offset())
        

if __name__ == "__main__":
    main()