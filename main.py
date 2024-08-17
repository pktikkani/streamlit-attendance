import os
from datetime import date
from logging import exception

import streamlit as st
from dotenv import load_dotenv
import sqlite3
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

# Load environment variables and set up OAuth client
load_dotenv('.env')
CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
REDIRECT_URI = os.environ['GOOGLE_REDIRECT_URI']

#DB Connection
conn = sqlite3.connect('users.db')
c = conn.cursor()


def create_registration_table():
    c.execute('''CREATE TABLE IF NOT EXISTS registration
                 (name TEXT, email TEXT, date TEXT, phone TEXT)''')
    conn.commit()

def create_attendance_table():
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
             (email TEXT, date TEXT)''')
    conn.commit()


def show_emails():
    c.execute("SELECT email FROM registration")
    return [row[0] for row in c.fetchall()]

# Custom CSS
def load_css():
    st.markdown("""
  <style>
  .big-font {
      font-size:30px !important;
      font-weight: bold;
  }
  .stButton>button {
      color: #4F8BF9;
      border-radius: 50px;
      height: 3em;
      width: 100%;
  }
  .custom-button {
      vertical-align: middle;
      font-size: 20px !important;
      padding: 10px 20px !important;
      background-color: #4CAF50 !important;
      color: white !important;
      border: none !important;
      border-radius: 50px !important;
      cursor: pointer !important;
      text-decoration: none !important;
      width: 100%;
  }
  .custom-button:hover {
      background-color: #45a049 !important;
  }
  </style>
  """, unsafe_allow_html=True)


# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def add_bg_gradient():
    st.markdown(
        f"""
           <style>
           .stApp {{
               background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
           }}
           </style>
           """,
        unsafe_allow_html=True
    )
    st.query_params.clear()


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(redirect_uri, scope=["profile", "email"])
    return authorization_url


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def login():
    add_bg_gradient()
    st.markdown("<h1 style='text-align: center;'>AYS Attendance</h1>", unsafe_allow_html=True)

    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    authorization_url = asyncio.run(
        get_authorization_url(client, REDIRECT_URI))
    st.session_state.auth_url = authorization_url

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button("Google Login", st.session_state.auth_url)


def callback():
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    if 'code' in st.query_params:
        code = st.query_params['code']
        try:
            with st.spinner("Logging you in..."):
                token = asyncio.run(get_access_token(
                    client, REDIRECT_URI, code))
                user_id, user_email = asyncio.run(
                    get_email(client, token['access_token']))
                st.write(
                    f"You're logged in as {user_email} and id is {user_id}")
                st.session_state['user'] = user_email
                st.session_state.logged_in = True
                st.success("Successfully logged in!")
        except Exception as e:
            exception(f"Failed to get access token or user email. Please try again. Error: {e}")
            st.error(f"Google Auth Error {e}")


def logout():
    add_bg_gradient()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.query_params.clear()
            st.rerun()


def user_attendance():
    st.title("User Attendance")
    add_bg_gradient()
    with st.form("attendance_form", clear_on_submit=True):
        options = show_emails()
        email = st.selectbox("Select Email", options)
        present_date = date.today()
        today = st.date_input("Select Date", present_date)
        submit_button = st.form_submit_button("Submit Attendance")
    if submit_button:
        if email:  # Check if name and email are not empty
            create_attendance_table()
            c.execute("INSERT INTO attendance VALUES (?, ?)", (email, today))
            conn.commit()
            st.success("Attendance recorded successfully!")
        else:
            st.error("Please enter both name and email.")


def registration():
    add_bg_gradient()
    st.title("User Registration")
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("Enter your name")
        email = st.text_input("Enter your email")
        phone = st.text_input("Enter your phone number")
        present_date = date.today()
        today = st.date_input("Select Date", present_date)
        submit_button = st.form_submit_button("Submit Registration")
    if submit_button:
        if name and email:  # Check if name and email are not empty
            create_registration_table()
            c.execute("INSERT INTO registration VALUES (?, ?, ?, ?)", (name, email, today, phone))
            conn.commit()
            st.success(f"Registration was successful {name}")
        else:
            st.error("Please enter both name and email.")


login_page = st.Page(login, title="Log in")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
user_attendance_page = st.Page(user_attendance, title="User Attendance")
reports = st.Page("tools/reports.py", title="Reports", icon="📊")
registration = st.Page(registration, title="Registration", icon="📝")


def main():
    load_css()
    # App header
    if 'code' in st.query_params:
        callback()

    if st.session_state.logged_in:
        st.sidebar.markdown(f"Welcome, {st.session_state['user']}!")
        pg = st.navigation(
            {
                "Account": [logout_page],
                "Tools": [reports],
            }
        )
    else:
        pg = st.navigation([login_page, user_attendance_page, registration])

    pg.run()


if __name__ == "__main__":
    main()




