from traceback import print_tb
from charset_normalizer import detect
import pymongo
from pymongo import MongoClient
from bson.code import Code
client = MongoClient('172.21.100.167', 27017)
from time import time
import time
from datetime import datetime
from datetime import timezone
from typing import Optional
import pytz
import helper

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def strtime_to_utc(date_time = Optional[str]):
    if date_time == None:
        date_time = datetime.utcfromtimestamp(datetime.now().timestamp())
    else:
        split_datetime = date_time.split(" ")
        if len(split_datetime) == 1:
            print("date = ", split_datetime)
            date_time = helper.str_to_date(date_time)
            date_time = datetime.utcfromtimestamp(date_time.timestamp())
            
        elif len(split_datetime) == 2:
            split_time = split_datetime[1].split(":")
            if len(split_time) == 1:
                print("date hour = ", split_datetime)
                date_time = helper.str_to_datetime_hour(date_time)
                date_time = datetime.utcfromtimestamp(date_time.timestamp())
            elif len(split_time) == 2:
                print("date minute = ", split_datetime)
                date_time = helper.str_to_datetime_minute(date_time)
                date_time = datetime.utcfromtimestamp(date_time.timestamp())
            elif len(split_time) == 3:
                if "." not in split_time[2]:
                    print("date second = ", split_datetime)
                    date_time = helper.str_to_datetime_second(date_time)
                    date_time = datetime.utcfromtimestamp(date_time.timestamp())
                else:
                    print("date milli = ", split_datetime)
                    date_time = helper.str_to_datetime_milli(date_time)
                    date_time = datetime.utcfromtimestamp(date_time.timestamp())
    return date_time

db = client['xface']

detection = db['detection']

staffs = [{'staff_id':1, 'staff_code':'277457', 'fullname':'nguyen phu tai'},
         {'staff_id':2, 'staff_code':'277458', 'fullname':'bui quang minh'},
         {'staff_id':3, 'staff_code':'277459', 'fullname':'nguyen tien dat'}]
dt_now = datetime.now()

print(dt_now, dt_now.timestamp())
dt_utc = datetime.fromtimestamp(dt_now.timestamp(), tz=timezone.utc)
dt_utc = datetime.utcfromtimestamp(dt_now.timestamp())
frame_id = 0
# for i in range(2000):
    
#     for staff in staffs:
#         detect_data = {'staff': staff,
#                 'camera': {'camera_id': 1, 'ip':'172.21.104.100', 'description':'floor 4'},
#                 'frame_id': frame_id+i,
#                 'face': {'x':1, 'y':1, 'w':1, 'h':1, 'encode_imaga':'hdfsufgsufgsie'},
#                 'detection_time': datetime.utcfromtimestamp(datetime.now().timestamp())
#                 }
        
#         detection.insert_one(detect_data)
#         time.sleep(0.01)
# print(detection.find_one())


# Manipulate detection data in mongodb

count = detection.count_documents({})
print(count)
# detection.create_index("timestamp", expireAfterSeconds = 60)

def checkin_checkout_sumary(start_time = None, end_time = None):
    start_time = strtime_to_utc(start_time)
    end_time = strtime_to_utc(end_time)

    print(start_time, type(start_time))
    pipeline = [{"$match": {"detection_time": {"$gt": start_time, "$lt": end_time}, "staff.notify_enable": 1, "staff.state": 1}},
                {"$group": {"_id": "$staff.staff_id", "staff_code":{"$first":"$staff.staff_code"}, 
                            "fullname":{"$first":"$staff.fullname"}, "unit": {"$first": "$staff.unit"},
                            "title": {"$first": "$staff.title"},
                            "checkin": {"$min": "$detection_time"}, "checkout": {"$max": "$detection_time"}}},
                {"$project": {"_id": 0}}]

    result = detection.aggregate(pipeline)
    return result

def sumary_per_person(staff_id = None, staff_code = None, staff_name = None, start_time = None, end_time = None):
    start_time = strtime_to_utc(start_time)
    end_time = strtime_to_utc(end_time)
    
    print(start_time > datetime.utcfromtimestamp(time.time() - 7*24*3600))

    statement = {}
    statement['timestamp'] = {"$gt": start_time, "$lt": end_time}
    if staff_id != None:
        statement['staff.staff_id'] = staff_id
    if staff_code != None:
        statement['staff.staff_code'] = staff_code
    if staff_name != None:
        statement['staff.fullname'] = {'$regex': staff_name}
    print("statement = ", statement)
    result = detection.find(statement, {'_id': 0, 'staff.staff_id': 0})                
    return result

result = checkin_checkout_sumary(start_time="2022-10-14 17:35:00")
for res in result:
    res['checkin'] = helper.datetime_to_str(datetime_from_utc_to_local(res['checkin']))
    res['checkout'] = helper.datetime_to_str(datetime_from_utc_to_local(res['checkout']))
    print(res)
    
# staff_query = detection.find({"staff.staff_id": {"$eq": 2}}, {"timestamp":1}).sort([('timestamp', -1)]).limit(1)
# print(staff_query, type(staff_query))
# for staff in staff_query:
#     print(staff)
    
# staff_sumary = sumary_per_person(staff_name="nguyen phu", start_time="2022-10-13 09")
# # print(len(staff_sumary))
# count = 0
# for doc in staff_sumary:
#     count += 1
#     print(doc)
    
# print(count)


