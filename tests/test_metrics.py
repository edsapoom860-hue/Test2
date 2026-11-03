import pandas as pd
from src.metrics import compute_kpis, monthly_counts

def test_kpi_total_and_company():
    df=pd.DataFrame([{'talk_date':'2026-10-01','participants':'10','company':'UBE'},{'talk_date':'2026-10-02','participants':'8','company':'UBS'}])
    assert compute_kpis(df)=={'talks':2,'participants':18,'UBE':1,'UBS':1}
    assert monthly_counts(df)['จำนวนกิจกรรม'].iloc[0]==2
