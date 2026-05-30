import streamlit as st
import datenbank
import gemini_api

# 1. Layout-Einstellungen & Sidebar (Einstellungs-Panel)
with st.sidebar:
    st.markdown("### ⚙️ INNOVA Settings")
    # Das Design der Partnerin bleibt! Das Feld ist jetzt "disabled", da wir den Key 
    # profimäßig und unsichtbar über die secrets.toml laden.
    api_key = st.text_input("API-Key:", placeholder="Wird sicher aus secrets.toml geladen", disabled=True)
    st.markdown("---")
    
    # Dropdown bleibt für die Optik, aber wir forcieren unser schnelles Gemini
    selected_llm = st.selectbox("Select your LLM-Model:", ["Claude 3.5 Sonnet", "ChatGPT 4o", "Gemini 1.5 Flash (Aktiv)"], index=2)
    st.markdown(f"🤖 **Modell:** Gemini 1.5 Flash (Vektoren & Text).")
    st.markdown("🧠 **Cache:** Supabase DB Aktiv")

    anzahl_hits, anzahl_misses = datenbank.hole_metriken()
    
    st.markdown("📊 **Live-Performance (Cloud):**")
    st.metric(label="⚡ Cache-Treffer (Geld gespart)", value=anzahl_hits)
    st.metric(label="🧠 Gemini Live-Anfragen", value=anzahl_misses)
    st.markdown("---")
    


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
        # WICHTIG: Alten Speicher zurücksetzen bei neuer Frage
        st.session_state.ai_answer = None
        st.session_state.bewertung_abgegeben = False
        
        with st.status("Verarbeite Anfrage...", expanded=True) as status:
            st.write("🧩 Übersetze Frage für die Datenbank...")
            query_embedding = gemini_api.erstelle_vektor(user_frage)
            
            if query_embedding:
                st.write("🔍 Durchsuche semantischen Speicher (Supabase Vektor-DB)...")
                found_result, similarity = datenbank.suche_aehnliche_frage(query_embedding)
                
                if found_result:
                    status.update(label=f"⚡ Cache Hit! Validierte Antwort geladen (Ähnlichkeit: {similarity*100:.1f}%).", state="complete")
                    
                    # Antwort für die Anzeige im Gedächtnis speichern
                    st.session_state.ai_answer = found_result 
                    st.session_state.cache_hit = True
                    datenbank.logge_event('hit')
                else:
                    status.update(label="🧠 Cache Miss. Generiere neue Echtzeit-Analyse via Gemini...", state="running")
                    ai_answer = gemini_api.generiere_innova_antwort(user_frage)
                    
                    st.write("💾 Lege Antwort zur Überprüfung in den Zwischenspeicher...")
                    # HIER IST DIE ÄNDERUNG: Wir speichern noch nicht in Supabase, sondern nur ins Gedächtnis!
                    st.session_state.ai_answer = ai_answer
                    st.session_state.query_embedding = query_embedding
                    st.session_state.current_question = user_frage
                    st.session_state.cache_hit = False
                    datenbank.logge_event('miss')
                    
                    status.update(label="✨ Analyse erfolgreich abgeschlossen!", state="complete")
            else:
                status.update(label="❌ Fehler: Konnte KI nicht erreichen.", state="error")


# --- NEUER ABSCHNITT: ANZEIGE & BEWERTUNG (Unabhängig vom Analyse-Button) ---
if st.session_state.ai_answer:
    
    # Hochwertige Präsentation der Antwort
    st.markdown("### 🎯 Executive Summary")
    st.info(st.session_state.ai_answer)
    
    # Bewertungssystem (Taucht nur auf, wenn die Antwort NEU ist und noch nicht bewertet wurde)
    if not st.session_state.cache_hit and not st.session_state.bewertung_abgegeben:
        st.markdown("---")
        st.markdown("### 💬 Qualitätskontrolle: Soll Innova diese Antwort lernen?")
        
        bewertung = st.radio("Wie gut ist diese Analyse?", 
                             ["yes (Sehr gut)", "neutral (Akzeptabel)", "no (Unbrauchbar/Falsch)"], 
                             horizontal=True)
        
        if st.button("Auswahl bestätigen & Logik ausführen"):
            st.session_state.bewertung_abgegeben = True
            
            if "no" in bewertung:
                st.error("❌ Innova verwirft diese Antwort. Sie wird NICHT in Supabase gespeichert.")
            else:
                # Nur bei yes oder neutral wird die echte Datenbank-Funktion ausgelöst
                datenbank.speichere_neue_antwort(
                    st.session_state.current_question, 
                    st.session_state.query_embedding, 
                    st.session_state.ai_answer
                )
                st.success(f"💾 Innova hat gelernt! Antwort als '{bewertung.split()[0]}' in Supabase gesichert.")
            
            st.rerun() # Lädt die App kurz neu, um die Button-Logik sauber abzuschließen

    # Visualisierungs-Vorschau
    st.markdown("---")
    st.markdown("### 🎨 Visual Blueprints Available")
    st.caption("Du kannst dieses Konzept jetzt im Da Vinci Skizzen-Stil visualisieren lassen.")
    
    if st.button("📦 Da Vinci Blueprint generieren"):
        st.code("Leonardo da Vinci Skizze eines medizinischen Exoskeletts, Sepia, detaillierte Mechanik, fotorealistische Schraffur")
    # Hier ist der verschmolzene Button:
    if st.button("📦 Da Vinci Blueprint generieren"):
        st.code("Leonardo da Vinci Skizze eines medizinischen Exoskeletts, Sepia, detaillierte Mechanik, fotorealistische Schraffur")
