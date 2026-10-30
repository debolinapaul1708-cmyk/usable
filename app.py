import hashlib, io, json, os, re
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ProcureIQ", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

BASE_DIR=os.path.dirname(__file__)
USERS_FILE=os.path.join(BASE_DIR,"users.json")
UPLOAD_DIR=os.path.join(BASE_DIR,"uploads")
BIDS_FILE=os.path.join(BASE_DIR,"data","sample_bids.csv")
os.makedirs(UPLOAD_DIR,exist_ok=True)
FALLBACK_BIDS="""bid_id,title,department,closing_date,bid_amount,min_turnover,min_experience_years,required_certifications,category
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

if "authenticated" not in st.session_state: st.session_state.authenticated=False
if "user" not in st.session_state: st.session_state.user=None
if "profile" not in st.session_state:
    st.session_state.profile={"turnover":12000000,"experience":6,"certifications":"ISO 9001, GST","categories":"Medical Equipment, IT Hardware"}

@st.cache_data
def load_bids():
    try: return pd.read_csv(BIDS_FILE)
    except FileNotFoundError: return pd.read_csv(io.StringIO(FALLBACK_BIDS))

def css():
    st.markdown("""<style>
    .block-container{padding-top:1.5rem}
    section[data-testid="stSidebar"]{background:#0b1220}
    section[data-testid="stSidebar"] *{color:#e2e8f0!important}
    div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:18px;box-shadow:0 6px 18px rgba(15,23,42,.06)}
    .hero{background:linear-gradient(120deg,#0f172a,#1d4ed8);color:white;padding:32px;border-radius:22px}
    .hero h1{margin:0}.hero p{opacity:.9}
    </style>""",unsafe_allow_html=True)

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,encoding="utf-8") as f: return json.load(f)
    return {}

def save_users(u):
    with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(u,f,indent=2)

def auth_screen():
    st.markdown('<div class="hero"><h1>🏛️ ProcureIQ</h1><p>Sign in to access your procurement dashboard.</p></div>',unsafe_allow_html=True)
    left,right=st.columns([1,1])
    with left:
        st.subheader("Sign in")
        with st.form("login"):
            email=st.text_input("Email"); password=st.text_input("Password",type="password")
            if st.form_submit_button("Sign in",use_container_width=True,type="primary"):
                users=load_users()
                if email in users and users[email]["password"]==hash_password(password):
                    st.session_state.authenticated=True
                    st.session_state.user={"email":email,"name":users[email]["name"]}
                    st.rerun()
                else: st.error("Invalid email or password.")
        st.caption("New supplier? Create an account on the right.")
    with right:
        st.subheader("Create account")
        with st.form("signup"):
            name=st.text_input("Full name"); company=st.text_input("Company name")
            email=st.text_input("Email"); password=st.text_input("Password",type="password")
            confirm=st.text_input("Confirm password",type="password")
            if st.form_submit_button("Create account",use_container_width=True):
                users=load_users()
                if not name or not company or not email: st.error("Complete all fields.")
                elif email in users: st.error("Account already exists.")
                elif len(password)<6: st.error("Password must have 6+ characters.")
                elif password!=confirm: st.error("Passwords do not match.")
                else:
                    users[email]={"name":name,"company":company,"password":hash_password(password),"created_at":datetime.now().isoformat()}
                    save_users(users); st.success("Account created. Please sign in.")

def sidebar():
    with st.sidebar:
        st.markdown("## 🏛️ ProcureIQ")
        st.caption(f"Signed in as **{st.session_state.user['name']}**")
        page=st.radio("Explore",["🏠 Dashboard","🔍 Browse Tenders","📄 Bid Workspace","📊 Analytics","👤 Supplier Profile"],label_visibility="collapsed")
        st.divider()
        p=st.session_state.profile
        p["turnover"]=st.number_input("Annual turnover (₹)",0,value=int(p["turnover"]),step=100000)
        p["experience"]=st.number_input("Experience (years)",0,value=int(p["experience"]))
        p["certifications"]=st.text_input("Certifications",p["certifications"])
        p["categories"]=st.text_input("Preferred categories",p["categories"])
        st.session_state.profile=p
        st.divider()
        if st.button("Sign out",use_container_width=True):
            st.session_state.authenticated=False; st.session_state.user=None; st.rerun()
    return page

def dashboard():
    bids=load_bids()
    st.markdown('<div class="hero"><h1>Welcome back 👋</h1><p>Explore opportunities and prepare your bids.</p></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Active tenders",len(bids)); c2.metric("Departments",bids["department"].nunique())
    c3.metric("Categories",bids["category"].nunique()); c4.metric("Total value",f"₹{bids['bid_amount'].sum()/10000000:.1f} Cr")
    st.subheader("Recommended opportunities")
    p=st.session_state.profile
    certs=[x.strip().lower() for x in p["certifications"].split(",")]
    cats=[x.strip().lower() for x in p["categories"].split(",")]
    bids["match"]=bids.apply(lambda r:(p["turnover"]>=r["min_turnover"])+(p["experience"]>=r["min_experience_years"])+(2 if str(r["category"]).lower() in cats else 0)+(1 if all(c in certs for c in str(r["required_certifications"]).lower().split(";")) else 0),axis=1)
    for _,r in bids.sort_values(["match","bid_amount"],ascending=[False,True]).head(6).iterrows():
        with st.container(border=True):
            a,b,c=st.columns([4,1.2,1])
            with a: st.markdown(f"**{r['title']}**"); st.caption(f"{r['bid_id']} • {r['department']} • {r['category']}")
            with b: st.metric("Value",f"₹{r['bid_amount']/100000:.1f} L")
            with c: st.metric("Match",f"{min(r['match']*20,100)}%")
            st.progress(min(r["match"]*20,100))

def browse():
    bids=load_bids(); st.title("🔍 Browse Tenders")
    c1,c2,c3=st.columns([2.2,1,1])
    search=c1.text_input("Search"); departments=["All departments"]+sorted(bids["department"].unique()); categories=["All categories"]+sorted(bids["category"].unique())
    dept=c2.selectbox("Department",departments); cat=c3.selectbox("Category",categories)
    f=bids.copy()
    if search: f=f[f["title"].str.contains(search,case=False,na=False)|f["department"].str.contains(search,case=False,na=False)|f["category"].str.contains(search,case=False,na=False)]
    if dept!="All departments": f=f[f["department"]==dept]
    if cat!="All categories": f=f[f["category"]==cat]
    st.info(f"Showing **{len(f)}** of **{len(bids)}** tenders.")
    for _,r in f.iterrows():
        with st.container(border=True):
            a,b,c,d=st.columns([4,1.2,1.2,1])
            with a: st.markdown(f"### {r['title']}"); st.caption(f"{r['bid_id']} • {r['department']} • {r['category']}"); st.write(f"₹{r['min_turnover']:,.0f} turnover • {r['min_experience_years']} years • {r['required_certifications']}")
            with b: st.metric("Value",f"₹{r['bid_amount']/100000:.1f} L")
            with c: st.metric("Closes",r["closing_date"])
            with d:
                if st.button("Open",key=r["bid_id"],use_container_width=True):
                    st.session_state.selected_bid=r["bid_id"]; st.switch_page("pages/2_📄_Bid_Workspace.py")

def workspace():
    st.title("📄 Bid Workspace"); bids=load_bids(); p=st.session_state.profile
    selected=st.session_state.get("selected_bid",bids.iloc[0]["bid_id"]); bid=bids[bids["bid_id"]==selected].iloc[0]
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

def analytics():
    bids=load_bids(); st.title("📊 Analytics")
    a,b=st.columns(2)
    with a: st.subheader("Tenders by department"); st.bar_chart(bids.groupby("department")["bid_id"].count())
    with b: st.subheader("Value by category"); st.bar_chart(bids.groupby("category")["bid_amount"].sum()/100000)
    st.subheader("Bid values"); st.bar_chart(bids.set_index("title")["bid_amount"]/100000)
    st.dataframe(bids[["bid_id","title","department","category","closing_date","bid_amount"]],use_container_width=True,hide_index=True)

def profile():
    st.title("👤 Supplier Profile"); p=st.session_state.profile
    c1,c2=st.columns(2)
    c1.metric("Turnover",f"₹{p['turnover']:,.0f}"); c1.metric("Experience",f"{p['experience']} years")
    c2.metric("Certifications",p["certifications"]); c2.metric("Categories",p["categories"])
    st.info("Update details in the sidebar to recalculate eligibility.")

css()
if not st.session_state.authenticated: auth_screen()
else:
    page=sidebar()
    if page=="🏠 Dashboard": dashboard()
    elif page=="🔍 Browse Tenders": browse()
    elif page=="📄 Bid Workspace": workspace()
    elif page=="📊 Analytics": analytics()
    else: profile()
