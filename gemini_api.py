import streamlit as st
import google.generativeai as genai

# 1. Den sicheren Key aus der secrets.toml laden
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def erstelle_vektor(text):
    """
    Übersetzer: Wandelt den Text in Zahlen für die Supabase-Datenbank um.
    """
    try:
        # Wir fragen Google: Welches Embedding-Modell ist verfügbar?
        verfuegbares_modell = None
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                verfuegbares_modell = m.name
                break
                
        if not verfuegbares_modell:
            st.error("Google-Server sagt: Kein Embedding-Modell freigeschaltet!")
            return None
            
        # Wir zwingen Google, den Vektor auf 1536 Dimensionen für Supabase zu kürzen!
        result = genai.embed_content(
            model=verfuegbares_modell,
            content=text,
            output_dimensionality=1536  # <--- DER MAGISCHE BRIEFKASTEN-FIX
        )
        return result['embedding']
    except Exception as e:
        st.error(f"Fehler bei der Vektor-Erstellung: {e}")
        return None

def generiere_innova_antwort(user_query, cache_vorwissen=None):
    """
    Erzähler: Generiert die strukturierte Produkt-Analyse.
    """
    system_prompt = """
    Du bist 'Innova', ein High-End-Berater für strategische Produktentwicklung.
    Deine Antworten müssen IMMER in genau 4 Abschnitte gegliedert sein:
    1. Executive Summary
    2. Aktionsplan (🧩)
    3. Insights (💡) & Mindset (🧠)
    4. Risiko-Radar (⚠️)
    Antworte professionell, präzise und lösungsorientiert.
    Nutze für den Aktionsplan immer eine strikte Dezimal-Gliederung (z.B. 1.1, 1.2, 2.1).
    """

    if cache_vorwissen:
        system_prompt += f"\n\nWICHTIG: Ein ähnliches Projekt wurde bereits analysiert. Nutze dieses Vorwissen als Basis und passe es auf die neue Idee an:\n{cache_vorwissen}"

    try:
        # Wir suchen das korrekte "flash" Modell, egal wie Google es heute nennt
        verfuegbares_flash_modell = 'gemini-1.5-flash-latest' # Fallback
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                verfuegbares_flash_modell = m.name
                break

        # Wir nutzen das gefundene Modell
        model = genai.GenerativeModel(
            model_name=verfuegbares_flash_modell,
            system_instruction=system_prompt
        )
        
        response = model.generate_content(user_query)
        return response.text
    except Exception as e:
        st.error(f"Fehler bei der Text-Generierung: {e}")
        return "Entschuldigung, Innova ist gerade nicht erreichbar."
