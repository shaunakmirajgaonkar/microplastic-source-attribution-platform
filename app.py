
from pathlib import Path
import pandas as pd, numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="MicroSource Local",page_icon="🧪",layout="wide")
DATA_PATH=Path("data/synthetic_microplastic_source_registry.csv")
REQUIRED_COLUMNS=['record_id', 'river_zone', 'observation_date', 'rainfall_24h_mm', 'upstream_drainage_score', 'industrial_proximity_score', 'industrial_discharge_signal', 'urban_land_use_score', 'waste_management_score', 'stormwater_density_score', 'wastewater_influence_score', 'river_flow_score', 'plastic_waste_load_score', 'microplastic_observation_score', 'sampling_distance_km', 'source_type', 'review_status']

st.markdown("""<style>
.stApp{background:#f6f9fa;color:#182d35}.block-container{max-width:1500px;padding:1.2rem 2rem 3rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #dbe6ea}[data-testid="stSidebar"] *{color:#21343d!important}
.hero{background:linear-gradient(135deg,#fff 0%,#eef8f6 55%,#f0f6fb 100%);border:1px solid #d8e5e8;border-radius:28px;padding:30px 34px;margin-bottom:18px;box-shadow:0 14px 36px rgba(35,67,77,.07)}
.hero h1{color:#17343d;font-size:2.55rem;letter-spacing:-.04em;margin:14px 0 8px}.hero p{color:#586c74;line-height:1.65}
.pill{display:inline-block;padding:7px 12px;margin-right:6px;border-radius:999px;background:#eaf6f3;border:1px solid #cde7e0;color:#21665a;font-size:.72rem;font-weight:800}
.panel{background:#fff;border:1px solid #dce7ea;border-radius:20px;padding:20px;margin:12px 0;box-shadow:0 7px 20px rgba(35,67,77,.04)}
.info{background:#f2f8fb;border:1px solid #d6e6ee;border-radius:16px;padding:15px;color:#385763}.warn{background:#fff9ec;border:1px solid #ead9a7;border-radius:16px;padding:15px;color:#67551f}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dce7ea;border-radius:18px;padding:12px 16px}h2,h3{color:#1d3740!important}
</style>""",unsafe_allow_html=True)

def score(r):
    rain=np.clip(float(r.rainfall_24h_mm)/75*100,0,100)
    v=[float(r.upstream_drainage_score),float(r.industrial_proximity_score),float(r.industrial_discharge_signal),float(r.urban_land_use_score),float(r.stormwater_density_score),float(r.wastewater_influence_score),float(r.plastic_waste_load_score),rain,float(r.microplastic_observation_score)]
    s=round(float(np.clip(.14*v[0]+.16*v[1]+.12*v[2]+.12*v[3]+.13*v[4]+.10*v[5]+.10*v[6]+.08*v[7]+.05*v[8],0,100)),1)
    band="Low Review" if s<30 else "Moderate Review" if s<55 else "High Review" if s<75 else "Critical Review"
    reasons=[]
    if v[1]>=70: reasons.append("strong industrial-proximity signal")
    if v[2]>=60: reasons.append("elevated industrial-discharge signal")
    if v[4]>=70: reasons.append("dense stormwater-drainage signal")
    if v[3]>=70: reasons.append("high urban land-use signal")
    if v[5]>=70: reasons.append("strong wastewater-influence signal")
    if v[6]>=70: reasons.append("high plastic-waste-load signal")
    if rain>=65: reasons.append("recent rainfall signal")
    if v[8]>=60: reasons.append("elevated local microplastic observation signal")
    return s,band,"; ".join(reasons) or "No strong source signal under local screening rules."

df=pd.read_csv(DATA_PATH)
missing=[c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing: st.error("Missing required columns: "+", ".join(missing)); st.stop()
x=df.apply(score,axis=1,result_type="expand"); x.columns=["source_screening_score","review_band","factor_explanation"]; df=pd.concat([df.reset_index(drop=True),x],axis=1)

st.sidebar.markdown("## 🧪 MicroSource Local"); st.sidebar.caption("River microplastic source screening")
page=st.sidebar.radio("Workspace",["Source Attribution Command Center","River Zone Explorer","Source Signals","Record Review","Local Data Lab","Responsible Use"])
st.sidebar.markdown("---"); st.sidebar.caption("100% local processing"); st.sidebar.caption("No external APIs"); st.sidebar.caption("Synthetic or authorized records only")

st.markdown("""<div class="hero"><span class="pill">LOCAL-FIRST</span><span class="pill">SOURCE SCREENING</span><span class="pill">EXPLAINABLE</span><span class="pill">HUMAN REVIEW</span>
<h1>🧪 MicroSource Local</h1><p><b>Microplastic Source Attribution Platform</b> — screen river records for potential source signals using drainage networks, nearby industrial activity, rainfall, land use, stormwater, wastewater, waste loads, and local observations.</p>
<p>Results are source-screening signals, not proof of origin, transport pathway, regulatory non-compliance, or attribution to a specific organization.</p></div>""",unsafe_allow_html=True)

if page=="Source Attribution Command Center":
    a,b,c,d,e=st.columns(5); a.metric("River records",len(df)); b.metric("Average score",f"{df.source_screening_score.mean():.0f}/100"); c.metric("High/Critical",int((df.source_screening_score>=55).sum())); d.metric("Industrial signals",int((df.industrial_proximity_score>=70).sum())); e.metric("Stormwater signals",int((df.stormwater_density_score>=70).sum()))
    l,r=st.columns(2)
    with l:
        q=df.groupby("river_zone",as_index=False).source_screening_score.mean().sort_values("source_screening_score",ascending=False)
        fig=px.bar(q,x="river_zone",y="source_screening_score",title="Source-screening score by river zone"); fig.update_layout(template="plotly_white",height=360); st.plotly_chart(fig,use_container_width=True)
    with r:
        fig=px.scatter(df,x="industrial_proximity_score",y="source_screening_score",size="plastic_waste_load_score",color="review_band",hover_name="river_zone",title="Industrial proximity vs source-screening score"); fig.update_layout(template="plotly_white",height=360); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="warn"><b>Interpretation:</b> Higher scores indicate records with more contributing source signals. They do not establish that a particular source caused observed microplastic pollution.</div>',unsafe_allow_html=True)
    st.dataframe(df[["record_id","river_zone","rainfall_24h_mm","industrial_proximity_score","stormwater_density_score","wastewater_influence_score","plastic_waste_load_score","source_screening_score","review_band"]].sort_values("source_screening_score",ascending=False),use_container_width=True,hide_index=True)

elif page=="River Zone Explorer":
    st.subheader("River-zone source profile"); zone=st.selectbox("River zone",["All zones"]+sorted(df.river_zone.astype(str).unique())); view=df if zone=="All zones" else df[df.river_zone==zone]
    a,b,c=st.columns(3); a.metric("Records in view",len(view)); b.metric("Mean score",f"{view.source_screening_score.mean():.0f}/100"); c.metric("Mean observed signal",f"{view.microplastic_observation_score.mean():.0f}/100")
    fig=px.scatter(view,x="upstream_drainage_score",y="plastic_waste_load_score",size="rainfall_24h_mm",color="review_band",hover_name="river_zone",title="Drainage influence vs plastic-waste load"); fig.update_layout(template="plotly_white",height=450); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(view[["record_id","river_zone","rainfall_24h_mm","upstream_drainage_score","urban_land_use_score","industrial_proximity_score","wastewater_influence_score","plastic_waste_load_score","source_screening_score","review_band"]],use_container_width=True,hide_index=True)

elif page=="Source Signals":
    st.subheader("Potential source-signal comparison"); signal_cols=["industrial_proximity_score","industrial_discharge_signal","urban_land_use_score","stormwater_density_score","wastewater_influence_score","plastic_waste_load_score"]
    m=df[signal_cols].mean().reset_index(); m.columns=["signal","mean_score"]; fig=px.bar(m,x="signal",y="mean_score",title="Average source signals across the registry"); fig.update_layout(template="plotly_white",height=420,xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True)
    fig=px.scatter(df,x="rainfall_24h_mm",y="source_screening_score",size="upstream_drainage_score",color="review_band",hover_name="river_zone",title="Rainfall vs source-screening score"); fig.update_layout(template="plotly_white",height=420); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="info"><b>Review approach:</b> Compare multiple independent local signals before drawing conclusions. Source attribution normally requires validated sampling, hydrological context, laboratory analysis, and qualified ecological assessment.</div>',unsafe_allow_html=True)

elif page=="Record Review":
    st.subheader("River record review"); selected=st.selectbox("Select record",df.record_id.astype(str).tolist()); r=df[df.record_id.astype(str)==selected].iloc[0]
    a,b,c,d=st.columns(4); a.metric("Screening score",f"{r.source_screening_score:.0f}/100"); b.metric("Review band",r.review_band); c.metric("Rainfall",f"{r.rainfall_24h_mm:.0f} mm"); d.metric("Observation",f"{r.microplastic_observation_score:.0f}/100")
    st.markdown('<div class="warn"><b>Attribution boundary:</b> This record review identifies combinations of potential source signals. It does not identify a confirmed pollution source.</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); st.write(f"**River zone:** {r.river_zone} • **Source type:** {r.source_type}"); st.write(f"**Industrial proximity:** {r.industrial_proximity_score}/100 • **Stormwater:** {r.stormwater_density_score}/100 • **Wastewater:** {r.wastewater_influence_score}/100"); st.write(f"**Urban land use:** {r.urban_land_use_score}/100 • **Waste load:** {r.plastic_waste_load_score}/100 • **Drainage:** {r.upstream_drainage_score}/100"); st.write(f"**Factor explanation:** {r.factor_explanation}"); st.markdown("</div>",unsafe_allow_html=True)

elif page=="Local Data Lab":
    st.subheader("CSV validation and local replacement"); st.write("CSV files are processed locally and validated before replacement."); st.code(", ".join(REQUIRED_COLUMNS),language="text")
    up=st.file_uploader("Replace local microplastic source registry",type=["csv"])
    if up:
        try:
            nd=pd.read_csv(up); miss=[c for c in REQUIRED_COLUMNS if c not in nd.columns]
            if miss: st.error("Missing required columns: "+", ".join(miss))
            elif nd.empty: st.error("The uploaded CSV contains no records.")
            else: nd.to_csv(DATA_PATH,index=False); st.success(f"Validated and loaded {len(nd):,} records."); st.rerun()
        except Exception as e: st.error(f"CSV validation failed: {e}")
    st.markdown("### Current local registry"); st.dataframe(df[REQUIRED_COLUMNS],use_container_width=True,hide_index=True)
    st.download_button("Download scored source registry",df.drop(columns=["factor_explanation"],errors="ignore").to_csv(index=False).encode(),"microplastic_source_scored.csv","text/csv")

else:
    st.subheader("Responsible use")
    st.markdown("""<div class="panel"><h3>Source screening, not source proof</h3><ul>
    <li>Use synthetic or authorized environmental records only.</li><li>Do not publish sensitive locations of protected species or vulnerable habitats.</li>
    <li>Do not attribute pollution to a company, facility, vessel, or community from screening scores alone.</li>
    <li>Use qualified hydrological, ecological, laboratory, and regulatory assessment for confirmed attribution.</li>
    <li>Consider rainfall, river flow, drainage connectivity, land use, sampling design, and measurement uncertainty.</li>
    </ul></div>""",unsafe_allow_html=True)
st.markdown("---"); st.caption("MicroSource Local • 100% local processing • No external APIs • Environmental source-screening decision support")
