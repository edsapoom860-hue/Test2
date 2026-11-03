"""Instructor reference — fully local Day 1 Safety Talk demo, not production."""
from datetime import date, datetime
from pathlib import Path
import io, json
import pandas as pd
import streamlit as st
from src.validation import validate_report
from src.storage import FIELDS, load_records, next_report_id, append_report, save_uploads
from src.metrics import compute_kpis, monthly_counts

BASE=Path(__file__).resolve().parent
REPORTS=BASE/'data'/'reports.csv'
SAMPLE=BASE/'data'/'sample_safety_talk.csv'
DEPTS=json.loads((BASE/'config'/'departments.json').read_text(encoding='utf-8'))
st.set_page_config(page_title='UBE Safety Talk — Workshop',page_icon='🦺',layout='wide')
st.title('UBE Safety Talk | Workshop Day 1')
st.caption('ต้นแบบเพื่อการอบรม • ทดสอบในเครื่อง • ไม่ใช่ระบบจริงของ UBE')
with st.sidebar:
    st.header('UBE Safety Talk')
    page=st.radio('เมนู',['บันทึก Safety Talk','Dashboard','ประวัติรายงาน'])
    st.caption('Local training only — ห้ามใช้ข้อมูลจริง')

def load_df(demo_fallback=False):
    data=load_records(REPORTS)
    demo=False
    if not data and demo_fallback:
        data=load_records(SAMPLE);demo=True
    return pd.DataFrame(data,columns=FIELDS),demo

if page=='บันทึก Safety Talk':
    st.subheader('แบบฟอร์มบันทึก Safety Talk')
    company=st.selectbox('บริษัท',['UBE','UBS'])
    with st.form('talk_form',clear_on_submit=False):
        a,b=st.columns(2)
        with a:
            talk_date=st.date_input('วันที่สื่อสาร *',value=date.today())
            dept=st.selectbox('หน่วยงาน *',DEPTS[company])
            reporter=st.text_input('ชื่อผู้รายงาน *',placeholder='ชื่อผู้สาธิต')
        with b:
            topic=st.text_input('หัวข้อ Safety Talk *')
            participants=st.number_input('จำนวนผู้เข้าร่วม *',min_value=0,value=0,step=1)
            attachments=st.file_uploader('หลักฐาน JPG/PNG/PDF (ไม่เกิน 5 MB ต่อไฟล์)',type=['jpg','jpeg','png','pdf'],accept_multiple_files=True)
        submitted=st.form_submit_button('บันทึกรายงาน',type='primary')
    if submitted:
        errors=validate_report(talk_date,company,dept,reporter,topic,int(participants),DEPTS)
        if errors:
            for error in errors: st.error(error)
        else:
            try:
                existing=load_records(REPORTS)
                rid=next_report_id(existing,talk_date)
                filenames=save_uploads(attachments,BASE/'data'/'uploads',rid)
                report={'report_id':rid,'talk_date':talk_date.isoformat(),'company':company,'department':dept,'reporter':reporter.strip(),'topic':topic.strip(),'participants':str(int(participants)),'evidence_files':json.dumps(filenames,ensure_ascii=False),'created_at':datetime.now().isoformat(timespec='seconds')}
                append_report(REPORTS,report)
                st.success('บันทึกรายงานสำเร็จ')
                st.code(rid,language=None)
            except Exception as e: st.error(f'ไม่สามารถบันทึกข้อมูล: {e}')
else:
    df,demo=load_df(demo_fallback=(page=='Dashboard'))
    if demo: st.info('DEMO: กำลังแสดงข้อมูลสมมติจาก sample_safety_talk.csv เพราะยังไม่มีรายงานจริงในโปรเจกต์')
    if page=='Dashboard':
        st.subheader('Dashboard: สรุปข้อมูล Safety Talk')
        cc,yy,mm=st.columns(3)
        with cc: comp=st.selectbox('บริษัท',['ทั้งหมด','UBE','UBS'])
        df['date_dt']=pd.to_datetime(df.talk_date,errors='coerce')
        years=sorted([int(y) for y in df.date_dt.dt.year.dropna().unique()],reverse=True)
        with yy: year=st.selectbox('ปี',['ทั้งหมด']+years)
        with mm: month=st.selectbox('เดือน',['ทั้งหมด']+list(range(1,13)),format_func=lambda x: 'ทั้งหมด' if x=='ทั้งหมด' else f'{int(x):02d}')
        filt=df.copy()
        if comp!='ทั้งหมด':filt=filt[filt.company==comp]
        depts=sorted(set(filt.department.dropna()))
        dep=st.selectbox('หน่วยงาน',['ทั้งหมด']+depts)
        if dep!='ทั้งหมด':filt=filt[filt.department==dep]
        if year!='ทั้งหมด':filt=filt[filt.date_dt.dt.year==int(year)]
        if month!='ทั้งหมด':filt=filt[filt.date_dt.dt.month==int(month)]
        k=compute_kpis(filt)
        c1,c2,c3,c4=st.columns(4)
        c1.metric('กิจกรรมทั้งหมด',k['talks']);c2.metric('ผู้เข้าร่วมทั้งหมด',k['participants']);c3.metric('UBE',k['UBE']);c4.metric('UBS',k['UBS'])
        trend=monthly_counts(filt)
        st.subheader('แนวโน้มกิจกรรมรายเดือน')
        if trend.empty: st.warning('ไม่มีข้อมูลในช่วงที่เลือก')
        else: st.bar_chart(trend.set_index('เดือน'))
    else:
        st.subheader('ประวัติรายงาน Safety Talk')
        if df.empty:
            st.info('ยังไม่มีข้อมูลที่บันทึก ให้เริ่มจากเมนูบันทึก Safety Talk')
        else:
            query=st.text_input('ค้นหา Report ID / หัวข้อ / ผู้รายงาน')
            comp=st.selectbox('บริษัท',['ทั้งหมด','UBE','UBS'])
            filt=df.copy()
            if comp!='ทั้งหมด':filt=filt[filt.company==comp]
            if query.strip():
                q=query.strip()
                filt=filt[filt[['report_id','topic','reporter']].fillna('').astype(str).apply(lambda col:col.str.contains(q,case=False,regex=False)).any(axis=1)]
            st.dataframe(filt[FIELDS],hide_index=True,use_container_width=True)
            data=filt[FIELDS].to_csv(index=False).encode('utf-8-sig')
            st.download_button('ดาวน์โหลด CSV ที่กรองแล้ว',data=data,file_name=f'SafetyTalk_{date.today():%Y%m%d}.csv',mime='text/csv')
