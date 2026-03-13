import streamlit as st
import pandas as pd
import plotly.express as px

# Replace with your actual published Google Sheets CSV link
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1ov2sXCFcwxxQ3Vc8_6kM7egCnk7FcNzUWjH2d32tJ2rLO1Yr9D9OdUP9PEArdWdcygJYax0BhXuv/pub?output=csv"

st.set_page_config(
    page_title="PGWP Refusal Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Remove accidental leading/trailing spaces from column names and text cells
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Rename long Google Form headers to short internal names
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

st.title("PGWP Refusal & Reconsideration Dashboard")
st.caption("Community data analysis of PGWP refusals related to language test submission.")

# Sidebar filters
st.sidebar.header("Filters")

country_options = ["All"] + sorted(df["country"].dropna().unique().tolist())
program_options = ["All"] + sorted(df["program_type"].dropna().unique().tolist())
status_options = ["All"] + sorted(df["reconsideration_status"].dropna().unique().tolist())
test_options = ["All"] + sorted(df["language_test_type"].dropna().unique().tolist())

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
col1, col2, col3 = st.columns(3)
col1.metric("Total Responses", len(filtered_df))
col2.metric(
    "Had Test Before Applying",
    int((filtered_df["test_taken_before"] == "Yes").sum())
)
col3.metric(
    "MP Contacted",
    int((filtered_df["mp_contacted"] == "Yes").sum())
)

# Helper for safe counts
def count_df(series, x_name="Category", y_name="Count"):
    vc = series.fillna("Unknown").value_counts().reset_index()
    vc.columns = [x_name, y_name]
    return vc

# Charts
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    fig1 = px.pie(
        count_df(filtered_df["test_taken_before"], "Test Taken Before", "Count"),
        names="Test Taken Before",
        values="Count",
        title="Language Test Taken Before PGWP Application"
    )
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    fig2 = px.pie(
        count_df(filtered_df["missing_reason"], "Missing Reason", "Count"),
        names="Missing Reason",
        values="Count",
        title="Why the Language Test Was Missing"
    )
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    fig3 = px.bar(
        count_df(filtered_df["reconsideration_status"], "Reconsideration Status", "Count"),
        x="Reconsideration Status",
        y="Count",
        title="Reconsideration Outcomes",
        text="Count"
    )
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    fig4 = px.bar(
        count_df(filtered_df["mp_contacted"], "MP Contacted", "Count"),
        x="MP Contacted",
        y="Count",
        title="MP Involvement",
        text="Count"
    )
    st.plotly_chart(fig4, use_container_width=True)

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    fig5 = px.bar(
        count_df(filtered_df["reconsideration_timing"], "Timing", "Count"),
        x="Timing",
        y="Count",
        title="How Soon Reconsideration Was Requested",
        text="Count"
    )
    st.plotly_chart(fig5, use_container_width=True)

with row3_col2:
    fig6 = px.bar(
        count_df(filtered_df["webform_count"].astype(str), "Webforms Submitted", "Count"),
        x="Webforms Submitted",
        y="Count",
        title="Number of IRCC Webforms Submitted",
        text="Count"
    )
    st.plotly_chart(fig6, use_container_width=True)

row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    fig7 = px.bar(
        count_df(filtered_df["restoration_status"], "Restoration Applied", "Count"),
        x="Restoration Applied",
        y="Count",
        title="Restoration Status",
        text="Count"
    )
    st.plotly_chart(fig7, use_container_width=True)

with row4_col2:
    fig8 = px.bar(
        count_df(filtered_df["contacted_ircc_before_refusal"], "Contacted IRCC Before Refusal", "Count"),
        x="Contacted IRCC Before Refusal",
        y="Count",
        title="IRCC Contact Before Refusal",
        text="Count"
    )
    st.plotly_chart(fig8, use_container_width=True)

# Raw data section
with st.expander("Show raw data"):
    st.dataframe(filtered_df, use_container_width=True)