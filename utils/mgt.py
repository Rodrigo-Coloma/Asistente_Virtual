
import sqlite3 as lite
from langchain_openai import OpenAI
from dotenv import dotenv_values
import pandas as pd
import streamlit as st
import os
import time


# OpenAI


def sqlite_connection():
    connection = lite.connect('./database/asistente.db')
    st.session_state.cursor = connection.cursor()
    return connection

# Create folder struccture if it doesn't exist
def folder_management():
    if 'users' not in os.listdir('./'):
        os.mkdir('./users')

def user_create(username,password, password_confirm):
    if password != password_confirm:
        st.write('Passwords do not match')
    else:
        try:
            st.session_state.cursor.execute(f"INSERT INTO users(Username, Password, Registration_Date) VALUES ('{username}','{password}',CURRENT_TIMESTAMP);")
            st.session_state.connection.commit()
            st.session_state.username = username
            st.write('User succesfully created!!')
            st.session_state.projects_df = pd.read_sql(f"SELECT * FROM projects WHERE Owner = '{st.session_state.username}'", st.session_state.connection)
            if username not in os.listdir('./users/'):
                os.mkdir(f'./users/{username}')
            time.sleep(1.2)
            st.session_state.step = 'Projects'
        except:
            st.write('Username already exists or contains invalid characters, please choose a new one')
            time.sleep(2)
        st.rerun()

def user_login(username,password):
    try:
        if list(st.session_state.users_df.loc[st.session_state.users_df['Username'] == username,:]['Password'])[0] == password:
            st.session_state.username = username
            st.session_state.projects_df = pd.read_sql(f"SELECT * FROM projects WHERE owner = '{st.session_state.username}'", st.session_state.connection)
            if username not in os.listdir('./users/'):
                os.mkdir(f'./users/{username}')
            st.session_state.step = 'Chat'
        else:
            st.write('Incorrect username or password')
            time.sleep(2)
    except:
        st.write('Username does not exist')
        time.sleep(2)
    st.rerun()