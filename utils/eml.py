import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import dotenv_values
import pandas as pd
import streamlit as st
import os
import time


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

    llm = ChatOpenAI(model="gpt-4o-mini")
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "language": language,
        "characteristics": characteristics,
        "email": email,
        "tto": tto
    })
def email():
    gpt_connect()