from datetime import date

def validate_report(talk_date, company, department, reporter, topic, participants, department_map):
    errors = []
    if not isinstance(talk_date, date): errors.append("กรุณาเลือกวันที่สื่อสาร")
    if company not in department_map: errors.append("กรุณาเลือกบริษัท UBE หรือ UBS")
    if not department or department not in department_map.get(company, []): errors.append("กรุณาเลือกหน่วยงานให้ตรงกับบริษัท")
    if not str(reporter or "").strip(): errors.append("กรุณากรอกชื่อผู้รายงาน")
    if not str(topic or "").strip(): errors.append("กรุณากรอกหัวข้อ Safety Talk")
    if not isinstance(participants, int) or participants <= 0: errors.append("จำนวนผู้เข้าร่วมต้องมากกว่า 0")
    return errors
