import streamlit as st
from openai import OpenAI

# Wir laden den OpenAI Key sicher aus den Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def erstelle_vektor(text):
    """
    Aufgabe: Wandelt den Text des Nutzers in eine Zahlenfolge (1536 Dimensionen) um.
    Das braucht die datenbank.py zwingend für die Supabase-Suche.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Fehler bei der Vektor-Erstellung: {e}")
        return None

def generiere_innova_antwort(user_query, cache_vorwissen=None):
    """
    Aufgabe: Generiert die strukturierte Produkt-Analyse.
    """
    # Eure festgelegte Struktur (Executive Summary, Aktionsplan, Insights, Risiken)
    system_prompt = """
    Du bist 'Innova', ein High-End-Berater für strategische Produktentwicklung.
    Deine Antworten müssen IMMER in genau 4 Abschnitte gegliedert sein:
    1. Executive Summary
    2. Aktionsplan (🧩)
    3. Insights (💡) & Mindset (🧠)
    4. Risiko-Radar (⚠️)
    Antworte professionell, präzise und lösungsorientiert.
    """

    # Wenn wir einen Treffer in der Datenbank hatten, geben wir das als Vorwissen mit!
    if cache_vorwissen:
        system_prompt += f"\n\nWICHTIG: Ein ähnliches Projekt wurde bereits analysiert. Nutze dieses Vorwissen als Basis und passe es auf die neue Idee an:\n{cache_vorwissen}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Extrem schnell und günstig für Prototypen
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Fehler bei der Text-Generierung: {e}")
        return "Entschuldigung, die KI ist gerade nicht erreichbar."
