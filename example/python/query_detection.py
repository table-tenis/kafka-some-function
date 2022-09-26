from email import charset
from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, func, alias
from sqlalchemy.orm import sessionmaker
import mariadb
import sys
import time
engine = create_engine("mariadb+mariadbconnector://root:root@127.0.0.1:3308/xface_system", echo=True)
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
   
Session = sessionmaker(bind=engine)
SESSION = Session() 
conn = mariadb.connect(
    user="root",
    password="root",
    host="127.0.0.1",
    port=3308,
    database='xface_system'
)

    # Instantiate Cursor
cur = conn.cursor()
conn.close()
print("conn = ", conn)
print("cur = ", cur)
def report():
    conn = mariadb.connect(
            user="root",
            password="root",
            host="127.0.0.1",
            port=3308,
            database='xface_system'
            )

    # Instantiate Cursor
    cur = conn.cursor()
    print("conn = ", conn)
    statement = """select staff.id, staff.staff_code, staff.fullname, b.min_time, b.max_time 
                    from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time 
                                                from detection
                                                where Date(detection_time) = CurDate() 
                                                group by staff_id) as b
                    on staff.id = b.staff_id
                    where staff.state != 0;"""
    cur.execute(statement)
    # for data in cur:
    #     print(data)
        
def report_alchemy():
    statement = """select staff.id, staff.staff_code, staff.fullname, b.min_time, b.max_time 
                    from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time 
                                                from detection
                                                where Date(detection_time) = CurDate() 
                                                group by staff_id) as b
                    on staff.id = b.staff_id
                    where staff.state != 0;"""
    # stat1 = Staff.join(Detection, Staff.id == Detection.staff_id)
    
    s = Staff.alias('s')
    d = Detection.alias('d')
    sub_query = select([d.staff_id, func.min(d.detection_time), func.max(d.detection_time)]).where(d.detection_time >= '2022-09-06 01:00:00').group_by(d.staff_id)
    # statement = select([s.id, s.staff_code, s.fullname, func.min(d.detection_time), func.max(d.detection_time)]).select_from(stat1).where(Detection.detection_time >= '2022-09-06 01:00:00' and Staff.state != 0).group_by(Detection.staff_id)
    staffs = SESSION.execute(sub_query).all()
    for staff in staffs:
        # print(staff[0].id, staff[0].staff_code, staff[0].fullname)
        print(staff[0])

if __name__ == '__main__':
    start = time.time()
    report()
    stop = time.time() - start
    print("execute time = ", stop)