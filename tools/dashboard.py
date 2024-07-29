import sqlite3

import streamlit as st
import pandas as pd


st.title("Dashboard")
conn = sqlite3.connect('attendance.db')

df = pd.read_sql_query("SELECT * FROM attendance", conn)

# Display data
st.dataframe(df)