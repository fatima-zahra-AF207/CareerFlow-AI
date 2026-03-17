import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- MOROCCAN LOCALIZATION ---
def get_moroccan_cities():
    return ["Casablanca", "Rabat", "Tanger", "Marrakech", "Fès", "Agadir", "Kenitra", "Oujda", "Tétouan", "Salé"]

def get_moroccan_salary_benchmark(ville, experience, secteur):
    # Benchmark réaliste pour le Maroc
    base_salaries = {
        "Développeur junior": (6000, 10000),
        "Développeur confirmé": (12000, 18000),
        "Senior/Lead": (20000, 30000),
        "Data Scientist": (15000, 25000),
        "Chef de projet": (18000, 28000),
        "Manager": (25000, 40000)
    }
    
    min_s, max_s = base_salaries.get(experience, (8000, 15000))
    
    # City adjustment
    if ville == "Casablanca":
        adj = 1.2
    elif ville == "Rabat":
        adj = 1.1
    else:
        adj = 0.9
        
    return int(min_s * adj), int(max_s * adj)

def convert_to_mad(amount, currency="EUR"):
    rates = {"EUR": 10.8, "USD": 10.1, "GBP": 12.8}
    return int(amount * rates.get(currency, 1.0))

def detect_moroccan_degree(text):
    degrees = ["Bac+2", "Bac+3", "Bac+5", "Bac+8", "Ingénieur", "Master", "Doctorat", "Licence", "DUT", "BTS", "DTS"]
    found = [d for d in degrees if d.lower() in text.lower()]
    return found

def scrape_indeed_marocco(keyword="développeur"):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://ma.indeed.com/jobs?q={encoded_keyword}&l=Maroc"
    return [
        {"title": f"Recherche Live: {keyword}", "company": "Indeed", "city": "Maroc", "salary": "Voir sur Indeed", "url": url}
    ]

def scrape_linkedin_morocco(keyword="développeur"):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}&location=Maroc"
    return [
        {"title": f"Recherche Live: {keyword}", "company": "LinkedIn", "city": "Partout au Maroc", "salary": "Voir sur LinkedIn", "url": url}
    ]

def scrape_rekrute_ma(keyword="développeur"):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.rekrute.com/recherche-offres-emploi-maroc.html?keyword={encoded_keyword}"
    return [
        {"title": f"Recherche Live: {keyword}", "company": "ReKrute", "city": "Maroc", "salary": "Voir sur ReKrute", "url": url}
    ]

def scrape_emploi_ma(keyword="développeur"):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.emploi.ma/recherche-travail-maroc?keyword={encoded_keyword}"
    return [
        {"title": f"Recherche Live: {keyword}", "company": "Emploi.ma", "city": "Maroc", "salary": "Voir sur Emploi.ma", "url": url}
    ]

def generate_moroccan_cover_letter(user_data, company, job_desc, lang="Français"):
    skills_list = ", ".join(list(user_data['skills'].keys())[:4])
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    if lang == "Français":
        return f"""
{user_data['name']}
{user_data.get('city', 'Maroc')}
Le {date_str}

À l'attention du Responsable du Recrutement
{company}

Objet : Candidature pour le poste de {user_data.get('career_path', 'Consultant')}

Madame, Monsieur,

C’est avec un grand intérêt que j’ai pris connaissance de votre offre pour le poste de {user_data.get('career_path', 'Consultant')} au sein de {company}. Fort de mes compétences en {skills_list}, je suis convaincu que mon profil correspond aux exigences de votre projet.

Ayant évolué dans le secteur technologique au Maroc, j'ai développé une solide expertise en {user_data.get('career_path', 'informatique')}. Ma maîtrise de {skills_list} me permet d'aborder avec confiance les défis techniques de votre entreprise.

Intégrer une structure comme {company} représente pour moi une opportunité de contribuer au développement de solutions innovantes à l'échelle nationale. Ma rigueur et mon esprit d'équipe sont des atouts que je souhaite mettre à votre disposition.

Je reste à votre entière disposition pour un entretien afin de vous exposer plus en détail mes motivations.

Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

Cordialement,
{user_data['name']}
        """.strip()
    else:
        return f"""
{user_data['name']}
{user_data.get('city', 'المغرب')}
بتاريخ {date_str}

إلى السيد مسؤول التوظيف
شركة {company}

الموضوع: طلب ترشيح لمنصب {user_data.get('career_path', 'مستشار')}

سيداتي، سادتي،

ببالغ الاهتمام اطلعت على عرضكم بخصوص منصب {user_data.get('career_path', 'مستشار')} في شركة {company}. وبفضل مهاراتي في {skills_list}، أنا على يقين من أن ملفي الشخصي يتوافق مع متطلبات مشروعكم.

من خلال مساري المهني في القطاع التكنولوجي بالمغرب، اكتسبت خبرة متينة في {user_data.get('career_path', 'المعلوميات')}. تمكني من {skills_list} يتيح لي مواجهة التحديات التقنية لشركتكم بكل ثقة.

إن الانضمام إلى مؤسسة مثل {company} يمثل لي فرصة للمساهمة في تطوير حلول مبتكرة على المستوى الوطني. إن جديتي وروح الفريق لدي هي أصول أرغب في وضعها رهن إشارتكم.

أبقى رهن إشارتكم لإجراء مقابلة قصد عرض دوافعي بمزيد من التفصيل.

في انتظار ردكم، تقبلوا فائق التقدير والاحترام.

مع خالص التحيات،
{user_data['name']}
        """.strip()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CareerFlow AI - Morocco",
    page_icon="🇲🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6C5CE7 0%, #a29bfe 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown p {
        color: white !important;
    }

    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid #6C5CE7;
    }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6C5CE7 0%, #00B894 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
        opacity: 0.9;
    }

    /* Badges */
    .skill-badge {
        display: inline-block;
        padding: 5px 12px;
        background: #e0e0ff;
        color: #6C5CE7;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }

    /* Progress Bar */
    .custom-progress-container {
        width: 100%;
        background-color: #eee;
        border-radius: 10px;
        margin: 10px 0;
    }

    .custom-progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #6C5CE7, #00B894);
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }

    /* Keyframe Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeIn 0.8s ease-out forwards;
    }

    /* Sidebar Radio Styling */
    div[data-testid="stSidebarNav"] {
        background-color: transparent !important;
    }
    
    .stRadio [role="radiogroup"] {
        gap: 10px;
    }
    
    .stRadio label {
        background: rgba(255,255,255,0.1);
        padding: 10px 20px;
        border-radius: 10px;
        color: white !important;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .stRadio label:hover {
        background: rgba(255,255,255,0.2);
    }

    </style>
    """, unsafe_allow_html=True)

local_css()

# --- SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': 'Anas El Amrani',
        'skills': {'Python': 85, 'React': 70, 'Laravel': 80, 'SQL': 75, 'Français': 95, 'Arabe': 100, 'Anglais': 75},
        'career_path': 'Ingénieur Logiciel Sénior',
        'applications': [
            {'company': 'OCP Group', 'position': 'Data Engineer', 'status': 'Entretien', 'date': '10/03/2024'},
            {'company': 'Attijariwafa Bank', 'position': 'Backend Dev', 'status': 'Appliqué', 'date': '12/03/2024'},
            {'company': 'DXC Technology', 'position': 'Fullstack Dev', 'status': 'Refusé', 'date': '05/03/2024'}
        ],
        'ats_score': 82,
        'show_path_details': False,
        'city': 'Casablanca'
    }

# Translation Dict
t = {
    "Français": {
        "title": "CareerFlow AI",
        "subtitle": "Votre copilote carrière intelligent au Maroc",
        "nav_profile": "👤 Profil & Diagnostic",
        "nav_optim": "🎯 Optimisation",
        "nav_tracking": "📅 Suivi & Candidatures",
        "nav_stats": "📈 Statistiques",
        "nav_settings": "⚙️ Paramètres",
        "cv_analysis": "📄 Analyse de CV",
        "ats_score": "Score ATS",
        "market_standards": "Basé sur le marché Marocain",
        "career_pred": "🎯 Prédiction de Carrière",
        "view_path": "Voir le parcours détaillé",
        "radar": "📊 Radar de Compétences",
        "badges": "🏆 Badges Acquis",
        "generate_ia": "Générer avec l'IA",
        "rec_jobs": "Offres recommandées pour vous",
        "salary_est": "Estimation : ",
        "match": "Match",
        "interview_sim": "🎙️ Simulateur d'Entretien",
        "analyze_resp": "Analyser ma réponse",
        "save_mods": "Sauvegarder les modifications",
        "lang_interface": "Langue de l'interface",
        "currency": "DH",
        "job_fairs": "📅 Salons & Événements au Maroc",
        "days_left": "jours restants",
        "register": "S'inscrire",
        "career_tips": "💡 Conseils Stratégiques",
        "timeline": "🕒 Suivi des Candidatures"
    },
    "العربية": {
        "title": "CareerFlow AI",
        "subtitle": "مساعدك الذكي لمسارك المهني في المغرب",
        "nav_profile": "👤 الملف الشخصي والتشخيص",
        "nav_optim": "🎯 التحسين والإستراتيجية",
        "nav_tracking": "📅 التتبع والترشيحات",
        "nav_stats": "📈 الإحصائيات العامة",
        "nav_settings": "⚙️ الإعدادات",
        "cv_analysis": "📄 تحليل السيرة الذاتية",
        "ats_score": "نقطة ATS",
        "market_standards": "بناءً على معايير السوق المغربي",
        "career_pred": "🎯 التنبؤ بالمسار المهني",
        "view_path": "عرض المسار المفصل",
        "radar": "📊 رادار المهارات",
        "badges": "🏆 الشارات المكتسبة",
        "generate_ia": "إنشاء بواسطة الذكاء الاصطناعي",
        "rec_jobs": "الوظائف المقترحة لك",
        "salary_est": "الراتب المتوقع: ",
        "match": "مطابقة",
        "interview_sim": "🎙️ محاكي المقابلات",
        "analyze_resp": "تحليل إجابتي",
        "save_mods": "حفظ التغييرات",
        "lang_interface": "لغة الواجهة",
        "currency": "درهم",
        "job_fairs": "📅 المعارض والفعاليات في المغرب",
        "days_left": "أيام متبقية",
        "register": "تسجيل",
        "career_tips": "💡 نصائح إستراتيجية",
        "timeline": "🕒 تتبع الترشيحات"
    }
}
L = t[st.session_state.lang]

# RTL Support CSS
if st.session_state.lang == "العربية":
    st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    .stSidebar { direction: ltr; text-align: left; }
    div[data-testid="stSidebarNav"] { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTS ---
def card(title, content, subtext=""):
    st.markdown(f"""
    <div class="metric-card animate-in">
        <h3 style="color: #6C5CE7; margin-top: 0;">{title}</h3>
        <div style="font-size: 1.8rem; font-weight: 800; color: #2d3436;">{content}</div>
        <p style="color: #636e72; font-size: 0.9rem;">{subtext}</p>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(label, value):
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between;">
            <span style="font-weight: 600;">{label}</span>
            <span>{value}%</span>
        </div>
        <div class="custom-progress-container">
            <div class="custom-progress-bar" style="width: {value}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MODULES ---

def module_profile():
    st.markdown(f"<h1 style='color: #6C5CE7;'>{L['nav_profile']}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown(f"### {L['cv_analysis']}")
        uploaded_file = st.file_uploader("Importez votre CV (PDF, DOCX) - Standard Marocain", type=['pdf', 'docx'])
        if uploaded_file:
            with st.spinner('Analyse par l\'IA...'):
                time.sleep(1)
                # Simulation de détection de diplôme marocain
                degrees = detect_moroccan_degree(uploaded_file.name + " Ingénieur d'état ENSIAS") 
            st.success("CV Analysé avec succès !")
            if degrees:
                st.info(f"🎓 Diplôme(s) détecté(s) : {', '.join(degrees)}")
            card(L['ats_score'], f"{st.session_state.user_data['ats_score']}%", L['market_standards'])
        else:
            card(L['cv_analysis'], "Prêt", "Importez un CV pour commencer")
            
        st.markdown(f"### {L['career_pred']}")
        st.info(f"Prochaine étape : **{st.session_state.user_data['career_path']}**")
        if st.button(L['view_path']):
            st.session_state.user_data['show_path_details'] = not st.session_state.user_data['show_path_details']
        
        if st.session_state.user_data.get('show_path_details'):
            st.markdown(f"""
            <div class="metric-card animate-in" style="border-left: 5px solid #00B894;">
                <h4 style="color: #00B894;">Parcours au Maroc :</h4>
                <ul style="color: #2d3436; font-size: 0.9rem;">
                    <li><b>Trimestre 1:</b> Certification Cloud (AWS/Azure)</li>
                    <li><b>Trimestre 2:</b> Formation Management (ENCG)</li>
                    <li><b>Trimestre 3:</b> Projet d'envergure nationale (OCP/Wafa)</li>
                    <li><b>Trimestre 4:</b> Transition vers Lead Tech</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"### {L['radar']}")
        skills = st.session_state.user_data['skills']
        df_skills = pd.DataFrame(dict(r=list(skills.values()), theta=list(skills.keys())))
        
        fig = px.line_polar(df_skills, r='r', theta='theta', line_close=True, range_r=[0,100])
        fig.update_traces(fill='toself', line_color='#6C5CE7')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"### {L['badges']}")
        badges_container = ""
        for s in skills.keys():
            badges_container += f'<span class="skill-badge">{s}</span>'
        st.markdown(badges_container, unsafe_allow_html=True)

def module_optimisation():
    st.markdown(f"<h1 style='color: #6C5CE7;'>{L['nav_optim']}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✍️ Lettre de Motivation", "🔍 Matching d'Offres"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            target_company = st.text_input("Entreprise cible (ex: OCP, CDG, Bank Al-Maghrib)", value="OCP Group")
            target_desc = st.text_area("Description de l'offre (Optionnel)")
            if st.button(L['generate_ia']):
                st.session_state.temp_letter = generate_moroccan_cover_letter(
                    st.session_state.user_data, 
                    target_company, 
                    target_desc, 
                    st.session_state.lang
                )
        
        with col2:
            if 'temp_letter' in st.session_state:
                st.markdown("""<div class="metric-card">""" + st.session_state.temp_letter + "</div>", unsafe_allow_html=True)
                st.download_button("Télécharger (.txt)", st.session_state.temp_letter)

    with tab2:
        st.markdown(f"### {L['rec_jobs']}")
        
        search_query = st.text_input("Mots-clés pour la recherche (ex: Python, React, Stage)", value="développeur")
        
        sites = {
            "LinkedIn Maroc": scrape_linkedin_morocco(search_query),
            "Indeed Maroc": scrape_indeed_marocco(search_query),
            "ReKrute.ma": scrape_rekrute_ma(search_query),
            "Emploi.ma": scrape_emploi_ma(search_query)
        }
        
        for site, jobs in sites.items():
            with st.expander(f"Offres de {site} ({len(jobs)})"):
                for job in jobs:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 800; font-size: 1.1rem;">{job['title']}</span>
                            <span style="color: #00B894; font-weight: 700;">{job.get('match', '90%')} {L['match']}</span>
                        </div>
                        <p style="margin-top: 5px; color: #6C5CE7; font-weight: 600;">{job['company']} - {job['city']}</p>
                        <p style="color: #636e72;">{L['salary_est']} {job['salary']}</p>
                        <a href="{job['url']}" target="_blank" style="text-decoration: none;">
                            <button style="background: #6C5CE7; color: white; border: none; padding: 8px 15px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: 600;">
                                Voir l'offre ↗
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
def module_suivi():
    st.markdown(f"<h1 style='color: #6C5CE7;'>{L['nav_tracking']}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1.2])
    
    with col1:
        st.markdown(f"### {L['timeline']}")
        df = pd.DataFrame(st.session_state.user_data['applications'])
        st.table(df)
        
        st.markdown(f"### {L['job_fairs']}")
        salons = [
            {"Event": "Forum EHTP-Entreprises", "Date": "15 Mai 2024", "Lieu": "Casablanca", "Progress": 65},
            {"Event": "Forum de l'EMI", "Date": "10 Juin 2024", "Lieu": "Rabat", "Progress": 40},
            {"Event": "Salon AMGE-Caravane", "Date": "22 Avril 2024", "Lieu": "Casablanca", "Progress": 85}
        ]
        
        for salon in salons:
            with st.container():
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 10px; padding: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: 800; font-size: 1.1rem; color: #6C5CE7;">{salon['Event']}</span><br>
                            <span style="color: #636e72; font-size: 0.9rem;">📍 {salon['Lieu']} | 📅 {salon['Date']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-weight: 700; color: #00B894;">{100 - salon['Progress']} {L['days_left']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                progress_bar("Préparation", salon['Progress'])

    with col2:
        st.markdown(f"### {L['career_tips']}")
        with st.expander(L['career_tips'], expanded=True):
            st.markdown(f"""
            1. **Langues** : Le français est indispensable. L'arabe est un fort atout.
            2. **Réseautage** : LinkedIn Maroc est incontournable.
            3. **CV** : Préférez le format chronologique.
            4. **Sites** : ReKrute.ma, Emploi.ma, LinkedIn.
            """)
            
        st.markdown(f"### {L['interview_sim']}")
        st.markdown(f"""
        <div class="metric-card">
            <h4>Question :</h4>
            <p><i>"Parlez-nous de votre expérience avec les technologies ERP au Maroc (Odoo/SAP) ?"</i></p>
        </div>
        """, unsafe_allow_html=True)
        st.text_area("Votre réponse", key="interview_resp")
        if st.button(L['analyze_resp']):
            st.info("🔄 Analyse en cours... Mettez en avant vos projets nationaux.")

def module_stats():
    st.markdown(f"<h1 style='color: #6C5CE7;'>{L['nav_stats']}</h1>", unsafe_allow_html=True)
    
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        card("Total Candidatures", "28", "+4 cette semaine")
    with row1_col2:
        card("Taux de Réponse", "42%", "Top 10% des profils")
    with row1_col3:
        card("Offres Reçues", "3", "Secteur Tech Maroc")
        
    st.markdown(f"### 💵 Benchmark Salaires ({L['currency']}/mois)")
    
    city = st.session_state.user_data.get('city', 'Casablanca')
    min_s, max_s = get_moroccan_salary_benchmark(city, "Senior/Lead", "IT")
    
    salary_data = pd.DataFrame({
        "Niveau": ["Junior", "Confirmé", "Senior", "Manager"],
        "Moyenne": [8000, 15000, 25000, 35000],
        "Votre Marché": [8000*1.1, 15000*1.1, 25000*1.1, 35000*1.1] # Simulé pour ville
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=salary_data["Niveau"], y=salary_data["Moyenne"], name="Moyenne Nationale", marker_color="#a29bfe"))
    fig.add_trace(go.Bar(x=salary_data["Niveau"], y=salary_data["Votre Marché"], name=f"Marché {city}", marker_color="#6C5CE7"))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🌍 Comparatif par Ville (+/- % vs Moyenne)")
    cities_comp = pd.DataFrame({
        "Ville": ["Casablanca", "Rabat", "Tanger", "Marrakech", "Autres"],
        "Ajustement": [20, 10, 0, -5, -10]
    })
    fig2 = px.bar(cities_comp, x="Ville", y="Ajustement", color="Ajustement", color_continuous_scale="Viridis")
    st.plotly_chart(fig2, use_container_width=True)

def module_settings():
    st.markdown(f"<h1 style='color: #6C5CE7;'>{L['nav_settings']}</h1>", unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.text_input("Nom complet", value=st.session_state.user_data['name'])
    st.text_input("Email", value="anas.elamrani@careerflow.ma")
    
    st.selectbox(L['lang_interface'], ["Français", "العربية"], key="lang_selector", 
                 index=0 if st.session_state.lang == "Français" else 1)
    
    if st.session_state.lang_selector != st.session_state.lang:
        st.session_state.lang = st.session_state.lang_selector
        st.rerun()

    st.selectbox("Ville de résidence", get_moroccan_cities(), index=0)
    st.checkbox("Notifications par Email", value=True)
    if st.button(L['save_mods']):
        st.success("Profil mis à jour !")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align: center; color: white;'>{L['title']} 🇲🇦</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{L['subtitle']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = {
        L["nav_profile"]: module_profile,
        L["nav_optim"]: module_optimisation,
        L["nav_tracking"]: module_suivi,
        L["nav_stats"]: module_stats,
        L["nav_settings"]: module_settings
    }
    
    choice = st.radio("Navigation", list(menu.keys()))
    
    st.sidebar.markdown(f"""
    <div style="position: fixed; bottom: 20px; left: 20px; color: rgba(255,255,255,0.6); font-size: 0.8rem;">
        Version 2.1.0 (Morocco)<br>
        Power by CareerFlow IA Morocco
    </div>
    """, unsafe_allow_html=True)

# --- RENDER CHOICE ---
menu[choice]()
