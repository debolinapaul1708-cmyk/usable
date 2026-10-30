import os, io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Bid Workspace", page_icon="📄", layout="wide")
BASE_DIR=os.path.dirname(os.path.dirname(__file__))
BIDS_FILE=os.path.join(BASE_DIR,"data","sample_bids.csv")
FALLBACK="""bid_id,title,department,closing_date,bid_amount,min_turnover,min_experience_years,required_certifications,category
GOV-2026-001,Supply of Medical Equipment,Health Department,2026-11-02,4500000,10000000,5,"ISO 9001; GST",Medical Equipment
GOV-2026-002,Road Maintenance Contract,Public Works Department,2026-11-03,12000000,25000000,8,"GST; Contractor License",Infrastructure
GOV-2026-003,IT Hardware Procurement,Education Department,2026-11-04,2800000,5000000,3,"GST; ISO 27001",IT Hardware
GOV-2026-004,Office Furniture Supply,General Administration,2026-11-05,1500000,3000000,2,"GST",Furniture
GOV-2026-005,Laboratory Chemicals Supply,Science & Technology Department,2026-11-06,2200000,4000000,4,"GST; ISO 9001",Laboratory Supplies
GOV-2026-006,School Uniform Manufacturing,Education Department,2026-11-07,3600000,6000000,3,"GST; ISO 9001",Textiles
GOV-2026-007,Solar Street Light Installation,Urban Development Department,2026-11-08,8900000,15000000,6,"GST; MNRE Empanelment",Renewable Energy
GOV-2026-008,Desktop Computers Supply,Home Department,2026-11-09,5200000,8000000,4,"GST; ISO 27001",IT Hardware
GOV-2026-009,Water Purification Systems,Rural Development Department,2026-11-10,6700000,12000000,5,"GST; BIS Certification",Water Solutions
GOV-2026-010,Security Guard Services,Public Works Department,2026-11-11,4300000,7000000,5,"GST; PSARA License",Manpower Services
GOV-2026-011,Hospital Beds Supply,Health Department,2026-11-12,3100000,5000000,3,"GST; ISO 13485",Medical Equipment
GOV-2026-012,Bridge Repair Works,Public Works Department,2026-11-13,18500000,35000000,10,"GST; Contractor License",Infrastructure
GOV-2026-013,Library Books Supply,Education Department,2026-11-14,900000,1500000,2,"GST",Books & Publications
GOV-2026-014,CCTV Surveillance System,Home Department,2026-11-15,7400000,12000000,6,"GST; ISO 9001",Security Systems
GOV-2026-015,Electric Buses Procurement,Transport Department,2026-11-16,42000000,80000000,12,"GST; ARAI Certification",Electric Vehicles
GOV-2026-016,Waste Management Services,Municipal Corporation,2026-11-17,5600000,9000000,5,"GST; CPCB Authorization",Waste Management
GOV-2026-017,Agricultural Equipment Supply,Agriculture Department,2026-11-18,3800000,6500000,4,"GST; ISO 9001",Agriculture
GOV-2026-018,Cloud Hosting Services,IT Department,2026-11-19,9800000,18000000,7,"GST; ISO 27001",IT Services
GOV-2026-019,Fire Safety Equipment Supply,Home Department,2026-11-20,2400000,4000000,3,"GST; BIS Certification",Safety Equipment
GOV-2026-020,Park Development Works,Urban Development Department,2026-11-21,11200000,20000000,8,"GST; Contractor License",Infrastructure
"""

if not st.session_state.get("authenticated"):
    st.warning("Please sign in from the main page."); st.stop()

try: bids=pd.read_csv(BIDS_FILE)
except FileNotFoundError: bids=pd.read_csv(io.StringIO(FALLBACK))

st.title("📄 Bid Workspace")
selected=st.session_state.get("selected_bid",bids.iloc[0]["bid_id"])
bid=bids[bids["bid_id"]==selected].iloc[0]
p=st.session_state.get("profile",{"turnover":12000000,"experience":6,"certifications":"ISO 9001, GST","categories":"Medical Equipment, IT Hardware"})

st.subheader(bid["title"]); st.caption(f"{bid['bid_id']} • {bid['department']} • {bid['category']}")
c1,c2,c3,c4=st.columns(4)
c1.metric("Bid value",f"₹{bid['bid_amount']/100000:.1f} L"); c2.metric("Closing",bid["closing_date"])
c3.metric("Min turnover",f"₹{bid['min_turnover']/100000:.1f} L"); c4.metric("Experience",f"{bid['min_experience_years']} years")
st.divider(); left,right=st.columns([1.1,1])
with left:
    st.markdown("### Eligibility")
    req=[x.strip().lower() for x in str(bid["required_certifications"]).split(";")]
    certs=[x.strip().lower() for x in p["certifications"].split(",")]; cats=[x.strip().lower() for x in p["categories"].split(",")]
    missing=[x for x in req if x not in certs]
    checks=[("Turnover",p["turnover"]>=bid["min_turnover"],f"Required ₹{bid['min_turnover']:,.0f}"),("Experience",p["experience"]>=bid["min_experience_years"],f"Required {bid['min_experience_years']} years"),("Certifications",not missing,"All available" if not missing else "Missing: "+", ".join(missing)),("Category",str(bid["category"]).lower() in cats,f"Bid category: {bid['category']}")]
    score=int(sum(1 for _,ok,_ in checks if ok)/len(checks)*100); st.progress(score,text=f"Readiness: {score}%")
    for n,ok,d in checks: st.markdown(f"- {'✅' if ok else '❌'} **{n}** — {d}")
with right:
    st.markdown("### Upload documents")
    docs=st.file_uploader("Upload documents",type=["pdf","docx","jpg","jpeg","png","xlsx","csv"],accept_multiple_files=True)
    required={"Company registration":["registration","incorporation","company"],"GST certificate":["gst"],"Turnover certificate":["turnover","financial","balance"],"Experience certificate":["experience","work","completion"],"Technical specification":["technical","specification","catalog"]}
    names=[x.name.lower() for x in docs] if docs else []
    status=[{"Document":k,"Status":"✅ Uploaded" if any(any(y in n for y in v) for n in names) else "⏳ Pending"} for k,v in required.items()]
    st.dataframe(pd.DataFrame(status),use_container_width=True,hide_index=True)
    pending=[x["Document"] for x in status if "Pending" in x["Status"]]
    if st.button("Submit bid",type="primary",use_container_width=True):
        if pending: st.error("Pending: "+", ".join(pending))
        elif score<100: st.error("Resolve eligibility issues first.")
        else: st.success("Bid submitted successfully.")
