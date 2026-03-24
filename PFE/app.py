# Main app.py file

import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from modules.cv_analyzer import CVAnalyzer
from modules.job_matcher import JobMatcher
from modules.tracking import ApplicationTracker
from modules.interview_coach import InterviewCoach
from modules.salary_benchmark import SalaryBenchmark
from modules.auth import AuthManager
from utils.helpers import setup_sidebar

# Page configuration
st.set_page_config(
    page_title="ForsaFlow AI - Votre copilote carrière au Maroc",
    page_icon="🇲🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Custom styles */
    .main-header {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .status-applied { background-color: #FFD966; color: #2C3E50; }
    .status-interview { background-color: #90BE6D; color: white; }
    .status-offer { background-color: #4CAF50; color: white; }
    .status-rejected { background-color: #F4A261; color: white; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Initialize modules
    auth = AuthManager()
    cv_analyzer = CVAnalyzer()
    job_matcher = JobMatcher()
    tracker = ApplicationTracker()
    coach = InterviewCoach()
    salary = SalaryBenchmark()
    
    # Check authentication
    if not auth.is_logged_in():
        auth.render_login()
        return
    
    # Setup sidebar navigation
    selected = setup_sidebar()
    
    # Render user info and logout in sidebar
    auth.render_user_menu()
    
    # Render selected page
    if selected == "🏠 Profil & Diagnostic":
        render_profile_page(cv_analyzer)
    elif selected == "✨ Optimisation":
        render_optimization_page(cv_analyzer)
    elif selected == "📊 Suivi & Candidatures":
        tracker.render_tracking()
    elif selected == "📈 Statistiques":
        render_statistics_page(tracker, salary)
    elif selected == "🤖 Coach IA":
        coach.render()
    elif selected == "⚙️ Paramètres":
        render_settings_page(auth)

def render_profile_page(cv_analyzer):
    """Render profile and diagnostic page"""
    
    st.markdown('<div class="main-header"><h1>🇲🇦 Profil & Diagnostic</h1><p>ForsaFlow AI - فُرصتك لمسيرة مهنية ناجحة | Votre opportunité pour une carrière réussie 🚀</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Analyse de CV")
        uploaded_file = st.file_uploader(
            "Importez votre CV (PDF, DOCX, Image)",
            type=['pdf', 'docx', 'png', 'jpg', 'jpeg'],
            help="Formats supportés: PDF, DOCX, PNG, JPG (limite 200MB)"
        )
        
        if uploaded_file is not None:
            # Afficher les informations du fichier
            st.success(f"✅ Fichier chargé : **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            
            # Message d'astuce pour les PDF
            if uploaded_file.type == "application/pdf":
                st.info("💡 **Astuce** : Si l'analyse ne détecte aucune compétence, essayez d'ouvrir votre CV dans un navigateur et de l'utiliser 'Enregistrer sous...' pour générer un PDF standard.")
            
            # Gérer l'analyse avec le session_state pour éviter les rechargements inutiles
            if 'cv_analysis' not in st.session_state or st.session_state.get('current_cv_name') != uploaded_file.name:
                if st.button("🔍 Lancer l'Analyse du CV"):
                    with st.spinner("🔍 Analyse de votre CV en cours..."):
                        try:
                            analysis = cv_analyzer.analyze(uploaded_file)
                            st.session_state.cv_analysis = analysis
                            st.session_state.current_cv_name = uploaded_file.name
                            try:
                                st.rerun()
                            except AttributeError:
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de l'analyse : {str(e)}")
            
            # Afficher les résultats si l'analyse existe pour ce fichier
            if 'cv_analysis' in st.session_state and st.session_state.get('current_cv_name') == uploaded_file.name:
                analysis = st.session_state.cv_analysis
                
                # Display ATS Score
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Score ATS</h3>
                    <h1 style="color: #FF6B35;">{analysis['ats_score']}%</h1>
                    <p>Basé sur le marché Marocain</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display skills
                st.subheader("💪 Compétences détectées")
                if analysis['skills']:
                    for skill, score in analysis['skills'].items():
                        st.write(f"**{skill}**")
                        st.progress(score/100)
                else:
                    st.info("Aucune compétence détectée. Vérifiez le format de votre CV.")
                
                # Display suggestions
                st.subheader("💡 Suggestions d'amélioration")
                for suggestion in analysis['suggestions']:
                    st.warning(suggestion)
    
    with col2:
        st.subheader("📊 Radar de Compétences")
        
        if 'analysis' in locals() and analysis['skills']:
            categories = list(analysis['skills'].keys())[:8]  # Limit to 8 skills
            values = list(analysis['skills'].values())[:8]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                marker=dict(color='#FF6B35', size=8),
                line=dict(color='#FF6B35', width=2)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100]),
                    angularaxis=dict(tickfont=dict(size=10))
                ),
                showlegend=False,
                height=400,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Importez votre CV pour voir votre radar de compétences")
        
        # Career prediction
        st.subheader("🔮 Prédiction de Carrière")
        
        career_goal = st.radio(
            "Votre objectif actuel :",
            ["Entrer sur le marché du travail 💼", "Poursuivre les études 🎓"],
            horizontal=False
        )
        
        if career_goal == "Entrer sur le marché du travail 💼":
            st.markdown(f"""
            **Prochaine étape :** Ingénieur Logiciel / Développeur Senior
            
            **Suggestions de parcours :**
            - 📈 Développez vos compétences en architecture cloud (AWS, Azure)
            - 🇲🇦 Ciblez les grandes entreprises au Maroc (OCP, Attijari, Technopolis)
            - 🌍 Participez à des meetups tech pour le réseautage
            
            **Skills à renforcer :** Architecture de Microservices, CI/CD, Management d'équipe.
            """)
        else:
            st.markdown("""
            **Parcours académique suggéré :**
            - 🎓 Master spécialisé ou Cycle d'Ingénieur (Ex: ENSIAS, EMI, UM6P)
            - 📜 MBA pour une transition vers le management technique
            - 🌍 Formations certifiantes en IA ou Cybersécurité
            
            **Conseil :** Choisissez un parcours qui complète vos compétences techniques actuelles avec une vision stratégique ou une spécialisation de niche.
            """)

def render_optimization_page(cv_analyzer):
    """Render CV optimization page"""
    
    st.markdown('<div class="main-header"><h1>✨ Optimisation CV</h1><p>Optimisez votre CV pour le marché marocain</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Entreprise cible")
        company = st.text_input("Nom de l'entreprise", placeholder="Ex: OCP Group, CDG, Attijariwafa Bank")
        
        st.subheader("📝 Description de l'offre")
        job_description = st.text_area("Collez la description de l'offre ici", height=150)
        
        if st.button("🤖 Générer avec l'IA"):
            with st.spinner("Génération en cours..."):
                st.success("CV optimisé généré!")
                st.markdown("""
                ### CV Optimisé
                
                **Résumé professionnel:**
                Ingénieur logiciel avec 3 ans d'expérience, spécialisé dans le développement full stack. Passionné par les nouvelles technologies et le marché marocain.
                
                **Compétences clés:**
                - Python, React, Laravel
                - SQL, MongoDB
                - Docker, Git
                
                **Expériences pertinentes:**
                - Stage chez [Entreprise] : Développement d'une application full stack
                - Projet académique : Création d'une plateforme e-commerce
                """)
    
    with col2:
        st.subheader("📊 Score ATS actuel")
        st.metric("Score", "82%", "+12% après optimisation")
        st.progress(0.82)
        
        st.subheader("🔑 Mots-clés recommandés")
        keywords = ["Python", "React", "SQL", "Docker", "AWS", "Agile", "Français", "Anglais"]
        for kw in keywords:
            st.markdown(f"- {kw}")

def render_statistics_page(tracker, salary):
    """Render statistics page"""
    
    st.markdown('<div class="main-header"><h1>📈 Statistiques</h1><p>Suivez vos performances et comparez-vous au marché</p></div>', unsafe_allow_html=True)
    
    # Get applications data
    df = tracker.get_applications()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Candidatures", len(df), "+4 cette semaine")
    with col2:
        interviews = len(df[df['status'].str.contains("Entretien", na=False)]) if not df.empty else 0
        response_rate = (interviews / len(df) * 100) if len(df) > 0 else 0
        st.metric("Taux de Réponse", f"{response_rate:.0f}%", "Top 10% des profils")
    with col3:
        offers = len(df[df['status'] == "Offre reçue"]) if not df.empty else 0
        st.metric("Offres Reçues", offers, "Secteur Tech Maroc")
    
    # Salary benchmark
    salary.render()
    
    # Application timeline
    if not df.empty:
        st.subheader("📅 Évolution des candidatures")
        df['date'] = pd.to_datetime(df['date'])
        timeline = df.groupby(df['date'].dt.date).size().reset_index(name='count')
        
        fig = px.line(timeline, x='date', y='count', title="Candidatures par jour")
        st.plotly_chart(fig, use_container_width=True)

def render_settings_page(auth):
    """Render settings page"""
    
    st.markdown('<div class="main-header"><h1>⚙️ Paramètres</h1><p>Gérez votre compte et vos préférences</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Informations personnelles")
        
        name = st.text_input("Nom complet", value=st.session_state.get('user_name', ''))
        email = st.text_input("Email", value=st.session_state.get('user_email', ''))
        city = st.selectbox("Ville de résidence", 
                           ["Casablanca", "Rabat", "Tanger", "Marrakech", "Fès"],
                           index=0)
        
        if st.button("💾 Sauvegarder les modifications"):
            st.success("Profil mis à jour!")
    
    with col2:
        st.subheader("🔔 Notifications")
        email_notif = st.checkbox("Notifications par email", value=True)
        job_alerts = st.checkbox("Alertes nouvelles offres", value=True)
        event_reminders = st.checkbox("Rappels événements", value=True)

if __name__ == "__main__":
    main()
