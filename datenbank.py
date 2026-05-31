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

def logge_event(event_type):
    """
    Speichert im Hintergrund, ob es ein 'hit' (Cache) oder 'miss' (Gemini) war.
    """
    supabase = init_db()
    try:
        supabase.table('analytics_logs').insert({"event_type": event_type}).execute()
        return True
    except Exception as e:
        # Im Hackathon-Sprint fangen wir den Fehler ab, damit die Haupt-App niemals wegen Analytics abstürzt
        return False

def hole_metriken():
    """
    Zählt die Zeilen in Supabase und gibt (hits, misses) zurück.
    """
    supabase = init_db()
    try:
        # Wir fragen gezielt nach der Anzahl (count) der jeweiligen Zeilen
        hits_res = supabase.table('analytics_logs').select('*', count='exact').eq('event_type', 'hit').execute()
        misses_res = supabase.table('analytics_logs').select('*', count='exact').eq('event_type', 'miss').execute()
        
        # Falls keine Daten da sind, standardmäßig 0 zurückgeben
        hits = hits_res.count if hits_res.count is not None else 0
        misses = misses_res.count if misses_res.count is not None else 0
        
        return hits, misses
    except Exception as e:
        return 0, 0
def hole_alle_prompts(suchbegriff=None):
    """
    Lädt alle bisherigen Fragen alphabetisch aus Supabase.
    Falls ein Suchbegriff eingegeben wurde, wird danach gefiltert.
    """
    try:
        from supabase import create_client, Client
        import streamlit as st
        
        # Sicherstellen, dass Supabase hier erreichbar ist
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase_client: Client = create_client(url, key)
        
        # Wir holen uns alle user_query Einträge aus eurer Tabelle knowledge_base
        abfrage = supabase_client.table("knowledge_base").select("user_query")
        
        # Wenn der Nutzer in der Suchleiste tippt, filtern wir danach
        if suchbegriff:
            abfrage = abfrage.ilike("user_query", f"%{suchbegriff}%")
            
        ergebnis = abfrage.execute()
        
        # Doppelte Einträge löschen (set) und alphabetisch sortieren
        alle_fragen = [zeile["user_query"] for zeile in ergebnis.data if zeile.get("user_query")]
        einzigartige_fragen = sorted(list(set(alle_fragen)))
        
        return einzigartige_fragen
    except Exception as e:
        print(f"Fehler beim Laden der Prompts: {e}")
        return []
