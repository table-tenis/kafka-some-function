"""simple consumer"""
import struct
import base64
from json import loads
from datetime import datetime
import time
import sqlalchemy
from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
engine = create_engine("mariadb+mariadbconnector://root:root@172.21.100.174:3306/xface_system", echo=True)
print(engine.connect())

Base = declarative_base(engine)
class Detection(Base):
    __tablename__ = 'detection'
    __table_args__ = {'autoload': True}
    
class Staff(Base):
    __tablename__ = 'staff'
    __table_args__ = {'autoload': True}
    
class Camera(Base):
    __tablename__ = 'camera'
    __table_args__ = {'autoload': True}

from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': '172.21.100.154:9092',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'false',
    'auto.commit.interval.ms': 1000,
    'group.id': 'mygroup'
})
Session = sqlalchemy.orm.sessionmaker(bind=engine)
SESSION = Session()

consumer.subscribe(['XFace'])

index = 0
def datetime_to_str(date_obj):
    if(date_obj == None or (isinstance(date_obj, datetime) == False)):
      return None
    try:
      return datetime.strftime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as err:
      print('ValueError: ', err)
    
list_data = []  
while True:
    start_time = time.time()
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue
    # print(len(msg.value()))
    data = loads(msg.value())
    print(data)
    a = {'title': 'FaceMeta', 'description': 'Metadata of face detected from video sources', 'type': 'object', 
     'properties': {'required': ['timestamp', 'camera_id', 'frame_id', 'cropped_image'], 
                    'timestamp': {'description': 'Time stamp of the image that this event blong to', 'type': 'double', 'value': 1664964590634.0}, 
                    'camera_id': {'description': 'Camera_id of the image that this event blong to', 'type': 'string', 'value': 'VTS'}, 
                    'frame_id': {'description': 'Frame_id of the image that this event blong to', 'type': 'integer', 'value': 69}, 
                    'cropped_image': {'type': 'object', 'properties': {'required': 
                        ['x', 'y', 'w', 'h', 'confidence_score', 'name', 'staff_id', 'feature', 'encoded_img'], 
                        'x': {'description': 'top left x coordinate of face image', 'type': 'float', 'value': 52.27944564819336}, 
                        'y': {'description': 'top left y coordinate of face image', 'type': 'float', 'value': 1748.33203125}, 
                        'w': {'description': 'width of face image', 'type': 'float', 'value': 40.03125}, 
                        'h': {'description': 'height of face image', 'type': 'float', 'value': 42.19855499267578}, 
                        'confidence_score': {'description': 'confidence score of name of the person appeared on the face image', 
                                             'type': 'float', 'value': 0.3670362532138825}, 
                        'name': {'description': 'name of the person appeared on the face image', 'type': 'string', 'value': 'Unknown'}, 
                        'staff_id': {'description': 'staff_id of the person appeared on the face image', 'type': 'string', 'value': '000000'}, 
                        'feature': {'description': 'vector feature of face image', 'type': 'bytes', 
                                    'value': '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'}, 
                        'encoded_img': {'description': 'jpeg encoded image of face', 'type': 'bytes', 'value': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAqACgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDy+306SSZsj5astoat25rqo4I1XgUqmJD81Rc6HA5D/hHHzkDinpoJzgiuxSaJjgEVaht0J3EgCjmBQOOi8OlRkiiuvmniiHzEAUUcw+VFK2OWG/pTNQtGZgU6Ve1K0e0uGVlwoNLBIGQZ7VJSMeK0k3jqK0popVgAUnNSBt0uAR1q04wB60hmTDaNJxMDgUVryNGtrK8rqpx6UVaTMW9TEtvGdpfWIj1JQJRxuHWqy6lA5IhfIrzVPvCtCBiDwTTaKjI9FgLNhjtx9azdY8QpZHy1O5ulc8ksmwfvH/76NY92S07biTz3oSFKTSOgj1Oe9DFnOPSiszTO9FbR2Ods/9k='}}}}}
    print('feature len = ', len(a['properties']['cropped_image']['properties']['feature']['value']))
    print('encode len = ',len(a['properties']['cropped_image']['properties']['encoded_img']['value']))
    # print(msg.offset(), msg.partition())
    # staff = SESSION.execute(select(Staff).where(Staff.staff_code == data['staffCode'])).first()
    # camera = SESSION.execute(select(Camera).where(Camera.ip == data['ip'])).first()
    # insert_data = {'staff_id':staff[0].id, 'cam_id':camera[0].id, 'session_id':1,
    #                'frame_id':1, 'detection_time':datetime_to_str(datetime.fromtimestamp(data['detectionTime']/1000.0)), 
    #                'detection_score':data['confidence'],
    #                'box_x':1, 'box_y':1, 'box_width':1, 'box_height':1}
    # # print("detection time = ", insert_data['detection_time'])
    # list_data.append(insert_data)
    # return_commit = consumer.commit(msg, asynchronous=True)
    # print('return_commit = ', return_commit)
    # if(len(list_data) >= 100):
    #     SESSION.execute(Detection.__table__.insert(), list_data)
    #     SESSION.commit()
    #     insert_time = (time.time() - start_time)*1000.0
    #     print("==================== insert-time = ", insert_time, " milliseconds")
    #     list_data.clear()
    # else:
    #     load_time = (time.time() - start_time)*1000.0
    #     print("=================== load-time = ", load_time)
    # print(f'Received message: {index}:', staff[0].id, staff[0].staff_code, ', type = ', type(staff[0]))

consumer.close()