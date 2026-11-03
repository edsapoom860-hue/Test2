from datetime import date
from src.storage import FIELDS, next_report_id, load_records, append_report

def test_report_id_unique():
    day=date(2026,11,2)
    assert next_report_id([],day)=='ST-20261102-0001'
    assert next_report_id([{'report_id':'ST-20261102-0002'}],day)=='ST-20261102-0003'

def test_append_csv(tmp_path):
    file=tmp_path/'reports.csv'
    rec={field:'' for field in FIELDS}
    rec.update(report_id='ST-20261102-0001',talk_date='2026-11-02',company='UBE',department='ผลิต',reporter='ผู้สาธิต',topic='PPE',participants='10',evidence_files='[]',created_at='2026-11-02T09:00:00')
    append_report(file,rec)
    assert load_records(file)[0]['report_id']==rec['report_id']
    assert file.read_bytes().startswith(b'\xef\xbb\xbf')
