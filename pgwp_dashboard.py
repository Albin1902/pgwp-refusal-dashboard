import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1ov2sXCFcwxxQ3Vc8_6kM7egCnk7FcNzUWjH2d32tJ2rLO1Yr9D9OdUP9PEArdWdcygJYax0BhXuv/pub?output=csv"

st.set_page_config(
    page_title="PGWP Refusal Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)

    # Clean columns and text values
    df.columns = df.columns.str.strip()
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    # Rename long Google Form headers to shorter internal names
    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Country of citizenship": "country",
        "Last 4 digits of your UCI (optional)": "uci_last4",
        "College / University attended": "college",
        "Program type": "program_type",
        "Program completion date": "completion_date",
        "Date PGWP application was submitted": "pgwp_submit_date",
        "Date of refusal": "refusal_date",
        "Which language test was used?": "language_test_type",
        "Was the language test taken BEFORE submitting the PGWP application?": "test_taken_before",
        "Language test date": "language_test_date",
        "CLB level or test score": "score",
        "Why was the language test not included in the application?": "missing_reason",
        "Did you contact IRCC BEFORE the refusal decision?": "contacted_ircc_before_refusal",
        "How soon after refusal was reconsideration requested?": "reconsideration_timing",
        "How many IRCC webforms were submitted requesting reconsideration?": "webform_count",
        "What documents were attached with reconsideration?": "attached_docs",
        "Was a clear explanation provided describing why the language test was missing?": "clear_explanation",
        "Did you apply for restoration of status?": "restoration_status",
        "Was a Member of Parliament contacted regarding reconsideration?": "mp_contacted",
        "What is the current status of your reconsideration request?": "reconsideration_status",
        "If decided, how long did it take to receive the reconsideration decision?": "decision_time"
    })

    return df

df = load_data()

# Manual refresh
if st.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

st.title("PGWP Refusal & Reconsideration Dashboard")
st.markdown(
    """
    Community-driven dashboard tracking PGWP refusals related to missing language test
    documents, reconsideration outcomes, restoration actions, and MP involvement.
    """
)
st.caption("Anonymous survey-based data for community trend analysis. Data refreshes automatically every 60 seconds.")

# Sidebar filters
st.sidebar.title("Filters")
st.sidebar.caption("Use these to explore the responses.")

def get_options(series):
    return ["All"] + sorted([str(x) for x in series.dropna().unique().tolist()])

country_options = get_options(df["country"])
program_options = get_options(df["program_type"])
status_options = get_options(df["reconsideration_status"])
test_options = get_options(df["language_test_type"])

selected_country = st.sidebar.selectbox("Country", country_options)
selected_program = st.sidebar.selectbox("Program Type", program_options)
selected_status = st.sidebar.selectbox("Reconsideration Status", status_options)
selected_test = st.sidebar.selectbox("Language Test", test_options)

filtered_df = df.copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["country"] == selected_country]

if selected_program != "All":
    filtered_df = filtered_df[filtered_df["program_type"] == selected_program]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df["reconsideration_status"] == selected_status]

if selected_test != "All":
    filtered_df = filtered_df[filtered_df["language_test_type"] == selected_test]

# Metrics
approved_count = (filtered_df["reconsideration_status"] == "Approved").sum()
refused_count = (filtered_df["reconsideration_status"] == "Refused").sum()
pending_count = (filtered_df["reconsideration_status"] == "Still waiting").sum()

decided_df = filtered_df[filtered_df["reconsideration_status"].isin(["Approved", "Refused"])]
success_rate = 0.0
if len(decided_df) > 0:
    success_rate = round((decided_df["reconsideration_status"] == "Approved").mean() * 100, 1)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Responses", len(filtered_df))
m2.metric("Approved", int(approved_count))
m3.metric("Pending", int(pending_count))
m4.metric("Approval Rate", f"{success_rate}%")

# Helpers
def count_df(series, x_name="Category", y_name="Count"):
    vc = series.fillna("Unknown").astype(str).value_counts().reset_index()
    vc.columns = [x_name, y_name]
    return vc

# Row 1
c1, c2 = st.columns(2)

with c1:
    fig1 = px.pie(
        count_df(filtered_df["test_taken_before"], "Test Taken Before", "Count"),
        names="Test Taken Before",
        values="Count",
        title="Language Test Taken Before PGWP Application"
    )
    fig1.update_layout(legend_title_text="")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.pie(
        count_df(filtered_df["missing_reason"], "Missing Reason", "Count"),
        names="Missing Reason",
        values="Count",
        title="Why the Language Test Was Missing"
    )
    fig2.update_layout(legend_title_text="")
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
c3, c4 = st.columns(2)

with c3:
    fig3 = px.bar(
        count_df(filtered_df["reconsideration_status"], "Reconsideration Status", "Count"),
        x="Reconsideration Status",
        y="Count",
        title="Reconsideration Outcomes",
        text="Count"
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    fig4 = px.bar(
        count_df(filtered_df["mp_contacted"], "MP Contacted", "Count"),
        x="MP Contacted",
        y="Count",
        title="MP Involvement",
        text="Count"
    )
    st.plotly_chart(fig4, use_container_width=True)

# Row 3
c5, c6 = st.columns(2)

with c5:
    fig5 = px.bar(
        count_df(filtered_df["reconsideration_timing"], "Timing", "Count"),
        x="Timing",
        y="Count",
        title="How Soon Reconsideration Was Requested",
        text="Count"
    )
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    fig6 = px.bar(
        count_df(filtered_df["webform_count"], "Webforms Submitted", "Count"),
        x="Webforms Submitted",
        y="Count",
        title="Number of IRCC Webforms Submitted",
        text="Count"
    )
    st.plotly_chart(fig6, use_container_width=True)

# Row 4
c7, c8 = st.columns(2)

with c7:
    fig7 = px.bar(
        count_df(filtered_df["restoration_status"], "Restoration Applied", "Count"),
        x="Restoration Applied",
        y="Count",
        title="Restoration Status",
        text="Count"
    )
    st.plotly_chart(fig7, use_container_width=True)

with c8:
    fig8 = px.bar(
        count_df(filtered_df["contacted_ircc_before_refusal"], "Contacted IRCC Before Refusal", "Count"),
        x="Contacted IRCC Before Refusal",
        y="Count",
        title="IRCC Contact Before Refusal",
        text="Count"
    )
    st.plotly_chart(fig8, use_container_width=True)

# Advanced analysis 1
st.subheader("Approval Outcome by MP Involvement")
mp_outcome_df = (
    filtered_df.groupby(["mp_contacted", "reconsideration_status"])
    .size()
    .reset_index(name="count")
)

if not mp_outcome_df.empty:
    fig_mp_outcome = px.bar(
        mp_outcome_df,
        x="mp_contacted",
        y="count",
        color="reconsideration_status",
        barmode="group",
        title="Outcome vs MP Involvement",
        labels={
            "mp_contacted": "MP Contacted",
            "count": "Cases",
            "reconsideration_status": "Outcome"
        }
    )
    st.plotly_chart(fig_mp_outcome, use_container_width=True)

# Advanced analysis 2
st.subheader("Reconsideration Timing vs Outcome")
timing_outcome_df = (
    filtered_df.groupby(["reconsideration_timing", "reconsideration_status"])
    .size()
    .reset_index(name="count")
)

if not timing_outcome_df.empty:
    fig_timing_outcome = px.bar(
        timing_outcome_df,
        x="reconsideration_timing",
        y="count",
        color="reconsideration_status",
        barmode="group",
        title="How Fast Reconsideration Was Requested vs Outcome",
        labels={
            "reconsideration_timing": "Timing",
            "count": "Cases",
            "reconsideration_status": "Outcome"
        }
    )
    st.plotly_chart(fig_timing_outcome, use_container_width=True)

# Raw data + download
st.subheader("Download Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="pgwp_filtered_data.csv",
    mime="text/csv"
)

with st.expander("Show raw data"):
    st.dataframe(filtered_df, use_container_width=True)
