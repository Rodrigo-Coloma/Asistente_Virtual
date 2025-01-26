import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatPerplexity
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, Docx2txtLoader
from dotenv import dotenv_values
import utils.rag as rag
import streamlit as st
import os
from openai import OpenAI


def gpt_connect():
    try:
        st.session_state.gpt_key = dotenv_values('./.env')['token_gpt']
    except:
        st.session_state.gpt_key = st.secrets['GPTAPIKEY']
        st.session_state.per_key = st.secrets['per_key']
    os.environ["OPENAI_API_KEY"] = st.session_state.gpt_key


def get_plan_context(vector_db, llm):
    retriever = vector_db.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("user", "Retrieve all the available information about the Plantilla Plan de acción{input}"),
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain

def get_plan_response(llm):
    retriever_chain = get_plan_context(st.session_state.vector_db, llm,)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
        """Eres un asistente de redacción de planes de acción para el departamento de datos de una empresa hotelera. Ayudame a redactar un plan de acción en base a la siguiente plantilla: 
        \n {context}\n"""),
        ("user", "{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)
            

    
def stream_llm_plan_response(llm_stream, input):
    conversation_rag_chain = get_plan_response(llm_stream)
    response_message = "*(RAG Response)*\n"
    for chunk in conversation_rag_chain.pick("answer").stream({ "input" : input}):
        response_message += chunk
        yield chunk

def plan():
    gpt_connect()
    if "sample" not in st.session_state:
        rag.default_load()
        st.session_state.sample = True
    rag.default_load()
    
    llm_stream = ChatOpenAI(model="gpt-4o", temperature=0.4)
    cols = st.columns(2)
    with cols[0]:
        notes = st.text_area("Copia aqui las notas ara el plan de acción", height=280)

        instructions = st.text_area("Instrucciones addicionales", height=140)

        instructions = f"Instrucciones adicionales: {instructions}"

    if st.button("Crear el Plan de Acción"):
        input = f"Estas son las notas tomadas en la reunión en las que te tienes que basar para elaborar el plan de acción\n{notes}\n{instructions}"

        with cols[1]:
            st.write_stream(stream_llm_plan_response(llm_stream, input))
