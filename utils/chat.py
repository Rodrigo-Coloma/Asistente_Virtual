import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import dotenv_values
import utils.rag as rag
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

def get_response(user_query, model, temperature, chat_history):

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

def get_context_retriever_chain(vector_db, llm):
    retriever = vector_db.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get inforamtion relevant to the conversation, focusing on the most recent messages."),
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain

def get_conversational_rag_chain(llm):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_db, llm)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
        """You are a helpful assistant. You will have to answer to user's queries.
        You will have some context to help with your answers, but it wont always would be completely related or helpful.
        You can also use your knowledge to assist answering the user's queries.\n
        {context}"""),
        MessagesPlaceholder(variable_name="messages"),
        ("user", "{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


def get_response_rag(user_query, model, temperature, chat_history):

    llm = ChatOpenAI(model=model, temperature=temperature)

    context = get_conversational_rag_chain(llm)

    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation and the context:

    Chat history: {chat_history}

    context: {context}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
        "context": context
    })

def chat():
    gpt_connect()
    
    model = st.sidebar.selectbox('modelo',["gpt-4o-mini", "gpt-4o"],index=0)
    temperature = st.sidebar.slider("Temperatura",0.0,1.0,0.5)
    is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)
    st.sidebar.toggle(
                "RAG", 
                value=is_vector_db_loaded, 
                key="use_rag", 
                disabled=not is_vector_db_loaded,
            )
    st.sidebar.file_uploader(
            "📄 Upload a document", 
            type=["pdf", "txt", "docx", "md"],
            accept_multiple_files=True,
            on_change= rag.load_doc_to_db,
            key="rag_docs",
        )

    # URL input for RAG with websites
    st.sidebar.text_input(
        "🌐 Introduce a URL", 
        placeholder="https://example.com",
        on_change= rag.load_url_to_db,
        key="rag_url",
    )

    with st.sidebar.expander(f"📚 Documents in DB ({0 if not is_vector_db_loaded else len(st.session_state.rag_sources)})"):
        st.write([] if not is_vector_db_loaded else [source for source in st.session_state.rag_sources])


    # Conversation
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
            if not st.session_state.use_rag:
                response = st.write_stream(get_response(user_query, model, temperature, st.session_state.chat_history))
            else:
                response = st.write_stream(get_response_rag(user_query, model, temperature, st.session_state.chat_history))
            

        st.session_state.chat_history.append(AIMessage(content=response))
    if st.sidebar.button('Limpiar chat',type="primary"):
        st.session_state.chat_history = []
        st.rerun()