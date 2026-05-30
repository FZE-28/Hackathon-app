import streamlit as st
import google.generativeai as genai

# 1. Den sicheren Key aus der secrets.toml laden
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def erstelle_vektor(text):
    """
    Übersetzer: Wandelt den Text in Zahlen für die Supabase-Datenbank um.
    """
    try:
        # 1. Wir fragen Google: Welches Embedding-Modell ist für uns verfügbar?
        verfuegbares_modell = None
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                verfuegbares_modell = m.name
                break # Wir nehmen direkt das erste Modell, das den Test besteht!
                
        if not verfuegbares_modell:
            st.error("Google-Server sagt: Kein Embedding-Modell für diesen API-Key freigeschaltet!")
            return None
            
        # 2. Wir nutzen exakt dieses gefundene Modell für die Übersetzung
        result = genai.embed_content(
            model=verfuegbares_modell,
            content=text
        )
        return result['embedding']
    except Exception as e:
        st.error(f"Fehler bei der Vektor-Erstellung: {e}")
        return None

def generiere_innova_antwort(user_query, cache_vorwissen=None):
    """
    Erzähler: Generiert die strukturierte Produkt-Analyse.
    """
    # Eure festgelegte Struktur
    system_prompt = """
    Du bist 'Innova', ein High-End-Berater für strategische Produktentwicklung.
    Deine Antworten müssen IMMER in genau 4 Abschnitte gegliedert sein:
    1. Executive Summary
    2. Aktionsplan (🧩)
    3. Insights (💡) & Mindset (🧠)
    4. Risiko-Radar (⚠️)
    Antworte professionell, präzise und lösungsorientiert.
    """

    # Wenn Supabase Vorwissen gefunden hat, geben wir das Gemini mit!
    if cache_vorwissen:
        system_prompt += f"\n\nWICHTIG: Ein ähnliches Projekt wurde bereits analysiert. Nutze dieses Vorwissen als Basis und passe es auf die neue Idee an:\n{cache_vorwissen}"

    try:
        # Wir nutzen das super-schnelle Gemini 1.5 Flash Modell
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )
        
        # Antwort generieren
        response = model.generate_content(user_query)
        return response.text
    except Exception as e:
        st.error(f"Fehler bei der Text-Generierung: {e}")
        return "Entschuldigung, Innova ist gerade nicht erreichbar."
