select staff.id, staff.staff_code, staff.fullname, b.min_time, b.max_time 
from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time 
                                from detection
                                where Date(detection_time) = CurDate() 
                                group by staff_id) as b
on staff.id = b.staff_id
where staff.state != 0;
