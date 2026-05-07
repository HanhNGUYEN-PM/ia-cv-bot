import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. UNIQUE CONFIGURATION
st.set_page_config(
    page_title="IA Portfolio Assistant", 
    page_icon="💼", 
    initial_sidebar_state="collapsed"
)

# 2. STYLE PERSONNALISÉ & MASQUAGE INTERFACE
st.markdown("""
    <style>
    /* Masquer les éléments de l'interface Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    .stApp { max-width: 800px; margin: 0 auto; }
    .version-frame {
        padding: 10px;
        border: 2px solid #0047AB;
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

st.markdown("""
    <div class="version-frame">
       This is version 1.0; I’d love to hear your feedback..
    </div>
    """, unsafe_allow_html=True)

st.title("🤖 Hi, I'm Hanh's AI assistant!", anchor=False)

st.markdown("""
Feel free to ask me anything about her experiences, compétences, and more. 

*However, I would recommend giving her a call for a personalized exchange!*
""")

st.caption("⚠️ **Notice:** This assistant uses a free API with daily limits. If you encounter any issues with 'Rate Limit', please feel free to return and continue our conversation tomorrow!")

st.divider()

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LOGIQUE DE CHAT ---

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Hanh's assistant is thinking..."):
            
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # INTÉGRATION DE VOTRE POSITIONNEMENT STRATÉGIQUE
            system_instructions = f"""
            You are Hanh's AI assistant. 
            Your role is to help answer interview questions in a way that is natural, credible, confident, structured, and impact-driven.

            MY POSITIONING:
            - Project & Product Manager with 10+ years of experience (Industry & SaaS).
            - Versatile for roles in Project Management, Product (PM/PO), Delivery, Operations, and Transformation.
            - Differentiator: Effective in complexity, fast-changing environments, and operational optimization.
            - Strengths: Bringing clarity to complexity, simplifying execution, and aligning teams.
            - Tone: Pragmatic, collaborative, calm, and mature. Avoid arrogance or buzzword-heavy speech.

            INFORMATION CONTEXT (Use this to answer):
            {context_text}

            ANSWERING RULES:
            1. Answer in the SAME LANGUAGE as the question.
            2. Be concise but insightful (Interview-ready).
            3. Use concrete examples from the provided context.
            4. Balance project management, product thinking, and customer impact.
            5. For failures: show ownership and learning. 
            6. For conflicts: remain diplomatic and factual.
            7. Format: Polished, executive tone, medium length. No bullet points unless necessary.
            """

            full_prompt = f"{system_instructions}\n\nRECRUITER QUESTION: {prompt}"
            
            try:
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"An error occurred: {e}")
