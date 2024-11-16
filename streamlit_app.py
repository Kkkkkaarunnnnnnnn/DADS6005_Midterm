import streamlit as st
import pandas as pd
import plotly.express as px
from pinotdb import connect

# Connect to Apache Pinot
host = "54.251.87.200"
port = 8099
conn = connect(host=host, port=port)
cursor = conn.cursor()

# Function to fetch data
@st.cache_data
def fetch_data(query):
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return pd.DataFrame(rows, columns=columns)

# Get distinct SUBSCRIPTIONTYPE values for the filter
subscription_query = """
SELECT DISTINCT SUBSCRIPTIONTYPE
FROM topic5
WHERE SUBSCRIPTIONTYPE IS NOT NULL;
"""
subscription_types = fetch_data(subscription_query)["SUBSCRIPTIONTYPE"].tolist()

# Add a filter for SUBSCRIPTIONTYPE
selected_subscription = st.sidebar.selectbox(
    "Select Subscription Type", ["All"] + subscription_types
)

# Modify queries to apply the filter
subscription_filter = (
    f"WHERE SUBSCRIPTIONTYPE = '{selected_subscription}' AND SUBSCRIPTIONTYPE IS NOT NULL"
    if selected_subscription != "All" else
    "WHERE SUBSCRIPTIONTYPE IS NOT NULL"
)

# Query 1: Region-wise User Distribution
query1 = f"""
SELECT REGIONID, COUNT(DISTINCT USERID) AS user_count
FROM topic5
{subscription_filter}
GROUP BY REGIONID
ORDER BY user_count DESC
LIMIT 10;
"""
region_data = fetch_data(query1)

# Query 2: Gender Distribution
query2 = f"""
SELECT GENDER, COUNT(*) AS gender_count
FROM topic5
{subscription_filter}
GROUP BY GENDER
ORDER BY gender_count DESC;
"""
gender_data = fetch_data(query2)

# Query 3: Average Viewtime by Gender
query3 = f"""
SELECT GENDER, AVG(VIEWTIME) AS avg_viewtime
FROM topic5
{subscription_filter}
GROUP BY GENDER;
"""
viewtime_data = fetch_data(query3)

# Query 4: Top Users by Viewtime
query4 = f"""
SELECT USERID, SUM(VIEWTIME) AS total_viewtime
FROM topic5
{subscription_filter}
GROUP BY USERID
ORDER BY total_viewtime DESC
LIMIT 10;
"""
top_users_data = fetch_data(query4)

# New Query: Count by Subscription Type
query5 = """
SELECT SUBSCRIPTIONTYPE, COUNT(*) AS subscription_count
FROM topic5
WHERE SUBSCRIPTIONTYPE IS NOT NULL
GROUP BY SUBSCRIPTIONTYPE
ORDER BY subscription_count DESC;
"""
subscription_data = fetch_data(query5)

# Streamlit Layout
st.title("Real-time Subscribers Analytics")
st.markdown("- Interactive Dashboard with Users Insights")

# Display the selected filter
st.sidebar.markdown(f"**Selected Subscription Type:** {selected_subscription}")

# Chart 1: Region-wise User Distribution
st.subheader("Region-wise User Distribution")
fig_region = px.bar(
    region_data,
    x="REGIONID",
    y="user_count",
    title="Region-wise User Distribution",
    color_discrete_sequence=["#98AE9B"]
)
st.plotly_chart(fig_region, use_container_width=True)

# Charts 2 & 3: Two columns
col1, col2 = st.columns(2)

# Chart 2: Gender Distribution (Pie Chart)
col1.subheader("Gender Distribution")
fig_gender = px.pie(
    gender_data,
    names="GENDER",
    values="gender_count",
    title="Gender Distribution",
    color_discrete_map={
        "MALE": "#B4C0AD",
        "FEMALE": "#B9C7DC",
        "OTHER": "#EEE7C3"
    }
)
col1.plotly_chart(fig_gender, use_container_width=True)

# Chart 3: Average Viewtime by Gender (Bar Chart)
col2.subheader("Average Viewtime by Gender")
fig_avg_viewtime = px.bar(
    viewtime_data,
    x="GENDER",
    y="avg_viewtime",
    title="Average Viewtime by Gender",
    color_discrete_sequence=["#B9C7DC"]
)
col2.plotly_chart(fig_avg_viewtime, use_container_width=True)

# Chart 4: Top Users by Viewtime (Vertical Bar Chart)
st.subheader("Top Users by Viewtime")
fig_top_users = px.bar(
    top_users_data,
    x="USERID",
    y="total_viewtime",
    title="Top Users by Viewtime",
    labels={"USERID": "User ID", "total_viewtime": "Total Viewtime"},
    text="total_viewtime",
    color_discrete_sequence=["#EEE7C3"]
)
fig_top_users.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig_top_users, use_container_width=True)

# New Chart: Count by Subscription Type (Full-width below)
st.subheader("Count by Subscription Type")
fig_subscription = px.bar(
    subscription_data,
    x="SUBSCRIPTIONTYPE",
    y="subscription_count",
    title="Count by Subscription Type",
    color_discrete_sequence=["#B4C0AD"]
)
st.plotly_chart(fig_subscription, use_container_width=True)
