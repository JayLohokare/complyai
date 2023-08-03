import streamlit as st
import os
from fastapi import FastAPI, UploadFile, File
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import time
from streamlit_chat import message

app = FastAPI()

# Define the directory to store uploaded CSV files
UPLOAD_DIR = "uploads"

# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY'

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    submit = st.button("Submit")
    

st.title("💬 CSV Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please upload your CSV to proceed..."}]



for msg in st.session_state.messages:
    print(msg)
    st.chat_message(msg["role"]).write(msg["content"])

if submit:
    file_path = os.path.join(UPLOAD_DIR, 'upload.csv')
    agent = create_csv_agent(OpenAI(temperature=0), file_path, verbose=True)
    res1  = agent.run("What does this document contains and what type of insights that we can get from this?")
    st.session_state.messages.append({"role": "assistant", "content": res1})
    st.chat_message("assistant").write(res1)

if prompt := st.chat_input():
    if not uploaded_file:
        st.info("Please upload your CSV to continue.")
        st.stop()
    # else:
         
    file_path = os.path.join(UPLOAD_DIR, 'upload.csv')
    agent = create_csv_agent(OpenAI(temperature=0), file_path, verbose=True)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    response  = agent.run(prompt)
    msg = response
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)