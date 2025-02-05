import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatPerplexity
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
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



def get_response(user_query, model, temperature, chat_history):

    st.session_state.client = OpenAI(api_key=st.session_state.gpt_key)

    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

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

def get_factos(llm, messages, user_query):
    
    messages = [("system", "eres un aistente cuya mision es proveer de los datos mas actuales y precisos que puedas encontrar para responder a las preguntas que te hagan")]
    for i, mess in enumerate(st.session_state.messages):
        if i != 0 or mess['role'] != "assistant":
            messages.append((mess['role'],mess['content']))
    
    prompt = ChatPromptTemplate.from_messages(messages)
    
    chain = prompt | llm

    with st.spinner():
        response = chain.invoke({"input": user_query})
        response_content = response.content
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        st.rerun()

def get_context_retriever_chain(vector_db, llm):
    retriever = vector_db.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation, focusing on the most recent messages."),
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

def stream_llm_response(llm_stream, messages):
    response_message = ""

    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk

    st.session_state.messages.append({"role": "assistant", "content": response_message})
    
def stream_llm_rag_response(llm_stream, messages):
    conversation_rag_chain = get_conversational_rag_chain(llm_stream)
    response_message = "*(RAG Response)*\n"
    for chunk in conversation_rag_chain.pick("answer").stream({"messages": messages[:-1], "input": messages[-1].content}):
        response_message += chunk
        yield chunk

    st.session_state.messages.append({"role": "assistant", "content": response_message})

def chat():
    gpt_connect()
    
    model = st.sidebar.selectbox('modelo',["gpt-4o-mini", "gpt-4o"],index=0)
    temperature = st.sidebar.slider("Temperatura",0.0,1.0,0.5)
    llm_stream = ChatOpenAI(model=model, temperature=temperature)
    llm_factos = ChatPerplexity(temperature=0.2, pplx_api_key=st.session_state.per_key, model="llama-3.1-sonar-large-128k-online")
    is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)
    
    if "use_rag" not in st.session_state:
        st.session_state.use_rag = False

    st.sidebar.toggle(
                "Busqueda web (Tiempo Real)", 
                value=False, 
                key="factos", 
                disabled= st.session_state.use_rag,
            )
    st.sidebar.toggle(
                    "RAG", 
                    value=False, 
                    key="use_rag", 
                    disabled=not is_vector_db_loaded or st.session_state.factos,
                )
    st.sidebar.file_uploader(
            "📄 Sube tus documentos", 
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

    if st.sidebar.button('Limpiar chat',type="primary"):
        st.session_state.messages = []
        st.rerun()

    # Conversation
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Como puedo ayudarte hoy?"}
]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            messages = [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m in st.session_state.messages]
            
            if st.session_state.factos:
                st.markdown(get_factos(llm_factos, messages,prompt))
            elif not st.session_state.use_rag:
                st.write_stream(stream_llm_response(llm_stream, messages))
            else:
                st.write_stream(stream_llm_rag_response(llm_stream, messages))
            
