import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import dotenv_values
import streamlit as st
import os


def gpt_connect():
    try:
        st.session_state.gpt_key = dotenv_values('./.env')['token_gpt']
    except:
        st.session_state.gpt_key = st.secrets['GPTAPIKEY']
    os.environ["OPENAI_API_KEY"] = st.session_state.gpt_key

def get_response_email(email, tto, language, characteristics):

    template = f"""
    You are a helpful assistant tasked with rewriting the provided email. Your goal is to ensure correct grammar and enhance clarity.

    The email should be composed in the following language: {language}.

    {tto}
    
    The level of politeness should be {characteristics['politeness']}
    The level of urgency should be {characteristics['urgency']}
    The level of formality should be {str(characteristics['formality'])}
    The level of friendlyness should be {str(characteristics['friendlyness'])}
    The level of schematism should be {str(characteristics['Schematic'])}
    The level of concisiveness should be {str(characteristics['concisiveness'])}    

    Email:

    {email}
"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model="gpt-4o")
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "language": language,
        "characteristics": characteristics,
        "email": email,
        "tto": tto
    })
def email():
    gpt_connect()
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
        tto = st.sidebar.selectbox(' Tratamiento ', ['Tú', 'Usted', 'Vosotros', 'Ustedes'], placeholder="Eligen el tratamiento para el email", index = 0)
        tto = f"El email debe dirigirse al receptor o receptores de {tto} independientemente del tratamiento del mail original y del nivel de formalidad especificado"
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
        st.write_stream(get_response_email(email,tto, language, characteristics))