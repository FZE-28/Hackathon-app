import streamlit as st
from supabase import create_client, Client

def init_db():
    """
    Stellt die Verbindung zu Supabase her, basierend auf den Secrets.
    """
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    
    supabase: Client = create_client(url, key)
    return supabase

def suche_aehnliche_frage(query_embedding):
    """
    Sucht in Supabase nach einer ähnlichen Frage anhand des Vektors.
    """
    supabase = init_db()
    
    try:
        response = supabase.rpc(
            "match_questions",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.85, # Ab 85% Ähnlichkeit ist es ein Treffer
                "match_count": 1
            }
        ).execute()

        if response.data and len(response.data) > 0:
            bester_treffer = response.data[0]
            return bester_treffer['ai_response'], bester_treffer['similarity']
        
        return None, 0.0
    except Exception as e:
        st.error(f"Fehler bei der Suche in der Datenbank: {e}")
        return None, 0.0

def speichere_neue_antwort(user_query, query_embedding, ai_response):
    """
    Speichert eine neue Frage samt Antwort und Vektor in der Datenbank.
    """
    supabase = init_db()
    
    try:
        supabase.table('knowledge_base').insert(
            {
                "user_query": user_query,
                "embedding": query_embedding,
                "ai_response": ai_response
            }
        ).execute()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False
