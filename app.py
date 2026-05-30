import streamlit as st


st.title("Product development")
st.write("Ask your question.")
user_frage = st.text_input("Enter your prompt here")

if st.button("Send"):
  st.write("We are looking for you in the database")
