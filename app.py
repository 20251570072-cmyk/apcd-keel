
**Commit message:** `chore: add Python dependencies`

---

### 3. `app.py` (The KEEL Dashboard)

Create this file with exact content:

```python
import streamlit as st

st.set_page_config(page_title="KEEL | APCD Intelligence", layout="wide")

st.title("⚓ KEEL")
st.subheader("The Backbone of Smart Customs")

st.sidebar.header("KEEL Modules")
module = st.sidebar.radio("Select Module", [
    "🏠 Home",
    "🔍 KEEL Trust",
    "♻️ KEEL Circular",
    "👮 KEEL Field",
    "🔮 Future Keels"
])

if module == "🏠 Home":
    st.markdown("""
    ### Welcome to KEEL
    
    Every ship has a keel — the structural backbone that holds it upright.
    
    **KEEL** is APCD's intelligence backbone, powering three live modules:
    
    | Module | Function |
    |---|---|
    | **KEEL Trust** | Behavioral risk scoring for customs traders |
    | **KEEL Circular** | Industrial symbiosis & circular economy matching |
    | **KEEL Field** | Single-screen dashboard for port floor officers |
    
    *Built for the APCD AI Innovation Competition 2026*
    """)

elif module == "🔍 KEEL Trust":
    st.header("KEEL Trust — Behavioral Risk Scoring")
    st.info("🚧 Under construction — Week 2 deliverable")
    
    trader = st.selectbox("Select Trader", ["Demo Trader A", "Demo Trader B", "Demo Trader C"])
    if trader:
        col1, col2, col3 = st.columns(3)
        col1.metric("Trust Score", "87/100")
        col2.metric("Risk Tier", "🟢 LOW")
        col3.metric("Shipments (90d)", "24")
        
        st.subheader("Why this score?")
        st.write("• Regular shipper — consistent monthly volume")
        st.write("• HS code consistency — 94% same category")
        st.write("• On-time duty payments — zero delays")
        
        st.subheader("Feature Breakdown")
        st.bar_chart({
            "Frequency": 85,
            "Consistency": 94,
            "Payment": 92,
            "Value Stability": 78,
            "Origin Diversity": 45
        })

elif module == "♻️ KEEL Circular":
    st.header("KEEL Circular — Economy Matchmaker")
    st.info("🚧 Under construction — Week 3 deliverable")
    
    st.markdown("**AI-suggested partnerships based on import/export complementarity:**")
    
    st.dataframe({
        "Company A": ["Al Amin Plastics", "Gulf Metals"],
        "Imports": ["HS 3901 — Plastic pellets", "HS 2601 — Iron ore"],
        "Company B": ["Gulf Recycling", "SteelFab Ajman"],
        "Exports": ["HS 3915 — Plastic waste", "HS 7204 — Scrap steel"],
        "Match Score": ["94%", "89%"],
        "Symbiosis Type": ["Waste → Raw", "Scrap → Foundry"]
    })
    
    st.success("💡 Suggestion: Al Amin Plastics should source 40% of raw material from Gulf Recycling")

elif module == "👮 KEEL Field":
    st.header("KEEL Field — Officer Dashboard")
    st.info("🚧 Under construction — Week 3 deliverable")
    
    container = st.text_input("Enter Container ID", "AJM-2026-001")
    if container:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trust Score", "87")
        col2.metric("Risk Tier", "🟢 LOW")
        col3.metric("Safety", "✅ CLEAR")
        col4.metric("Dwell Time", "4.2 hrs")
        
        st.subheader("Shipment Intelligence")
        st.write("**Trader:** Al Amin Plastics (Trusted since 2019)")
        st.write("**Origin:** Mumbai, India")
        st.write("**HS Code:** 3901.20 — Polypropylene pellets")
        st.write("**Declared Value:** AED 45,000")
        
        st.subheader("Safety & Circular Alerts")
        st.success("✅ Non-hazardous cargo")
        st.info("♻️ Circular match: Gulf Recycling (94% compatibility)")
        
        st.button("🟢 Recommend Auto-Clearance", type="primary")

elif module == "🔮 Future Keels":
    st.header("Extensible Architecture")
    st.markdown("""
    The KEEL Core is designed to accept additional modules without disrupting live operations:
    
    | Module | Description | Data Required | Status |
    |---|---|---|---|
    | **KEEL Vision** | CV-based container seal integrity check | Port camera feeds | 🟡 Phase 2 |
    | **KEEL Routes** | Predictive maritime tracking & ETA | AIS vessel data | 🟡 Phase 2 |
    | **KEEL Flow** | Automated document workflow (RPA) | Form templates | 🟡 Phase 3 |
    
    *Each module plugs into the same SQLite core using standardized feature schemas.*
    """)

st.sidebar.markdown("---")
st.sidebar.caption("KEEL v0.1 | APCD Competition Build")
