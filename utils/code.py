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

    template = f"""
    You are a helpful assistant tasked with resolving coding problems in {language}. Your goal is to respond with a JSON object with two items script and explanation:

    Output format:

        script: the script solving the problem

        explanation: explanation of the script

    Problem to solve:

    {script}

    Help me to: {query}

    
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
    "JavaScript",
    "Java",
    "C#",
    "C++",
    "TypeScript",
    "PHP",
    "Ruby"
]

    language = st.sidebar.selectbox(' Lenguaje ', programming_languages, placeholder="Eligen el lenguaje con el que quieres trabajar", index = 0)


    script = st.text_area("Copia aqui el script con el que necesites ayuda:", height=280)

    query = st.text_area("Como puedo ayudarte?", height=140)

    if st.button("Ayudame con el codigo"):
        response = get_response_code(script, query, language)
        script_output = response.get('script', '')
        st.write_stream(script_output)