import openai
import streamlit as st
from pathlib import Path        


def img():
    openai.api_key = st.secrets['GPTAPIKEY']
    prompt=st.text_input("Describe aquí la imagen que deseas generar")

    if st.button("Generar imagen",type= "primary"):
        response = openai.images.generate(
            prompt = prompt,
            model = "dall-e-3"
        )
        st.image(response.data[0].url)