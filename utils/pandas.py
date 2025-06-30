from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
import streamlit as st
import pandas as pd
import traceback
import os

file_formats = {
        "csv": pd.read_csv,
        "xls": pd.read_excel,
        "xlsx": pd.read_excel,
        "xlsm": pd.read_excel,
        "xlsb": pd.read_excel,
    }
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
def clear_submit():
        """
        Clear the Submit Button State
        Returns:

        """
        st.session_state["submit"] = False


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Unsupported file format: {ext}")
        return None

def play_pandas():
    """st.session_state.gpt_key = st.secrets['GPTAPIKEY']
    os.environ["OPENAI_API_KEY"] = st.session_state.gpt_key"""

    uploaded_file = st.sidebar.file_uploader(
        "Upload a Data file",
        type=list(file_formats.keys()),
        help="Various File formats are Support",
        on_change=clear_submit,
    )

    if not uploaded_file:
        st.sidebar.warning(
            "This app uses LangChain's `PythonAstREPLTool` which is vulnerable to arbitrary code execution. Please use caution in deploying and sharing this app."
        )

    if uploaded_file:
        df = load_data(uploaded_file)

    if st.sidebar.button("Auto Dashboard", type="primary"):
        if "error" not in st.session_state:
                st.session_state.autoprompt = [{"role": "user", "content": f"""Create the most awesome streamlit dashboard with the dataframe provided.
                                        First clean the dataframe and handdle missing data and different data types paying special attention not to perform unsupported operations, then create a dashboard that provides business inteligence insights.
                                        The dashboard needs to provide summary of the data and the ability to filter it (st.multiselect) for all the relevant fieldvisualy describe the dataframe as well as to visualy describe the dataframe.
                                        You may change the name of the columns so they are more descriptive.
                                        The dashboard should be interactive and user friendly and in spanish.
                                        The dashboard should be able to handle large datasets and provide insights into the data.
                                        never use st.set_page_config.
                                        Make figures small, use 2 st.columns. And only show each figure once!! no duplicated st.pyplot(figx)
                                        Create an extensive insightfull analysis of the dataframe (EDA) using diferent visualizations.
                                        Include at least 10 visualizations distributed in the 2 st.columns.
                                        Add as many coments as st.write() as you can, so the user can understand what is going on.
                                        You may include barcharts, column charts, scatter plots, piecharts. Using numeric_df = df.select_dtypes(include=['number']) select numeric columns andn create a correlation matrix with
                                        correlation_matrix = numeric_df.corr() and plot it in a heatmap.
                                        Be speciallly carefull not to treat object columns as numeric, and to only treat numeric columns as numeric
                                        Also try to identify those columns which are parseable to datetime and parse them as such, you may create month and year columns and use them in visualizations.
                                        Your response must include necessary imports, be complete and ready to run in streamlit. No need to define the dataframe again, just use the one you have (df) """}]
        else:
             correction_prompt = f"""The script you provided led to this error: {st.session_state.error}. Can you please fix it?. """
             st.session_state.autoprompt.append({"role": "user", "content": correction_prompt})   
                
        llm_auto = ChatOpenAI(
            temperature=0.00, model="gpt-4o", openai_api_key=openai_api_key, streaming=True
        )
        pandas_df_agent_auto = create_pandas_dataframe_agent(
            llm_auto,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )   
        response = pandas_df_agent_auto.run(st.session_state.autoprompt)
        if response != None and "```python" in response:
            st.session_state.autoprompt.append({"role": "assistant", "content": response})
            st.session_state.script = response.split("```python")[1].split("```")[0].strip()
            st.rerun()

    if "script" in st.session_state:
        #st.sidebar.markdown("### Generated Script")
        #st.sidebar.code(st.session_state.script, language="python")
        try:
            exec(st.session_state.script)
            st.sidebar.success("Script executed successfully!")
        except Exception as e:
            st.sidebar.error(f"Error executing script: {traceback.format_exc()}")
            tb = traceback.format_exc()
            if tb != st.session_state.error:
                st.session_state.error = tb
                st.rerun()

    if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    """
    script = st.sidebar.text_input(placeholder="What is this data about?", label="Script to run on DataFrame", key="script_input")
    if st.sidebar.button("Run Script", type="primary"):
        exec(script)
    """
    if prompt := st.chat_input(placeholder="What is this data about?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        llm = ChatOpenAI(
            temperature=0.1, model="gpt-4o", openai_api_key=openai_api_key, streaming=True
        )

        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
            if response != None and "```python" in response:
                st.session_state.script = response.split("```python")[1].split("```")[0].strip()

    """if "script" in st.session_state:
        st.sidebar.markdown("### Generated Script")
        st.sidebar.code(st.session_state.script, language="python")
        if st.sidebar.button("Run Script", type="primary"):
            try:
                exec(st.session_state.script)
                st.sidebar.success("Script executed successfully!")
            except Exception as e:
                st.sidebar.error(f"Error executing script: {e}")"""
    


    """I wasnt to create a comprehensive dashboard in streamlit using (if neccesary) numpy, panda, pyplot, seaborn and matplotlib.
                                        The dashboard needs to visualy describe the the dataframe as well as to provide summary of the data and the ability to filter it.
                                        You may change the name of the columns so they are more descriptive.
                                        The dashboard should be interactive and user friendly.
                                        The dashboard should be able to handle large datasets and provide insights into the data.
                                        The dashboard should be able to handle missing data and provide insights into the data.
                                        Using st.selectbox, make it so i canm choose a column and get the apropiate distribution visualization in each case. It should be contained in the left side of the dashboard. 
                                        in a column that takes 1 third of the screen width. If the categories are too long, please rotate the label on the x axis so it can be readable.
                                        On the right side of the dashboard, in a column that takes 2 thirds of the screen width, show as many small figures as possible, each one with a different and relevant 
                                        visualization of the data, that provides the user with meaningfull insights.
                                        Add as many coments as st.write() as you can, so the user can understand what is going on.
                                        never use st.set_page_config or st.set_option to set the page config or layout.
                                        Make figures small, use st.columns if needed. And only show each figure once!! no duplicated st.pyplot(figx)
                                        
                                        Your response must include necessary imports, be complete and ready to run in streamlit. No need to define the dataframe again, just use the one you have (df)
                                        """
