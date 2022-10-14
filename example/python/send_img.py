import re
import cv2
from cv2 import imshow
import numpy as np
from confluent_kafka import Producer
from confluent_kafka.error import KafkaException, KafkaError
from time import time, sleep
import pickle
from json import dumps
import threading
COUNT = 0

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
   
def count_fps():
    global COUNT
    old_count = 0
    while True:
        sleep(1)
        print('---------------------------------- Number Message Sent = ', COUNT - old_count)
        old_count = COUNT
def main():
    frame = cv2.imread("/home/vietph/Pictures/skynight.jpg", 1)
    # cv2.imshow('frame', frame)
    # cv2.waitKey(10000)
    # frame = cv2.resize(image, (10000, 2500),
    #            interpolation = cv2.INTER_NEAREST)
    imgbyte = pickle.dumps(cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1])
    # print(type(cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1]), len(cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1]))
    
    # p = Producer({'bootstrap.servers': '172.21.100.154:9092', 'linger.ms': 5000, 'batch.num.messages': 10,
    #           'queue.buffering.max.messages': 1000, 'acks': 1, 'message.max.bytes': 20485880,
    #           'delivery.timeout.ms': 10000, 'request.timeout.ms':2000, 'retries':2, 'retry.backoff.ms':5})
    p = Producer({'bootstrap.servers': '172.21.100.154:9092', 'message.max.bytes': 20485880,
                  'batch.num.messages': 10, 'queue.buffering.max.messages': 1000})
    # Initialize procuder
    # Read frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org1 = (1500, 250)
    org2 = (3000, 250)
    # fontScale
    fontScale = 10 
    # Blue color in BGR
    color = (0, 0, 255)
    # Line thickness of 2 px
    thickness = 3
    # frame1 = cv2.putText(frame, str(1), org, font, 
    #                fontScale, color, thickness, cv2.LINE_AA)
    # cv2.imshow('fram1', frame1)
    # cv2.waitKey(10000)
    NUM_INSERTED = 0
    global COUNT
    while True:
        NUM_INSERTED += 1
        start = time()
        # frame1 = cv2.putText(frame.copy(), str(NUM_INSERTED), org1, font, 
        #            fontScale, color, thickness, cv2.LINE_AA)
        # cv2.putText(frame1, str(NUM_INSERTED), org2, font, 
        #            fontScale, color, thickness, cv2.LINE_AA)
        # imgbyte = pickle.dumps(cv2.imencode('.jpg', frame1)[1])
        # print(len(imgbyte))
        # a = dumps({'num':NUM_INSERTED, 'bytes':imgbyte.hex()}).encode('utf-8')
        # print(len(a))
        try:
            p.produce('Test_C', imgbyte, on_delivery=delivery_report)
        except Exception as e:
            print(e)
        # if NUM_INSERTED % 50 == 0:
        # p.flush()
        if NUM_INSERTED %10 == 0:
            # p.flush()
            number_event = p.poll(0)
            COUNT += number_event
            print("number_event = ", number_event)
        end = time() - start
        # print("time produce = ", end*1000.0, " ms, Number Inserted = ", NUM_INSERTED)
        if 0.017 - end > 0:
            sleep(0.012 - end)
        # sleep(0.1)

if __name__ == "__main__":
    t1 = threading.Thread(target=count_fps)
    t1.start()
    main()
    t1.join()