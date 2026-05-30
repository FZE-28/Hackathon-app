import streamlit as st
import chromadb

@st.cache_resource
def lade_datenbank():
    client = chromadb.PersistentClient(path="./ki_speicher")
    collection = client.get_or_create_collection(name="produktentwicklung")
    return collection
  
db = lade_datenbank()




st.title("Product development")
st.write("Ask your question.")
user_frage = st.text_input("Enter your prompt here")

if st.button("Send"):
  st.write("We are looking for you in the database")
