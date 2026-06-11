import streamlit as st
from project import get_connection
import pandas as pd

def login():

    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        conn = get_connection()

        query = """
        SELECT user_id, username, role, branch_id
        FROM users
        WHERE username = %s AND password = %s
        """

        df = pd.read_sql(query, conn, params=(username, password))

        if len(df) > 0:

            user = df.iloc[0]

            st.session_state.logged_in = True
            st.session_state.user_id = user["user_id"]
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.session_state.branch_id = user["branch_id"]

            st.rerun()

        else:
            st.error("Invalid username or password")