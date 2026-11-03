from datetime import date
from src.validation import validate_report
MAP={'UBE':['ผลิต'],'UBS':['Wet-Process']}

def test_valid():
    assert validate_report(date.today(),'UBE','ผลิต','ผู้สาธิต','PPE',12,MAP)==[]

def test_no_topic():
    assert any('หัวข้อ' in x for x in validate_report(date.today(),'UBE','ผลิต','ผู้สาธิต','',12,MAP))

def test_participants_zero():
    assert any('จำนวน' in x for x in validate_report(date.today(),'UBE','ผลิต','ผู้สาธิต','PPE',0,MAP))

def test_department_wrong_company():
    assert validate_report(date.today(),'UBE','Wet-Process','ผู้สาธิต','PPE',12,MAP)
