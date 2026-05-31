import streamlit as st
import datenbank
import gemini_api

# --- KUGELSICHERES KURZZEITGEDÄCHTNIS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None
if "query_embedding" not in st.session_state:
    st.session_state.query_embedding = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "cache_hit" not in st.session_state:
    st.session_state.cache_hit = False
if "bewertung_abgegeben" not in st.session_state:
    st.session_state.bewertung_abgegeben = False

if "show_inspiration" not in st.session_state:
    st.session_state.show_inspiration = False
if "eingabe_text" not in st.session_state:
    st.session_state.eingabe_text = ""

# 1. Layout-Einstellungen & Sidebar (Einstellungs-Panel)
with st.sidebar:
    st.markdown("### ⚙️ INNOVA Settings")
    api_key = st.text_input("API-Key:", placeholder="Wird sicher aus secrets.toml geladen", disabled=True)
    st.markdown("---")
    
    selected_llm = st.selectbox("Select your LLM-Model:", ["Claude 3.5 Sonnet", "ChatGPT 4o", "Gemini 1.5 Flash (Aktiv)"], index=2)
    st.markdown(f"🤖 **Modell:** Gemini 1.5 Flash (Vektoren & Text).")
    st.markdown("🧠 **Cache:** Supabase DB Aktiv")

    anzahl_hits, anzahl_misses = datenbank.hole_metriken()
    
    st.markdown("📊 **Live-Performance (Cloud):**")
    st.metric(label="⚡ Cache-Treffer (Geld gespart)", value=anzahl_hits)
    st.metric(label="🧠 Gemini Live-Anfragen", value=anzahl_misses)

    st.markdown("---")
    
    # --- NEU: DER BRAINSTORM-SCHALTER ---
    brainstorm_mode = st.toggle("🌌 Brainstorm-Modus aktivieren", help="Wechselt vom strengen Blueprint zu historischer Inspiration und freiem Brainstorming.")
    
    st.markdown("---")
    if st.button("💡 Prompt-Inspiration öffnen/schließen", use_container_width=True):
        st.session_state.show_inspiration = not st.session_state.show_inspiration
        st.rerun()


# 2. Hauptbereich (Haupt-UI)
st.title("🚀 INNOVA")
st.subheader("Die Evolution der Produktentwicklung")
st.write("Verwandle deine kreative Vision in ein marktreifes Konzept. Ohne Limitierung durch Token und Fragen")

st.markdown("---")

# --- CHAT-HISTORIE ANZEIGEN ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabebereich in einer sauberen Struktur
user_frage = st.chat_input("Welche Nischenfrage zur Produktentwicklung möchtest du analysieren?")

if user_frage: 
    with st.chat_message("user"):
        st.markdown(user_frage)
    
    st.session_state.messages.append({"role": "user", "content": user_frage})
    
    if user_frage.strip() == "":
        st.warning("Bitte gib zuerst eine Frage ein.")
    else:
        st.session_state.ai_answer = None
        st.session_state.bewertung_abgegeben = False
        
        with st.status("Verarbeite Anfrage...", expanded=True) as status:
            st.write("🧩 Übersetze Frage für die Datenbank...")
            query_embedding = gemini_api.erstelle_vektor(user_frage)
            
            if query_embedding:
                st.write("🔍 Durchsuche semantischen Speicher (Supabase Vektor-DB)...")
                
                # Im Brainstorm-Modus umgehen wir den strengen Cache am besten, damit frische Ideen kommen
                if brainstorm_mode:
                    found_result = None
                    st.write("🌌 Brainstorm-Modus aktiv: Cache wird für kreative Iteration übersprungen.")
                else:
                    found_result, similarity = datenbank.suche_aehnliche_frage(query_embedding)
                
                if found_result:
                    status.update(label=f"⚡ Cache Hit! Validierte Antwort geladen (Ähnlichkeit: {similarity*100:.1f}%).", state="complete")
                    st.session_state.ai_answer = found_result 
                    st.session_state.cache_hit = True
                    datenbank.logge_event('hit')
                else:
                    status.update(label="🧠 Cache Miss. Generiere neue Echtzeit-Analyse via Gemini...", state="running")
                    
                    # --- NEU: DIE MODUS-WEICHE FÜR GEMINI ---
                    query_for_api = user_frage
                    if brainstorm_mode:
                        query_for_api = f"WICHTIG: Nutze den kreativen Brainstorming-Modus! Ignoriere den strikten 4-Punkte-Blueprint. Nenne historische Meilensteine und Erfindungen zum Thema '{user_frage}' und brainstorme darauf aufbauend völlig neue, visionäre Schnittstellen und Konzepte für die Zukunft."
                    
                    ai_answer = gemini_api.generiere_innova_antwort(query_for_api)
                    
                    st.write("💾 Lege Antwort zur Überprüfung in den Zwischenspeicher...")
                    st.session_state.ai_answer = ai_answer
                    st.session_state.query_embedding = query_embedding
                    st.session_state.current_question = user_frage
                    st.session_state.cache_hit = False
                    
                    if not brainstorm_mode:
                        datenbank.logge_event('miss')
                    
                    status.update(label="✨ Analyse erfolgreich abgeschlossen!", state="complete")
                
                # HIER IST DIE KORRIGIERTE EINRÜCKUNG!
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.ai_answer})
            
            else:
                status.update(label="❌ Fehler: Konnte KI nicht erreichen.", state="error")


# --- NEUER ABSCHNITT: ANZEIGE & BEWERTUNG ---
if st.session_state.ai_answer:
    
    st.markdown("### 🎯 Executive Summary")
    st.info(st.session_state.ai_answer)

    st.download_button(
        label="📥 Innova-Analyse herunterladen", 
        data=st.session_state.ai_answer, 
        file_name="innova_analyse.txt" 
    )
    
    if not st.session_state.cache_hit and not st.session_state.bewertung_abgegeben and not brainstorm_mode:
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
                datenbank.speichere_neue_antwort(
                    st.session_state.current_question, 
                    st.session_state.query_embedding, 
                    st.session_state.ai_answer
                )
                st.success(f"💾 Innova hat gelernt! Antwort als '{bewertung.split()[0]}' in Supabase gesichert.")
            
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎨 Visual Blueprints Available")
    st.caption("Du kannst dieses Konzept jetzt im Da Vinci Skizzen-Stil visualisieren lassen.")
    
    if st.button("📦 Da Vinci Blueprint generieren"):
        st.code("Leonardo da Vinci Skizze eines medizinischen Exoskeletts, Sepia, detaillierte Mechanik, fotorealistische Schraffur")


# --- NEUES FEATURE: BRAINSTORM & INSPIRATION PANEL (RECHTS) ---
if st.session_state.show_inspiration:
    st.markdown("""
        <style>
        .inspiration-box {
            background-color: #162447;
            padding: 15px;
            border-radius: 10px;
            border-left: 3px solid #FFD700;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("💡 **Inspirations-Modus ist AKTIV**")
    
    with st.expander("✨ Vorherige Prompts durchsuchen & laden", expanded=True):
        suchbegriff = st.text_input("🔍 Stichwort-Suche für Prompts:", placeholder="z.B. Exoskelett...")
        
        prompts_aus_db = datenbank.hole_alle_prompts(suchbegriff)
        
        st.markdown("**Verfügbare Prompts :**")
        
        if not prompts_aus_db:
            st.caption("Keine passenden Prompts in der Datenbank gefunden.")
        else:
            for p in prompts_aus_db:
                if st.button(f"📄 {p}", key=f"btn_{p}", use_container_width=True):
                    st.session_state.eingabe_text = p
                    st.rerun()
