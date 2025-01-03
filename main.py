import streamlit as st
from dotenv import dotenv_values
import pandas as pd
import numpy as np
import time
import utils.mgt as mgt
import utils.chat as chat



# Header
st.components.v1.html('<h2 style="text-align: center;">&#128202 Asistente Ilunion &#128640 </h2>', width=None, height=50, scrolling=False)

# Create the connection with the database and OpenAI
if "connetion" not in st.session_state:    
    st.session_state.connection = mgt.sqlite_connection()

# Create folders if necessary
if 'folders' not in st.session_state:
    mgt.folder_management()
    st.session_state.folders = True

# We choose the step (page) to work on
if "step" not in st.session_state:
    st.session_state.step = 'User Login'
    st.session_state.steps = ['User Login', 'Chat']
st.session_state.step = st.sidebar.selectbox('Choose step', st.session_state.steps, st.session_state.steps.index(st.session_state.step))
#User Management
if st.session_state.step == 'User Login':   
    login_tab, register_tab, delete_tab = st.tabs(['Login','Registro', 'Borrar Cuenta'])
    if "username" in st.session_state and st.session_state.username == 'admin':
        st.dataframe(st.session_state.users_df)
    st.session_state.users_df = pd.read_sql("SELECT * FROM users", st.session_state.connection)
    with login_tab:
        username = st.text_input('Username: ',placeholder='your_username')
        password = st.text_input('Password: ',placeholder='your_password',type='password')
        if st.button('Login',type='primary'):
            mgt.user_login(username,password)
    with register_tab:
        if "username" in st.session_state and st.session_state.username == 'admin':    
            username = st.text_input('Username: ')
            password = st.text_input('Password: ',type='password')
            password_confirm = st.text_input('Comfirm Password: ',placeholder='Repeat your password',type='password')
            if st.button('Create',type='primary'):
                mgt.user_create(username,password,password_confirm)
        else:
            st.write("Por favor, ponte en contacto con el administrador para generar una nueva cuenta")

if st.session_state.step == 'Chat':
    if "username" in st.session_state:
        chat.chat()
    else:
        st.write("Por favor, haz login en la aplicación para empezar a chatear")
