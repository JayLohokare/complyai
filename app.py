import streamlit as st
import os
from fastapi import FastAPI, UploadFile, File
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import time
from streamlit_chat import message

from langchain import (
    LLMMathChain,
    OpenAI,
    SerpAPIWrapper,
    SQLDatabase,
    SQLDatabaseChain,
)
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI

app = FastAPI()

employment_tests = {
    "1": "How many number of employees had system access after termination?",
    "2": "How many employees records indicate date of joining (DOJ) after date of leaving?"
}

# Define the directory to store uploaded CSV files
UPLOAD_DIR = "uploads"


def refresh():
    st.session_state.conversation = None
    st.session_state.chat_history = None
    st.session_state.data_type = None

# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = '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'

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    submit = st.button("Submit")
    clear = st.button("Refresh")
    

def updateMessages():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

def printMessage(role, message):
    st.session_state.messages.append({"role": role, "content": message})
    # updateMessages()



st.title("Comply AI")
if st.session_state != None and "messages" not in st.session_state:
    st.session_state.messages = []
    printMessage("assistant", "Started a new session. Please upload a file to analyze...")

if clear:
    refresh()

if submit:
    if uploaded_file == None:
        printMessage("assistant", "Please upload a file for Comply AI to analyze...")
        
    else:
        printMessage("assistant", "Uploading and Analyzing the file. We do not retain any data you upload!")
        
        # if  "data_type" not in st.session_state or  st.session_state.data_type == None or  st.session_state.data_type == "":
        file_path = os.path.join(UPLOAD_DIR, 'upload.csv')
        agent = create_csv_agent(OpenAI(temperature=0), file_path, verbose=True)
        res1  = agent.run("If this document contains employee data (e.g. names, designations, departments, reporting managers, date of joining, date of leaving, applications, and termination dates), Say 'Detected employment data'")
        
        
        printMessage("assistant", res1)
        
        
        if res1 == "Detected employment data":
            st.session_state.data_type = "employment"
            prompt = "Select tests to run \n\n"
            for testKey in employment_tests.keys():
                    prompt = prompt + str(testKey) + " : " + str(employment_tests[testKey]) + "\n\n"
            prompt = prompt + "You can also ask questions to explain the data!"
            printMessage("assistant", prompt)
               
               

                # st.chat_message("assistant").write("Select tests to run")
                # for testKey in employment_tests.keys():
                #     prompt = str(testKey) + " : " + str(employment_tests[testKey])
                #     st.chat_message("assistant").write(prompt)
                # st.chat_message("assistant").write("You can also ask questions to explain the data!")
                


if prompt := st.chat_input():
    if not uploaded_file:
        printMessage("assistant", "Please upload a file for Comply AI to analyze...")

    else:
        file_path = os.path.join(UPLOAD_DIR, 'upload.csv')
        agent = create_csv_agent(OpenAI(temperature=0), file_path, verbose=True)
        
        printMessage("user", prompt)
        

        if st.session_state.data_type == None:
            printMessage("assistant", "The uploaded file type isn't supported in our Beta. Please contact sales to get advanced access!")

        if st.session_state.data_type == "employment":
            selectedOption = (prompt.strip())
            if selectedOption in employment_tests.keys():
                response  = agent.run(employment_tests[selectedOption])
            else:
                response  = agent.run(prompt)
            msg = response
            printMessage("assistant", msg)


updateMessages()