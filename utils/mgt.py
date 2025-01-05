import streamlit as st
import os



def user_login(username,password):
    try:
        real_pass = st.secrets['passwords'][username]
    except:
        st.warning('Usuario no válido')
    if real_pass == password:
        st.session_state.username = username
        try:
            os.mkdir('./users/')
        except:
            if username not in os.listdir('./users/'):
                os.mkdir(f'./users/{username}')
            st.rerun()
    else:
        st.error('Contraseña incorrecta')
    