import streamlit as st
from dotenv import dotenv_values
import pandas as pd
import numpy as np
import time
import utils.mgt as mgt
import utils.chat as chat
import utils.eml as eml


def main():
    # Header
    st.components.v1.html('<h2 style="text-align: center;">&#128202 Asistente &#128640 </h2>', width=None, height=50, scrolling=False)


    # We choose the step (page) to work on
    if "username" not in st.session_state:
        with st.form('credentials'):
            username = st.text_input('Username: ',placeholder='your_username')
            password = st.text_input('Password: ',placeholder='your_password',type='password')
            if st.form_submit_button('Login',type='primary'):
                mgt.user_login(username,password)
    else:
        st.session_state.tools = ['Chat', 'Email']
        st.session_state.tool = st.sidebar.selectbox('Herramienta', st.session_state.tools,0)
        if st.session_state.tool == 'Chat':
            chat.chat()

        if st.session_state.tool == 'Email':
            eml.email()

if __name__=="__main__":
    main()
