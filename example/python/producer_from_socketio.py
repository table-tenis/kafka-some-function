CAMERA_IPS = [
    "172.21.104.201",
    "172.21.104.202",
    "172.21.104.119",
    "172.21.110.105",
    "172.21.104.121",
    "172.21.110.106",
    "172.21.110.107",
    "172.21.110.108",
    "172.21.110.109",
    "172.21.110.110",
    "172.21.110.111",
    "172.21.110.112",
    "172.21.111.101",
    "172.21.111.102",
    "172.21.111.103",
    "172.21.111.104",
    "172.21.111.105",
    "172.21.111.106",
    "172.21.111.107",
    "172.21.111.108",
    "172.21.111.109",
    "172.21.105.101",
    "172.21.105.102",
    "172.21.111.110",
    "172.21.111.111",
    "172.21.109.101",
    "172.21.109.102",
    "172.21.109.103",
    "172.21.109.104",
    "172.21.109.105",
    "172.21.109.106",
    "172.21.109.107",
    "172.21.109.108",
    "172.21.109.109",
    "172.21.109.110",
    "172.21.109.111",
    "10.61.166.186",
    "172.21.105.103",
    "172.21.104.100",
    "172.21.104.101",
    "172.21.104.102",
    "172.21.104.103",
    "172.21.104.104",
    "172.21.104.105",
    "172.21.104.106",
    "172.21.104.107",
    "172.21.104.108",
    "172.21.104.109",
    "172.21.104.110",
    "172.21.104.111",
    "172.21.104.112",
    "172.21.104.113",
    "172.21.104.114",
    "10.61.166.187",
    "10.61.166.188",
    "172.21.105.104",
    "172.21.105.105",
    "172.21.105.106",
    "172.21.105.107",
    "172.21.105.108",
    "172.21.105.109",
    "172.21.105.110",
    "172.21.105.111",
    "172.21.111.112",
    "172.21.109.112",
    "172.21.109.113",
    "172.21.109.114",
    "172.21.109.115",
    "172.21.104.116",
    "172.21.104.117",
    "172.21.104.118",
    "172.21.104.123",
    "172.21.110.101",
    "172.21.110.102",
    "172.21.110.103",
    "172.21.110.104",
    "172.21.104.115",
    "172.21.104.122",
    "172.21.104.124",
    "172.21.104.125",
    "172.21.104.126",
    "172.21.104.127",
    "172.21.104.128",
    "172.21.104.129",
    "172.21.104.131",
    "172.21.104.132",
    "172.21.104.142",
    "172.21.100.136",
    "172.21.120.101",
    "172.21.120.102",
    "172.21.120.103",
    "172.21.120.104",
    "172.21.120.105",
    "172.21.104.140",
    "172.21.104.141",
    "172.21.104.143",
]

URL = 'http://172.21.100.254:8080'

import json
import asyncio
import socketio
sio = socketio.AsyncClient()

from datetime import datetime
from json import dumps
from confluent_kafka import Producer
from confluent_kafka.error import KafkaException, KafkaError

p = Producer({'bootstrap.servers': '172.21.100.174:29092', 'linger.ms': 20000, 'batch.num.messages': 10,
              'queue.buffering.max.messages': 1000, 'acks': 1,
              'delivery.timeout.ms': 25000, 'request.timeout.ms':10, 'retries':2, 'retry.backoff.ms':5})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
# p.flush()

NUM_RECEIVED_PACKET = 0
NUM_INSERTED = 0

async def register():
    """connect to server, greating, and subcribe"""
    # connect to server
    await sio.connect(URL)
    print('my sid is', sio.sid)

    # intro
    s = json.dumps({"msgType": "intro", "type": "client", "role": "dev"})
    await sio.emit("intro message", s)

    # have to subscribe
    for i in range(0, int(len(CAMERA_IPS))):
        s = json.dumps({"ip": CAMERA_IPS[i], "msgType": "subscribe"})
        await sio.emit("subscribe", s)
    
    await sio.wait()

@sio.event
async def connect():
    """connected event"""
    print("connected")

async def add_detection_to_kafka(data):
    """data"""
    global NUM_INSERTED
    NUM_INSERTED += 1
    data['stt'] = NUM_INSERTED
    # print(data)
    
    print(len(data))
    try:
        p.produce('mot_detection_v2', dumps(data).encode('utf-8'), on_delivery=delivery_report)
    except Exception as e:
        print(e)
    if NUM_INSERTED % 50 == 0:
        number_event = p.poll(0)
        print("number_event = ", number_event)
    # if NUM_INSERTED % 1000 == 0:
    #     number_msg = p.flush(2)
    #     print("number_msg in queue = ", number_msg)

@sio.on("new detection")
async def on_new_detection(data):
    """receive new detection"""
    global NUM_RECEIVED_PACKET
    NUM_RECEIVED_PACKET += 1
    await add_detection_to_kafka(data)

@sio.on('*')
async def catch_all(event, data):
    """any vents that do not have an event handler"""
    print("catch {} with data {}".format(event, data))

async def print_stats():
    """print stats"""
    while True:
        await asyncio.sleep(2)
        print("{} packets received, {} packets inserted".format(NUM_RECEIVED_PACKET, NUM_INSERTED))

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(register())
    loop.create_task(print_stats())
    loop.run_forever()

if __name__ == "__main__":
    main()