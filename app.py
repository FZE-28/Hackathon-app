import streamlit as st
import datenbank
import gemini_api
import urllib.parse

# --- 1. KUGELSICHERES SETUP & STATE ---
st.set_page_config(page_title="INNOVA", page_icon="🚀", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "eingabe_text" not in st.session_state:
    st.session_state.eingabe_text = ""
if "run_sidebar_prompt" not in st.session_state:
    st.session_state.run_sidebar_prompt = None

# --- 2. SIDEBAR (PROFESSIONELLES DASHBOARD) ---
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
    
    # --- PROMPT-BIBLIOTHEK (VOM KOLLEGEN) ---
    st.markdown("---")
    st.markdown("### 💡 Prompt-Bibliothek")
    suchbegriff = st.text_input("🔍 Suche in alten Prompts:")
    
    prompts_aus_db = datenbank.hole_alle_prompts(suchbegriff)
    
    if not prompts_aus_db:
        st.caption("Keine Prompts gefunden.")
    else:
        for p in prompts_aus_db:
            if st.button(f"📄 {p[:35]}...", key=f"btn_{p}", help=p):
                st.session_state.eingabe_text = p
                st.rerun()
                
    if st.session_state.eingabe_text:
        st.markdown("**✏️ Prompt anpassen & starten:**")
        edited_prompt = st.text_area("Hier bearbeiten:", value=st.session_state.eingabe_text, height=120)
        
        if st.button("🚀 Aus Seitenleiste starten", type="primary", use_container_width=True):
            st.session_state.run_sidebar_prompt = edited_prompt
            st.session_state.eingabe_text = ""
            st.rerun()


# --- 3. HAUPT-UI ---
st.title("🚀 INNOVA")
st.subheader("Die Evolution der Produktentwicklung")
st.write("Verwandle deine kreative Vision in ein marktreifes Konzept. Ohne Limitierung durch Token und Fragen")
st.markdown("---")

# Chat-Historie rendern (Echtes ChatGPT Feeling)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. CHAT-LOGIK & EINGABE ---
# Kombinierter Input: Entweder aus dem Chatfeld ODER aus der Seitenleiste vom Kollegen
chat_input_text = st.chat_input("Welche Nischenfrage zur Produktentwicklung möchtest du analysieren?")
user_frage = chat_input_text or st.session_state.run_sidebar_prompt

if user_frage: 
    # Seitenleisten-Trigger zurücksetzen
    st.session_state.run_sidebar_prompt = None
    
    if user_frage.strip() == "":
        st.warning("Bitte gib zuerst eine Frage ein.")
    else:
        # 1. User Frage ins UI und Gedächtnis
        with st.chat_message("user"):
            st.markdown(user_frage)
        st.session_state.messages.append({"role": "user", "content": user_frage})
        st.session_state.current_question = user_frage
        
        # 2. Innova Antwort generieren (im echten Chat-UI)
        with st.chat_message("assistant"):
            with st.status("Verarbeite Anfrage...", expanded=True) as status:
                st.write("🧩 Übersetze Frage für die Datenbank...")
                query_embedding = gemini_api.erstelle_vektor(user_frage)
                
                if query_embedding:
                    st.write("🔍 Durchsuche semantischen Speicher (Supabase Vektor-DB)...")
                    found_result, similarity = datenbank.suche_aehnliche_frage(query_embedding)
                    
                    if found_result:
                        status.update(label=f"⚡ Cache Hit! Validierte Antwort geladen (Ähnlichkeit: {similarity*100:.1f}%).", state="complete")
                        ai_answer = found_result 
                        datenbank.logge_event('hit')
                    else:
                        status.update(label="🧠 Cache Miss. Generiere neue Echtzeit-Analyse via Gemini...", state="running")
                        ai_answer = gemini_api.generiere_innova_antwort(user_frage)
                        
                        st.write("💾 Speichere neues Wissen direkt in Supabase...")
                        # Für den Pitch: Wir speichern direkt, um den lästigen Bewertungs-Klick zu sparen!
                        datenbank.speichere_neue_antwort(user_frage, query_embedding, ai_answer)
                        datenbank.logge_event('miss')
                        
                        status.update(label="✨ Analyse erfolgreich abgeschlossen & gelernt!", state="complete")
                    
                    # Antwort sofort im Chat-Fenster anzeigen
                    st.markdown(ai_answer)
                    
                    # Antwort in den Rucksack packen
                    st.session_state.ai_answer = ai_answer
                    st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                else:
                    status.update(label="❌ Fehler: Konnte KI nicht erreichen.", state="error")


# --- 5. VISUELLE WERKZEUGE (Nur anzeigen, wenn es eine aktuelle Analyse gibt) ---
if st.session_state.ai_answer:
    st.markdown("---")
    st.markdown("### 🎨 INNOVA Visualisierungs-Werkzeuge")
    
    col1, col2 = st.columns(2)
    
    # --- LINKE SPALTE: BILDGENERIERUNG (REPARIERT) ---
    with col1:
        st.markdown("**🖼️ Konzept-Skizze**")
        st.caption("Erstellt eine technische Blueprint-Zeichnung deines Produkts.")
        if st.button("📦 Technischen Blueprint generieren", use_container_width=True):
            with st.spinner("Zeichne Blueprint..."):
                try:
                    # REPARIERTER PROMPT: Zeichnet das Produkt, nicht Leonardo Da Vinci!
                    bild_prompt = f"Technical engineering patent blueprint drawing of {st.session_state.current_question}, highly detailed schematic, vintage sepia style, no text"
                    encoded_prompt = urllib.parse.quote(bild_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"
                    
                    st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 10px; border: 2px solid #ccc;">', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Bild konnte nicht geladen werden.")
                
    # --- RECHTE SPALTE: DIAGRAMME ---
    with col2:
        st.markdown("**🧩 Architektur & Prozess**")
        st.caption("Generiert Code für Mindmaps oder Flussdiagramme.")
        diagramm_typ = st.radio("Typ:", ["Mindmap (Struktur)", "Flussdiagramm (Prozess)"], horizontal=True)
        
        if st.button("Diagramm zeichnen", use_container_width=True):
            with st.spinner(f"Erstelle {diagramm_typ}..."):
                if "Mindmap" in diagramm_typ:
                    graph_prompt = f"Graphviz DOT code ONLY for a simple mindmap about: {st.session_state.current_question}. Format: digraph G {{ ... }}. Max 10 nodes. No explanation."
                else:
                    graph_prompt = f"Graphviz DOT code ONLY for a very simple flowchart about developing: {st.session_state.current_question}. Format: digraph G {{ ... }}. Max 6 steps. No explanation."
                
                dot_code = gemini_api.generiere_innova_antwort(graph_prompt)
                
                if "```" in dot_code:
                    try:
                        dot_code = dot_code.split("```")[1]
                        if dot_code.startswith("dot"):
                            dot_code = dot_code[3:]
                    except:
                        pass
                
                st.graphviz_chart(dot_code)
                
                # --- DOWNLOAD FÜR DAS DIAGRAMM ---
                st.download_button(
                    label="📥 Diagramm-Code (DOT) speichern",
                    data=dot_code,
                    file_name="innova_architektur.dot",
                    mime="text/plain",
                    help="Diesen Code kannst du auf Seiten wie 'Graphviz Online' jederzeit wieder in ein Bild verwandeln."
                )
                except Exception as e:
                    st.error("Die KI hat leider einen ungültigen Diagramm-Code erzeugt. Bitte versuche es noch einmal.")
