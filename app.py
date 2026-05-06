import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. UNIQUE CONFIGURATION (DOIT ÊTRE EN HAUT)
st.set_page_config(
    page_title="IA Portfolio Assistant", 
    page_icon="💼", 
    initial_sidebar_state="collapsed"
)

# 2. MASQUER LE MENU ET STYLE PERSONNALISÉ
st.markdown("""
    <style>
    /* Masquer le menu Streamlit pour la confidentialité */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    .stApp { max-width: 800px; margin: 0 auto; }
    .version-frame {
        padding: 10px;
        border: 2px solid #0047AB; /* Bleu Cobalt */
        border-radius: 8px;
        background-color: rgba(0, 71, 171, 0.05);
        text-align: center;
        margin-bottom: 25px;
        color: #0047AB;
        font-size: 0.9em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Connexion à Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Clé API manquante dans les Secrets Streamlit !")

# --- LOGIQUE D'EXTRACTION ---
@st.cache_data
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

# 1. Message encadré bleu
st.markdown("""
    <div class="version-frame">
        This is version 1.0; I’d love to hear your feedback.
    </div>
    """, unsafe_allow_html=True)

# Correction des guillemets ici : utilisation de simples ' autour de Rate Limit
st.caption("⚠️ **Notice:** This assistant uses a free API with daily limits. If you encounter any issues with 'Rate Limit', please feel free to return and continue our conversation tomorrow!")

st.divider()

# 2. Greeting Message (Titre sans ancre URL)
st.title("🤖 Hi, I'm Hanh's AI assistant!", anchor=False)
st.markdown("""
Feel free to ask me anything about her experiences, compétences, and more. 

*However, I would recommend giving her a call for a personalized exchange!*
""")
st.divider()

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 3. Chat Input
if prompt := st.chat_input("Type your question here..."):
    # Affichage immédiat du message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- ÉLÉMENT DE PATIENCE ---
    with st.chat_message("assistant"):
        # Le spinner s'affiche ici et disparaît dès que le bloc "with" est terminé
        with st.spinner("Hanh's assistant is thinking..."):
            
            # Appel au modèle Gemini
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            full_prompt = f"""
            Tu es l'assistant IA de Hanh. Utilise les infos dans le fichier faq.pdf pour répondre au recruteur.
            La réponse doit etre professionnelle, synthétisée, fidèle aux données fournies et valorisante. Si tu ne sais pas, ne pas inventer la réponse et invite-le à contacter Hanh directement.
            
            CONTEXTE :
            {context_text}
            
            QUESTION DU RECRUTEUR :
            {prompt}
            """
            
            try:
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                # On ajoute la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Désolé, une erreur est survenue : {e}")


