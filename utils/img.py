import openai
import streamlit as st
from pathlib import Path 
import requests    
import os   


def img():
    openai.api_key = st.secrets['GPTAPIKEY']
    prompt=st.text_input("Describe aquí la imagen que deseas generar")

    if st.button("Generar imagen",type= "primary"):
        response = openai.images.generate(
            prompt = prompt,
            model = "dall-e-3"
        )
        img_url = response.data[0].url
        req_response = requests.get(url=img_url, timeout=20)
        path = "../data/images/temp.png"
        if req_response.status_code == 200:
            with open(path, "wb") as output:
                output.write(req_response.content)
        else: 
            req_response.raise_for_status()
        st.image(path)
        st.write(img_url)