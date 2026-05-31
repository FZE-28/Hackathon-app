import streamlit as st
import datenbank
import gemini_api
import urllib.parse

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
if "eingabe_text" not in st.session_state:
    st.session_state.eingabe_text = ""
if "run_sidebar_prompt" not in st.session_state:
    st.session_state.run_sidebar_prompt = None

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
    
    # --- CHAT-VERLAUF EXPORTIEREN ---
    st.markdown("💾 **Session exportieren**")
    chat_export = ""
    for msg in st.session_state.messages:
        rolle = "Du" if msg["role"] == "user" else "Innova"
        chat_export += f"[{rolle}]: {msg['content']}\n\n"
        
    st.download_button(
        label="📥 Gesamten Chat herunterladen",
        data=chat_export,
        file_name="innova_chatverlauf.txt",
        use_container_width=True
    )
    st.markdown("---")
    
    # --- DER BRAINSTORM-SCHALTER ---
    brainstorm_mode = st.toggle("🌌 Brainstorm-Modus aktivieren", help="Wechselt vom strengen Blueprint zu historischer Inspiration und freiem Brainstorming.")
    
    # --- NEU: INSPIRATION DIREKT IN DER SEITENLEISTE ---
    st.markdown("---")
    st.markdown("### 💡 Prompt-Bibliothek")
    suchbegriff = st.text_input("🔍 Suche in alten Prompts:")
    
    prompts_aus_db = datenbank.hole_alle_prompts(suchbegriff)
    
    if not prompts_aus_db:
        st.caption("Keine Prompts gefunden.")
    else:
        # Wir zeigen die Prompts als kleine Buttons an
        for p in prompts_aus_db:
            if st.button(f"📄 {p[:35]}...", key=f"btn_{p}", help=p):
                st.session_state.eingabe_text = p
                st.rerun()
                
    # Wenn ein Prompt angeklickt wurde, zeigen wir ein Editier-Feld!
    if st.session_state.eingabe_text:
        st.markdown("**✏️ Prompt anpassen & starten:**")
        edited_prompt = st.text_area("Hier bearbeiten:", value=st.session_state.eingabe_text, height=120)
        
        if st.button("🚀 Aus Seitenleiste starten", type="primary", use_container_width=True):
            st.session_state.run_sidebar_prompt = edited_prompt
            st.session_state.eingabe_text = "" # Feld danach wieder aufräumen
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

# Eingabebereich in einer sauberen Struktur (Design der Partnerin)
user_frage = st.chat_input("Welche Nischenfrage zur Produktentwicklung möchtest du analysieren?")

# --- DER MAGISCHE TRICK FÜR DIE SEITENLEISTE ---
if st.session_state.run_sidebar_prompt:
    user_frage = st.session_state.run_sidebar_prompt
    st.session_state.run_sidebar_prompt = None # Danach direkt wieder leeren

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
                
                # Im Brainstorm-Modus umgehen wir den Cache
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
                    
                    query_for_api = user_frage
                    if brainstorm_mode:
                        query_for_api = f"WICHTIG: Kreativer Brainstorming-Modus! 1. Nenne EINEN historischen Meilenstein zu '{user_frage}' in maximal 2 Sätzen. 2. Biete mir danach exakt 3 radikal neue, visionäre Richtungen als kurze Stichpunkte an, aus denen ich für das weitere Brainstorming wählen kann. Keine langen Texte!"
                    
                    ai_answer = gemini_api.generiere_innova_antwort(query_for_api)
                    
                    st.write("💾 Lege Antwort zur Überprüfung in den Zwischenspeicher...")
                    st.session_state.ai_answer = ai_answer
                    st.session_state.query_embedding = query_embedding
                    st.session_state.current_question = user_frage
                    st.session_state.cache_hit = False
                    
                    if not brainstorm_mode:
                        datenbank.logge_event('miss')
                    
                    status.update(label="✨ Analyse erfolgreich abgeschlossen!", state="complete")
                
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.ai_answer})
            
            else:
                status.update(label="❌ Fehler: Konnte KI nicht erreichen.", state="error")


# --- NEUER ABSCHNITT: ANZEIGE & BEWERTUNG ---
if st.session_state.ai_answer:
    
    st.markdown("### 🎯 Executive Summary")
    st.info(st.session_state.ai_answer)

    st.download_button(
        label="📥 Aktuelle Analyse herunterladen", 
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
    
    col1, col2 = st.columns(2)
    
    # --- LINKE SPALTE: BILDGENERIERUNG ---
    with col1:
        st.markdown("**🖼️ Konzept-Skizze**")
        if st.button("📦 Da Vinci Blueprint (BILD) generieren", use_container_width=True):
            with st.spinner("Da Vinci malt dein Konzept..."):
                try:
                    bild_prompt = f"Leonardo da Vinci sketch of {st.session_state.current_question}, detailed mechanics, sepia, technical drawing, high resolution"
                    encoded_prompt = urllib.parse.quote(bild_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"
                    
                    # Der HTML Trick: Crasht niemals, weil der Browser das Bild lädt, nicht Streamlit!
                    st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 10px; border: 2px solid #ccc;">', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Bild konnte nicht geladen werden.")
                
    # --- RECHTE SPALTE: DIAGRAMME ---
    with col2:
        st.markdown("**🧩 Architektur & Prozess**")
        diagramm_typ = st.radio("Typ:", ["Mindmap (Struktur)", "Flussdiagramm (Prozess)"], horizontal=True)
        
        if st.button("Diagramm zeichnen", use_container_width=True):
            with st.spinner(f"Erstelle {diagramm_typ}..."):
                if "Mindmap" in diagramm_typ:
                    graph_prompt = f"Erstelle eine detaillierte Mindmap im Graphviz DOT-Format für das Konzept: {st.session_state.current_question}. Erstelle einen zentralen Knoten und fächere ihn in mindestens 4 Kategorien auf. Antworte NUR mit dem DOT-Code (startend mit digraph)."
                else:
                    graph_prompt = f"Erstelle ein detailliertes Flussdiagramm im Graphviz DOT-Format, das den Entwicklungsprozess für: {st.session_state.current_question} beschreibt. Zeige Start, Schritte und Entscheidungen. Antworte NUR mit dem DOT-Code."
                
                dot_code = gemini_api.generiere_innova_antwort(graph_prompt)
                
                if "```" in dot_code:
                    try:
                        dot_code = dot_code.split("```")[1]
                        if dot_code.startswith("dot"):
                            dot_code = dot_code[3:]
                    except:
                        pass
                
                st.graphviz_chart(dot_code)
                
                # --- NEU: DOWNLOAD FÜR DAS DIAGRAMM ---
                st.download_button(
                    label="📥 Diagramm-Code (DOT) speichern",
                    data=dot_code,
                    file_name="innova_architektur.dot",
                    mime="text/plain",
                    help="Diesen Code kannst du auf Seiten wie 'Graphviz Online' jederzeit wieder in ein Bild verwandeln."
                )
