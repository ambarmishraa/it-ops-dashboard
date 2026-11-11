"""IT Operations Dashboard (Streamlit). Run: streamlit run app.py"""
import altair as alt
import streamlit as st

import generate_data
import queries

st.set_page_config(page_title="IT Operations Dashboard", layout="wide")

if not queries.DB_PATH.exists():
    generate_data.main()

st.title("IT Operations Dashboard")
st.caption("Synthetic incident data (randomly generated) used to practise SQL, Pandas and dashboarding.")

with st.sidebar:
    st.header("Filters")
    start = st.date_input("From", value=__import__("datetime").date(2025, 11, 1))
    end = st.date_input("To", value=__import__("datetime").date(2026, 11, 1))
    platform = st.multiselect("Platform (applications table)", ["SAP", "Web", "Cloud", "SaaS", "Network"],
                              default=["SAP", "Web", "Cloud", "SaaS", "Network"])

args = dict(start=str(start), end=str(end))
kpi = queries.run(queries.KPIS, **args).iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Incidents", int(kpi.total_incidents))
c2.metric("Currently open", int(kpi.open_incidents or 0))
c3.metric("Avg. resolution (h)", kpi.avg_resolution_hours)
c4.metric("SLA met (%)", kpi.sla_met_pct)

by_app = queries.run(queries.BY_APPLICATION, **args)
by_app = by_app[by_app["platform"].isin(platform)]

left, right = st.columns(2)
with left:
    st.subheader("Incidents per month")
    monthly = queries.run(queries.MONTHLY, **args)
    st.altair_chart(alt.Chart(monthly).mark_line(point=True).encode(
        x=alt.X("month:O", title="Month"), y=alt.Y("incidents:Q", title="Incidents")), use_container_width=True)
with right:
    st.subheader("Incidents by category")
    cat = queries.run(queries.BY_CATEGORY, **args)
    st.altair_chart(alt.Chart(cat).mark_bar().encode(
        x=alt.X("incidents:Q"), y=alt.Y("category:N", sort="-x", title="")), use_container_width=True)

st.subheader("Applications: volume, resolution time and SLA")
st.dataframe(by_app, use_container_width=True, hide_index=True)

st.subheader("Priority and SLA targets")
st.dataframe(queries.run(queries.BY_PRIORITY, **args), use_container_width=True, hide_index=True)
