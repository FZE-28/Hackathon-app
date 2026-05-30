import streamlit as st
from supabase import create_client, Client

def init_db():
    # Holt die URL und den Key aus den sicheren Streamlit-Secrets
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    
    # Baut die Verbindung auf
    supabase: Client = create_client(url, key)
    return supabase

def suche_aehnliche_frage(query_embedding):
    supabase = init_db()
    
    # Ruft die Supabase-Funktion für die Vektorsuche auf
    response = supabase.rpc(
        "match_questions",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.85,
            "match_count": 1
        }
    ).execute()

    # Gibt die Antwort zurück, wenn ein Treffer gefunden wurde
    if response.data and len(response.data) > 0:
        return response.data[0]['ai_response'], response.data[0]['similarity']
    
    return None, 0.0

def speichere_neue_antwort(user_query, query_embedding, ai_response):
    supabase = init_db()
    
    # Speichert die neue Frage und Antwort in der Tabelle
    supabase.table('knowledge_base').insert(
        {
            "user_query": user_query,
            "embedding": query_embedding,
            "ai_response": ai_response
        }
    ).execute()
    
    return True
