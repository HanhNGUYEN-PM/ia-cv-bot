import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuration de la page
st.set_page_config(page_title="IA Portfolio Assistant", page_icon="💼")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .version-frame {
        padding: 10px;
        border: 1px solid #ff4b4b;
        border-radius: 5px;
        background-color: rgba(255, 75, 75, 0.1);
        text-align: center;
        margin-bottom: 20px;
        color: #ff4b4b;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# Connexion à Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Clé API manquante dans les Secrets Streamlit !")

# --- LOGIQUE D'EXTRACTION ---
@st.cache_data # Optimisation : ne relit pas les PDF à chaque message
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

context_text = get_docs_text(["cv.pdf", "faq.pdf"])

# --- INTERFACE UI ---

# 1. Framed Message (Version V0)
st.markdown('<div class="version-frame">It\'s the V0 version, please excuse for any occurred problem</div>', unsafe_allow_html=True)

# 2. Greeting Message
st.title("🤖 Discutez avec mon profil")
st.markdown("""
**Hi, I'm Hanh's AI assistant!**  
Feel free to ask me anything about her experiences, compétences, and more. 

*However, I would recommend giving her a call for a personalized exchange!*
""")
st.divider()

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages passés
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Chat Input avec le nouveau texte
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Appel au modèle Gemini 3 Flash Preview (ID vérifié sur votre capture)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    full_prompt = f"""
    Tu es l'assistant IA de Hanh. Utilise les infos ci-dessous pour répondre au recruteur.
    Sois pro, concis et valorisant. Si tu ne sais pas, invite-le à contacter Hanh directement.
    
    CONTEXTE :
    {context_text}
    
    QUESTION DU RECRUTEUR :
    {prompt}
    """
    
    try:
        response = model.generate_content(full_prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Désolé, une erreur est survenue : {e}")
