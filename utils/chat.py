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

def get_response(user_query, model, teamperature, chat_history):

    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation. Use behind the scenes search if needed:

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model=model, temperature=temperature)
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })


def chat():
    gpt_connect()
    #Conversation
    model = st.sidebar.selectbox('modelo',["gpt-4o-mini", "gpt-4o"],index=0)
    temperature = st.sidebar.slider("Temperatura",0.0,1.0,0.5)
    if "chat_history" in st.session_state:
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):
                with st.chat_message("User"):
                    st.markdown(message.content)
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.markdown(message.content)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.chat_message("AI"):
            response = st.write_stream(get_response(user_query, model, temperature, st.session_state.chat_history))

        st.session_state.chat_history.append(AIMessage(content=response))
    if st.sidebar.button('Limpiar chat',type="primary"):
        st.session_state.chat_history = []
        st.rerun()