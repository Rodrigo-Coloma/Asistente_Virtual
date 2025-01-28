import openai
import streamlit as st
from pathlib import Path        


def img():
    resolution = st.sidebar.selectbox('Resolución',['256x256', '512x512', '1024x1024'])
    n_img = st.sidebar.slider('Nº de imagenes',1,3,1)
    openai.api_key = st.secrets['GPTAPIKEY']
    prompt=st.text_input("Describe aquí la imagen que deseas generar")

    if st.button("Generar imagen",primary=True):
        response = openai.Image.create(
            prompt = prompt,
            n = n_img,
            size = resolution
        )
        for img in response['data']:
            st.image(img['url'])