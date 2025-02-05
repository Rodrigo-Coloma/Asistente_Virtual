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


def get_response_code(script, query, language):

    template = """
    Eres un asistente servicial encargado de resolver problemas de codificación en {language}. Tu tarea es {query}

    Código original: {script}

    
"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model="gpt-4o", temperature= 0.25)
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "language": language,
        "script": script,
        "query": query,
    })
def code():

    gpt_connect()
    programming_languages = [
                                "DAX",
                                "Python",
                                "SQL",
                                "Excel",
                                "React",
                                "JavaScript",
                                "Html",
                                "Css",
                                "Java",
                                "C#",
                                "C++",
                                "TypeScript",
                                "PHP",
                                "Ruby"
                            ]

    language = st.sidebar.selectbox(' Lenguaje ', programming_languages, placeholder="Eligen el lenguaje con el que quieres trabajar", index = 0)

    cols = st.columns(2)

    with cols[0]:
        script = st.text_area("Copia aqui el script con el que necesites ayuda:", height=280)

        script = f"Original script: {script}"

        query = st.text_area("Como puedo ayudarte?", height=140)

    if st.button("Ayudame con el codigo"):
        with cols[1]:
            st.write_stream(get_response_code(script, query, language))
