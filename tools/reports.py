import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Database connection
conn = sqlite3.connect('attendance.db')


def reports():
    st.title("Attendance Reports")

    # Fetch all data from the database
    df = pd.read_sql_query("SELECT * FROM attendance", conn)

    if df.empty:
        st.warning("No attendance records found.")
        return

    # Group by email and count unique dates
    attendance_summary = df.groupby('email').agg({
        'name': 'first',  # Get the first name associated with each email
        'date': 'nunique'  # Count unique dates for each email
    }).reset_index()
    attendance_summary.columns = ['Email', 'Name', 'Days Present']

    # Display summary table
    st.subheader("Attendance Summary")
    st.dataframe(attendance_summary)

    # Bar chart of attendance
    st.subheader("Attendance Visualization")
    fig = px.bar(attendance_summary, x='Email', y='Days Present', text='Days Present',
                 hover_data=['Name'], color='Days Present',
                 height=400, title="Days Present by Member")
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

    # Pie chart of attendance distribution
    st.subheader("Attendance Distribution")
    fig_pie = px.pie(attendance_summary, values='Days Present', names='Email',
                     title='Distribution of Attendance')
    st.plotly_chart(fig_pie)

    # Recent attendance records
    st.subheader("Recent Attendance Records")
    recent_records = df.sort_values('date', ascending=True).head(10)
    st.table(recent_records)

    # Download full report
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Full Report",
        data=csv,
        file_name="full_attendance_report.csv",
        mime="text/csv",
    )


# Call the function
reports()
