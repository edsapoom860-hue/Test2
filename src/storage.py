"""Local CSV workshop storage, not a production multi-user database."""
from pathlib import Path
from datetime import datetime, date
import csv, json, os, tempfile, uuid

FIELDS = ['report_id','talk_date','company','department','reporter','topic','participants','evidence_files','created_at']

def load_records(path):
    path = Path(path)
    if not path.exists(): return []
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS: raise ValueError('CSV schema ไม่ตรงกับหัวตาราง')
        return list(reader)

def next_report_id(records, talk_date):
    stamp = talk_date.strftime('%Y%m%d')
    prefix=f'ST-{stamp}-'
    numbers=[]
    for rec in records:
        rid=str(rec.get('report_id',''))
        if rid.startswith(prefix) and rid[len(prefix):].isdigit(): numbers.append(int(rid[len(prefix):]))
    return f'{prefix}{max(numbers,default=0)+1:04d}'

def append_report(path, report):
    """Atomic replace for workshop (no concurrent multi-user guarantee)."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    existing=load_records(path)
    r=dict(report)
    if any(r.get(k) is None for k in FIELDS): raise ValueError('ข้อมูลรายงานไม่ครบตาม schema')
    if r['report_id'] in {row['report_id'] for row in existing}: raise ValueError('Report ID ซ้ำ')
    all_rows=existing+[r]
    fd,tmp=tempfile.mkstemp(prefix='report_',suffix='.csv',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore')
            writer.writeheader();writer.writerows(all_rows)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def save_uploads(uploaded_files, folder, report_id, max_bytes=5*1024*1024):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    allow={'.jpg','.jpeg','.png','.pdf'}
    pending=[]
    for f in uploaded_files or []:
        ext=Path(f.name).suffix.lower()
        if ext not in allow: raise ValueError(f'ไม่รองรับไฟล์ประเภท: {ext}')
        body=f.getvalue()
        if len(body)>max_bytes: raise ValueError('ไฟล์แนบแต่ละไฟล์ต้องไม่เกิน 5 MB')
        if not body: raise ValueError('ไฟล์แนบต้องไม่ว่าง')
        pending.append((ext,body))
    names=[]
    for ext,body in pending:
        filename=f'{report_id}_{uuid.uuid4().hex[:10]}{ext}'
        (folder/filename).write_bytes(body)
        names.append(filename)
    return names
