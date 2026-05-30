import streamlit as st

import datenbank
import gemini_api

# 1. Layout-Einstellungen & Sidebar (Einstellungs-Panel)
with st.sidebar:
    st.markdown("### ⚙️ INNOVA Settings")
    api_key = st.text_input("Anthropic API-Key:", type="password", placeholder="sk-ant-...")
    st.markdown("---")
    selected_llm = st.selectbox("Select your LLM-Model:", ["Claude 3.5 Sonnet", "ChatGPT 4o", "Gemini Pro"])
    st.markdown(f"🤖 **Modell:** {selected_llm}.")
    st.markdown("🧠 **Cache:** Supabase DB Aktiv")

# 2. Hauptbereich (Haupt-UI)
st.title("🚀 INNOVA")
st.subheader("Die Evolution der Produktentwicklung")
st.write("Verwandle deine kreative Vision in ein marktreifes Konzept. Ohne Limitierung durch Token und Fragen")

st.markdown("---")

# Eingabebereich in einer sauberen Struktur
user_frage = st.text_input("Welche Nischenfrage zur Produktentwicklung möchtest du analysieren?", 
                           placeholder="z.B. Wie konzipiere ich ein Kühlsystem für ein medizinisches Exoskelett?")

if st.button("Analyse starten", type="primary"):
    if user_frage.strip() == "":
        st.warning("Bitte gib zuerst eine Frage ein.")
    else:
        # Visuelles Feedback für den Nutzer
        with st.status("Verarbeite Anfrage...", expanded=True) as status:
            st.write("🔍 Durchsuche semantischen Speicher (Vektor-Datenbank)...")
            found_result = datenbank.suche_aehnliche_frage(user_frage)
            
            if found_result != None:
                status.update(label="⚡ Cache Hit! Validierte Antwort geladen.", state="complete")
                # Anzeige des Ergebnisses in einer eleganten Box
                st.success(found_result)
            else:
                status.update(label="🧠 Cache Miss. Generiere neue Echtzeit-Analyse via LLM...", state="running")
                
                # Nur NOCH EIN Aufruf mit allen drei Parametern!
                ai_answer = claude_api.frage_claude(user_frage, api_key, selected_llm)
                
                st.write("💾 Speichere neue Erkenntnisse in Vektor-Datenbank...")
                datenbank.speichere_neue_antwort(user_frage, ai_answer)
                
                status.update(label="✨ Analyse erfolgreich abgeschlossen!", state="complete")
                
                # Hochwertige Präsentation der Antwort
                st.markdown("### 🎯 Executive Summary")
                st.info(ai_answer)
                
                # Visualisierungs-Vorschau
                st.markdown("---")
                st.markdown("### 🎨 Visual Blueprints Available")
                st.caption("Du kannst dieses Konzept jetzt im Da Vinci Skizzen-Stil visualisieren lassen.")
                
                # Hier ist der verschmolzene Button:
                if st.button("📦 Da Vinci Blueprint generieren"):
                    st.code("Leonardo da Vinci Skizze eines medizinischen Exoskeletts, Sepia, detaillierte Mechanik, fotorealistische Schraffur")
