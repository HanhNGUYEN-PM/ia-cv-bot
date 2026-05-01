import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuration de la page
st.set_page_config(page_title="IA Portfolio Assistant", page_icon="💼")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

# Connexion à Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Clé API manquante dans les Secrets Streamlit !")

# --- LOGIQUE D'EXTRACTION ---
def get_docs_text(files):
    text = ""
    for file in files:
        try:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            st.error(f"Erreur lecture {file}: {e}")
    return text

# Chargement du contexte (CV + FAQ)
context_text = get_docs_text(["cv.pdf", "faq.pdf"])

# --- INTERFACE CHAT ---
st.title("🤖 Discutez avec mon profil")
st.info("Posez des questions sur mes compétences, mes projets ou mes motivations.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Quelles sont ses compétences en Python ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Appel au modèle Gemini 1.5 Flash (Gratuit et rapide)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    full_prompt = f"""
    Tu es l'assistant IA de ce candidat. Utilise les infos ci-dessous pour répondre au recruteur.
    Sois pro, concis et valorisant. Si tu ne sais pas, invite-le à contacter le candidat.
    
    CONTEXTE :
    {context_text}
    
    QUESTION DU RECRUTEUR :
    {prompt}
    """
    
    response = model.generate_content(full_prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})