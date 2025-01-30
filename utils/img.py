import openai
import streamlit as st
from pathlib import Path 
import requests    
import os   


def img():
    openai.api_key = st.secrets['GPTAPIKEY']
    prompt=st.text_input("Describe aquí la imagen que deseas generar")
    resolution = st.sidebar.selectbox('Resolución',["256x256","512x512","1024x1024"])
    n_img = st.sidebar.slider("Número de imágenes",1,3,1)

    if st.button("Generar imagen",type= "primary"):
        with st.spinner("generando la imagen..."):
            response = openai.images.generate(
                prompt = prompt,
                model = "dall-e-3",
                size = resolution,
                n = n_img
            )
        for img in response.data:
            img_url = img.url
            req_response = requests.get(url=img_url, timeout=30)
            path = "./data/images/temp.png"
            if req_response.status_code == 200:
                with open(path, "wb") as output:
                    output.write(req_response.content)
            else: 
                req_response.raise_for_status()
            st.image(path)
            st.write(img_url)