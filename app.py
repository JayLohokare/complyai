import streamlit as st
import os
from fastapi import FastAPI, UploadFile, File
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import time
from streamlit_chat import message
import tempfile

import pandas as pd

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
    "2": "How many employees records indicate date of joining (DOJ) after date of leaving?",
}

# Define the directory to store uploaded CSV files
UPLOAD_DIR = "uploads"

def updateMessages():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

def printMessage(role, message):
    st.session_state.messages.append({"role": role, "content": message})


def refresh():
    st.session_state.conversation = None
    st.session_state.chat_history = None
    st.session_state.data_type = None
    st.session_state.messages = []
    preselected_uploaded_file = None
    printMessage("assistant", "Started a new session. Please upload a file to analyze...")
    updateMessages()


# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = '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'

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a file")
    submit = st.button("Submit")
    clear = st.button("Refresh")
    employmentDataButton = st.button("Use Sample Employment data")

def create_preselected_agent():
    llm = OpenAI(temperature=0)
    return create_csv_agent(OpenAI(temperature=0), 'uploads/employment.csv', verbose=True)

def select_employment_data():
    preselected_uploaded_file = "employment"
    agent = create_preselected_agent()
    printMessage("assistant", "Detected Employment data")
    st.session_state.data_type = "employment"

    prompt = "Select tests to run \n\n"
    for testKey in employment_tests.keys():
            prompt = prompt + str(testKey) + " : " + str(employment_tests[testKey]) + "\n\n"
    prompt = prompt + "You can also ask questions to explain the data!"
    printMessage("assistant", prompt)
    
if employmentDataButton:
    refresh()
    select_employment_data()
    
def create_agent(fileObj):
    llm = OpenAI(temperature=0)
    if '.csv' in fileObj.name:

        bytes_data = fileObj.read()  
        
        with open(os.path.join("/tmp", fileObj.name), "wb") as f:
            f.write(bytes_data)
            file_name = f.name
       
        return create_csv_agent(OpenAI(temperature=0), file_name, verbose=True)
    if '.xlsx' in fileObj.name:
        data = pd.read_excel(fileObj, engine='openpyxl')
        data.to_csv('temp.csv', index=False)
        return create_csv_agent(OpenAI(temperature=0), 'temp.csv', verbose=True)
    if '.xls' in fileObj.name:
        data = pd.read_excel(fileObj)
        data.to_csv('temp.csv', index=False)
        return create_csv_agent(OpenAI(temperature=0), 'temp.csv', verbose=True)

st.title("Comply AI")
if st.session_state != None and "messages" not in st.session_state:
    st.session_state.messages = []
    preselected_uploaded_file = None
    printMessage("assistant", "Started a new session. Please upload a file to analyze...")

if clear:
    refresh()

if submit:
    if uploaded_file == None:
        printMessage("assistant", "Please upload a file for Comply AI to analyze...")
        
    else:
        printMessage("assistant", "Uploading and Analyzing the file. We do not retain any data you upload!")
      
        # agent = create_preselected_agent()
        agent = create_agent(uploaded_file)

        resp  = agent.run("If this document contains employee data (e.g. names, designations, departments, reporting managers, date of joining, date of leaving, applications, and termination dates), Say 'Detected employment data'")
        printMessage("assistant", resp)
        if resp == "Detected employment data":
            st.session_state.data_type = "employment"
            prompt = "Select tests to run \n\n"
            for testKey in employment_tests.keys():
                    prompt = prompt + str(testKey) + " : " + str(employment_tests[testKey]) + "\n\n"
            prompt = prompt + "You can also ask questions to explain the data!"
            printMessage("assistant", prompt)

        else:
            printMessage("assistant", "Data not compatible with known tests, contact sales for more details")


if prompt := st.chat_input():
    if not uploaded_file and preselected_uploaded_file == None:
        printMessage("assistant", "Please upload a file for Comply AI to analyze...")
    elif preselected_uploaded_file != None:
        
        printMessage("user", prompt)
        
        agent = create_preselected_agent()
        
        st.session_state.data_type = "employment"

        if st.session_state.data_type == "employment":
            selectedOption = (prompt.strip())
            if selectedOption in employment_tests.keys():
                response  = agent.run(employment_tests[selectedOption])
            else:
                response  = agent.run(prompt)
            msg = response
            printMessage("assistant", msg)
        
        
    else:
        agent = create_agent(uploaded_file)
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
