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
        # Visuelles Feedback für den Nutzer (von deiner Partnerin)
        with st.status("Verarbeite Anfrage...", expanded=True) as status:
            
            st.write("🧩 Übersetze Frage für die Datenbank...")
            # SCHRITT 1: Text für Supabase vorbereiten (Gemini Embedding)
            query_embedding = gemini_api.erstelle_vektor(user_frage)
            
            if query_embedding:
                st.write("🔍 Durchsuche semantischen Speicher (Supabase Vektor-DB)...")
                # SCHRITT 2: In Supabase suchen
                found_result, similarity = datenbank.suche_aehnliche_frage(query_embedding)
                
                if found_result:
                    status.update(label=f"⚡ Cache Hit! Validierte Antwort geladen (Ähnlichkeit: {similarity*100:.1f}%).", state="complete")
                    ai_answer = found_result # Wir übernehmen die Antwort aus dem Gedächtnis
                else:
                    status.update(label="🧠 Cache Miss. Generiere neue Echtzeit-Analyse via Gemini...", state="running")
                    
                    # SCHRITT 3: Neue Antwort von Gemini generieren lassen
                    ai_answer = ki_api.generiere_innova_antwort(user_frage)
                    
                    st.write("💾 Speichere neue Erkenntnisse in Vektor-Datenbank...")
                    # SCHRITT 4: Neue Idee in Supabase abspeichern
                    datenbank.speichere_neue_antwort(user_frage, query_embedding, ai_answer)
                    
                    status.update(label="✨ Analyse erfolgreich abgeschlossen!", state="complete")
                
                # Hochwertige Präsentation der Antwort (von deiner Partnerin)
                st.markdown("### 🎯 Executive Summary")
                st.info(ai_answer)
                
                # Visualisierungs-Vorschau
                st.markdown("---")
                st.markdown("### 🎨 Visual Blueprints Available")
                st.caption("Du kannst dieses Konzept jetzt im Da Vinci Skizzen-Stil visualisieren lassen.")
                
                # Hier ist der verschmolzene Button:
                if st.button("📦 Da Vinci Blueprint generieren"):
                    st.code("Leonardo da Vinci Skizze eines medizinischen Exoskeletts, Sepia, detaillierte Mechanik, fotorealistische Schraffur")
            
            else:
                status.update(label="❌ Fehler: Konnte KI nicht erreichen.", state="error")
