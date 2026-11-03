import pandas as pd

def compute_kpis(df):
    if df.empty: return {'talks':0,'participants':0,'UBE':0,'UBS':0}
    ppl=pd.to_numeric(df.get('participants',pd.Series(dtype=float)),errors='coerce').fillna(0).clip(lower=0)
    return {'talks':len(df),'participants':int(ppl.sum()),'UBE':int((df.company=='UBE').sum()),'UBS':int((df.company=='UBS').sum())}

def monthly_counts(df):
    if df.empty: return pd.DataFrame({'เดือน':[],'จำนวนกิจกรรม':[]})
    temp=df.copy()
    temp['parsed_date']=pd.to_datetime(temp['talk_date'],errors='coerce')
    temp=temp.dropna(subset=['parsed_date'])
    if temp.empty: return pd.DataFrame({'เดือน':[],'จำนวนกิจกรรม':[]})
    grp=temp.groupby(temp['parsed_date'].dt.to_period('M')).size()
    return pd.DataFrame({'เดือน':grp.index.astype(str),'จำนวนกิจกรรม':grp.values})
