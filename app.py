import streamlit as st
import datenbank.py  
import claude_api.py 

linke_spalte, rechte_spalte = st.columns(2)

with linke_spalte:
    st.write("Hier könnte ein Bild oder eine Erklärung stehen.")

with rechte_spalte:
    user_frage = st.text_input("Dein Prompt:")

st.title("Product development")
st.write("Ask your question.")
user_frage = st.text_input("Enter your prompt here")

#datenbank.suche_aehnliche_frage(text)
#datenbank.speichere_neue_antwort(frage, antwort)
#claude_api.frage_claude(text)

if st.button("Send"):
  st.write("We are looking for you in the database")
  found_result = datenbank.suche_aehnliche_frage(user_frage)
  if found_result != None:
    st.write(found_result)
  else:
    ai_answer = claude_api.frage_claude(user_frage)
    datenbank.speichere_neue_antwort(user_frage, ai_answer)
    st.write(ai_answer)

