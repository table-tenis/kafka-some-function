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
from pydantic import parse_raw_as
from pydantic.error_wrappers import ValidationError
from data_schema import Topic1Model, Topic5Model
from pymongo import MongoClient
from bson.code import Code

import helper
TOPIC1 = "RawMeta"
TOPIC5 = 'topic5_test'

client = MongoClient('172.21.100.167', 27017)
xface_db = client['xface']
detection_coll = xface_db['detection']
# detection_coll.create_index("detection_time", expireAfterSeconds = 28800)

engine = create_engine("mariadb+mariadbconnector://root:root@172.21.100.167:3306/xface_system", echo=True)
print(engine.connect())

Base = declarative_base(engine)
class Detection(Base):
    __tablename__ = 'detection'
    __table_args__ = {'autoload': True}
    
class Mot(Base):
    __tablename__ = 'mot'
    __table_args__ = {'autoload': True}
    
class Staff(Base):
    __tablename__ = 'staff'
    __table_args__ = {'autoload': True}
    
class Camera(Base):
    __tablename__ = 'camera'
    __table_args__ = {'autoload': True}

from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': '172.21.100.167:9092',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'true',
    'auto.commit.interval.ms': 1000,
    'group.id': 'mygroup'
})
Session = sqlalchemy.orm.sessionmaker(bind=engine)
SESSION = Session()

consumer.subscribe([TOPIC1])

index = 0
def datetime_to_str(date_obj):
    if(date_obj == None or (isinstance(date_obj, datetime) == False)):
      return None
    try:
      return datetime.strftime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as err:
      print('ValueError: ', err)
    
list_data = []  
list_mot = []
mongo_detection_list = []
while True:
    start_time = time.time()
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue
    # print(len(msg.value()))
    # data = loads(msg.value())
    # print(data)
    
    # {
    #     "srctime": 1665733649803,
    #     "camera_id": "8",
    #     "frame_id": 3669,
    #     "session_id": "f64549d3-b3e3-4390-98b6-90fa99bc2cda",
    #     "FACE": [ {'bbox', 'feature', 'image', 'name', 'staff_id', 'score'}

    #     ],
    #     "MOT": [
    #           {'bbox', 'object_id', 'embedding'}
    #     ]
    # }

    try:
        t1 = parse_raw_as(Topic1Model, msg.value())
        # print(t1.srctime, datetime_to_str(helper.datetime_from_utc_to_local(t1.srctime)))
        for face in t1.FACE:
            print(face.bbox)
            staff = SESSION.execute(select(Staff).where(Staff.staff_code == face.staff_id)).first()
            camera = SESSION.execute(select(Camera).where(Camera.id == t1.camera_id)).first()
            if staff:
                # print(staff[0].id, staff[0].staff_code, staff[0].fullname)
                # camera = SESSION.execute(select(Camera).where(Camera.ip == data['ip'])).first()
                staff = staff[0]
                camera = camera[0]
                insert_data = {'staff_id':staff.id, 'cam_id':t1.camera_id, 'session_id':t1.session_id,
                        'frame_id': t1.frame_id, 'detection_time':datetime_to_str(helper.datetime_from_utc_to_local(t1.srctime)), 
                        'detection_score': face.score,
                        'box_x':face.bbox.x, 'box_y': face.bbox.y, 'box_width':face.bbox.w, 'box_height':face.bbox.h,
                        'feature': face.feature}
                
                
                mongo_detect_data = {'staff': {'staff_id': staff.id, 'staff_code': staff.staff_code, 'unit': staff.unit,
                                               'title': staff.title, 'fullname': staff.fullname, 'nickname': staff.nickname,
                                               'cellphone': staff.cellphone, 'date_of_birth': helper.date_to_str(staff.date_of_birth),
                                               'sex': staff.sex, 'state': staff.state, 'notify_enable': staff.notify_enable},
                'camera': {'camera_id': camera.id, 'ip': camera.ip, 'site_id': camera.site_id, 'name': camera.name, 
                           'description': camera.description, 'rtsp_uri': camera.rtsp_uri, 'stream': camera.stream},
                'frame_id': t1.frame_id,
                'face': {'x':face.bbox.x, 'y': face.bbox.y, 'w': face.bbox.w, 'h': face.bbox.h, 'encoded_image': face.image},
                'detection_time': t1.srctime
                }
                print(t1.srctime, type(t1.srctime))
                list_data.append(insert_data)
                # detection_coll.insert_one(mongo_detect_data)
                mongo_detection_list.append(mongo_detect_data)
                if(len(list_data) >= 100):
                    SESSION.execute(Detection.__table__.insert(), list_data)
                    SESSION.commit()
                    detection_coll.insert_many(mongo_detection_list)
                    insert_time = (time.time() - start_time)*1000.0
                    print("==================== insert-time = ", insert_time, " milliseconds")
                    list_data.clear()
                    mongo_detection_list.clear()
                    
        for mot in t1.MOT:
            # print(staff[0].id, staff[0].staff_code, staff[0].fullname)
            # camera = SESSION.execute(select(Camera).where(Camera.ip == data['ip'])).first()
            insert_data = {'cam_id':t1.camera_id, 'session_id':t1.session_id,
                    'frame_id': t1.frame_id, 'track_time':datetime_to_str(helper.datetime_from_utc_to_local(t1.srctime)), 
                    'track_id': mot.object_id,
                    'box_x':mot.bbox.x, 'box_y': mot.bbox.y, 'box_width':mot.bbox.w, 'box_height':mot.bbox.h}
            # print(insert_data)
            list_mot.append(insert_data)
            if(len(list_mot) >= 100):
                SESSION.execute(Mot.__table__.insert(), list_mot)
                SESSION.commit()
                insert_time = (time.time() - start_time)*1000.0
                print("==================== insert-time = ", insert_time, " milliseconds")
                list_mot.clear()
                
                
        
    except ValueError as e:
        print(',', end='')

consumer.close()