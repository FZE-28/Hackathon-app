import streamlit as st
import google.generativeai as genai

# 1. Den sicheren Key aus der secrets.toml laden
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def erstelle_vektor(text):
    """
    Übersetzer: Wandelt den Text in Zahlen für die Supabase-Datenbank um.
    """
    try:
        # Wir nutzen das spezielle Embedding-Modell von Gemini
        result = genai.embed_content(
            model="models/embedding-001",
            content=text
        )
        # Gibt die Zahlenreihe (den Vektor) zurück
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
