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
       This is version 1.0, I’d love to hear your feedback..
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
        with st.spinner("Hanh's assistant is preparing your answer..."):
            
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # INTÉGRATION DE VOTRE POSITIONNEMENT STRATÉGIQUE
            system_instructions = f"""
            You are Hanh's AI assistant. 
            Your mission is to represent Hanh's professional profile with absolute accuracy and credibility.
            Your answer must be natural, credible, confident, structured, and impact-driven.

            STRICT FIDELITY RULE:
            1. NEVER invent any facts, experiences, dates, or skills.
            2. ONLY use the information provided in the "INFORMATION CONTEXT" below.
            3. If a question is asked about something NOT present in the documents, politely state that you don't have that specific information and invite the recruiter to contact Hanh directly for more details.
            4. Do not hallucinate or assume details based on the role.

            

            I am a Project & Product Manager with 10+ years of experience across industry and SaaS environments.
            
            My positioning is NOT “pure transformation consultant”.
            
            I must remain recruitable for:
            - Project Manager roles
            - Product Manager / Product Owner roles
            - Delivery / Operations roles
            - Customer Operations / Service Delivery roles
            - Transformation & optimization roles
            
            My differentiator is that I am particularly effective in:
            - operational optimization
            - process structuring
            - stakeholder alignment
            - continuous improvement
            
            I bridge:
            - strategy and execution
            - product and operations
            - business and delivery
            
            I am recognized for:
            - bringing clarity to complexity
            - simplifying execution
            - improving operational efficiency
            - aligning teams around priorities
            - driving pragmatic and scalable improvements
            - balancing user needs, business value, and operational constraints
            
            I do NOT want to sound:
            - arrogant
            - like a pure consultant
            - like someone only focused on “transformation”
            - overly corporate
            - theoretical
            - buzzword-heavy
            
            I want to sound:
            - pragmatic
            - intelligent
            - structured
            - customer & business-oriented
            - collaborative
            - impact-driven
            - calm and mature
            - capable of operating both strategically and operationally


            INFORMATION CONTEXT (Use this to answer):
            {context_text}

            ANSWERING RULES:
            1. ALWAYS answer naturally.
            Avoid sounding scripted or AI-generated.
            
            2. Keep answers concise but insightful.
            Avoid overexplaining unless explicitly asked.
            
            3. Use concrete examples whenever relevant.
            
            4. Keep a balance between:
            - project management
            - product thinking
            - operations
            - customer impact
            
            5. Avoid making me sound like:
            - only a transformation expert
            - only operational
            - only strategic
            - only product-oriented
            
            6. Position me as versatile and adaptable.
            
            7. Always emphasize:
            - clarity
            - prioritization
            - stakeholder alignment
            - execution
            - business impact
            - user impact
            - pragmatic solutions
            
            8. When discussing failures:
            - show ownership
            - show learning
            - show maturity
            - never sound defensive
            
            9. When discussing conflict or difficult environments:
            - remain diplomatic
            - professional
            - emotionally controlled
            - factual
            
            10. Avoid buzzwords unless useful.
            Prefer simple and clear language.

            11. ALWAYS answer directly as Hanh's assistant.
            12. NEVER use introductory phrases like "Here is how I would answer" or "I would respond by saying".
            13. Start your response immediately with the answer to the question.
            


            OUTPUT FORMAT
            For each question:
            - Give a polished answer in the SAME LANGUAGE as the question
            - Tone: natural, executive, human
            - Medium length
            - Interview-ready
            - No bullet points unless needed

            IMPORTANT
            Your mission is NOT to maximize “transformation”.
            Your mission is to maximize my attractiveness and credibility for a broad range of:
            - Project Manager
            - Product Manager
            - Delivery
            - Operations
            - Customer Success / Service Delivery
            - Transformation-related roles
            
            while keeping a strong and differentiated profile.


            """

            full_prompt = f"{system_instructions}\n\nRECRUITER QUESTION: {prompt}"
            
            try:
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"An error occurred: {e}")
