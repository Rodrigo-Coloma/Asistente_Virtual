import streamlit as st
from dotenv import dotenv_values
import pandas as pd
import numpy as np
import time
import utils.mgt as mgt
import utils.chat as chat
import utils.eml as eml



# Header
st.components.v1.html('<h2 style="text-align: center;">&#128202 Asistente Ilunion &#128640 </h2>', width=None, height=50, scrolling=False)


# We choose the step (page) to work on
if "username" not in st.session_state:
    with st.form('credentials'):
        username = st.text_input('Username: ',placeholder='your_username')
        password = st.text_input('Password: ',placeholder='your_password',type='password')
        if st.form_submit_button('Login',type='primary'):
            mgt.user_login(username,password)
else:
    st.session_state.steps = ['Chat', 'Email']
    st.session_state.step = st.sidebar.selectbox('Choose step', st.session_state.steps, st.session_state.steps.index(st.session_state.step))
    if st.session_state.step == 'Chat':
        if "username" in st.session_state:
            chat.chat()
        else:
            st.write("Por favor, haz login en la aplicación para empezar a chatear")

    if st.session_state.step == 'Email':
        if "username" in st.session_state:
            idiomas = [
                "Español",
                "Inglés",
                "Francés",
                "Alemán",
                "Italiano",
                "Portugués",
                "Chino Mandarín",
                "Árabe",
                "Ruso",
                "Japonés"
            ]
            dic ={0:"extremely low", 1:"very low",2:"low",3:"relatively low",4:"below average",5:"average", 6:"above average", 7: "relatively  high", 8: "high", 9: "very high", 10: "extremely high"}


            characteristics = {}
            language = st.sidebar.selectbox(' Idioma ', idiomas, placeholder="Eligen el idioma del email", index = 0)
            if language == "Español":
                tto = st.sidebar.selectbox(' Tratamiento ', ['Tú', 'Usted'], placeholder="Eligen el tratamiento para email", index = 0)
                tto = f"El email debe dirigirse al receptor o receptores de {tto}"
            else:
                tto = ""
            characteristics['politeness'] = dic[st.sidebar.slider('Educacion', 0, 10,7)]
            characteristics['urgency'] = dic[st.sidebar.slider('Urgencia', 0, 10,3)]
            characteristics['formality'] = dic[st.sidebar.slider('Formalidad', 0, 10,7)]
            characteristics['friendlyness'] = dic[st.sidebar.slider('Cercanía', 0, 10,7)]
            characteristics['Schematic'] = dic[st.sidebar.slider('Esquematico', 0, 10,5)]
            characteristics['concisiveness'] = dic[st.sidebar.slider('Conciso', 0, 10,7)]

            email = st.text_area("Copia aqui tu email:", height=300)

            if st.button("Ayudame con el email"):
                st.write_stream(eml.get_response_email(email,tto, language, characteristics))


        else:
            st.write("Por favor, haz login en la aplicación para empezar a chatear")

