import streamlit as st
try:
    import openai
except ImportError:
    openai = None
from typing import Dict, List
import json

class InterviewCoach:
    """AI-powered interview coach"""
    
    def __init__(self, api_key=None):
        if api_key:
            openai.api_key = api_key
    
    def get_questions(self, job_type: str, question_type: str) -> List[str]:
        """Generate interview questions based on context"""
        
        questions_db = {
            "comportementales": {
                "Stage": [
                    "Parlez-moi de votre parcours académique et de vos motivations pour ce stage.",
                    "Comment gérez-vous les situations de stress ou les délais serrés?",
                    "Décrivez un projet où vous avez travaillé en équipe. Quel était votre rôle?"
                ],
                "Junior": [
                    "Pourquoi avez-vous choisi ce domaine?",
                    "Comment restez-vous à jour avec les nouvelles technologies?",
                    "Décrivez une situation où vous avez dû apprendre une nouvelle technologie rapidement."
                ],
                "Senior": [
                    "Parlez-moi de votre plus grand accomplissement professionnel.",
                    "Comment avez-vous géré un conflit dans votre équipe?",
                    "Quelle est votre approche pour le mentorat des juniors?"
                ]
            },
            "techniques": {
                "Data Engineer": [
                    "Comment optimiseriez-vous une requête SQL lente?",
                    "Quelle est la différence entre un Data Warehouse et un Data Lake?",
                    "Comment garantissez-vous la qualité des données dans un pipeline ETL?"
                ],
                "Développeur": [
                    "Expliquez la différence entre une classe abstraite et une interface.",
                    "Comment gérez-vous la concurrence dans une application?",
                    "Quels sont les principes SOLID et pourquoi sont-ils importants?"
                ]
            },
            "maroc": {
                "général": [
                    "Comment voyez-vous votre carrière au Maroc dans les 5 prochaines années?",
                    "Quelle est votre compréhension du marché technologique marocain?",
                    "Êtes-vous prêt à travailler en équipe multiculturelle?"
                ]
            }
        }
        
        # Determine questions to return
        if question_type == "🇲🇦 Comportementales":
            return questions_db["comportementales"].get(job_type, questions_db["comportementales"]["Junior"])
        elif question_type == "💻 Techniques":
            if "data" in str(job_type).lower():
                return questions_db["techniques"]["Data Engineer"]
            else:
                return questions_db["techniques"]["Développeur"]
        elif question_type == "🌍 Contexte Maroc":
            return questions_db["maroc"]["général"]
        else:
            return ["Parlez-nous de vous."]
    
    def analyze_answer(self, answer: str, question: str) -> Dict:
        """Analyze user answer and provide feedback"""
        
        # Simple heuristics
        answer_length = len(answer.split())
        
        if answer_length < 20:
            score = 4
            feedback = "Votre réponse est trop courte. Développez davantage vos idées."
        elif answer_length < 50:
            score = 6
            feedback = "Bonne base, mais vous pouvez ajouter plus de détails concrets."
        elif answer_length < 100:
            score = 8
            feedback = "Très bonne réponse! Structure claire et exemples pertinents."
        else:
            score = 9
            feedback = "Excellent! Réponse complète et bien structurée."
        
        # Check for specific keywords
        keywords = ["expérience", "projet", "équipe", "résultat", "appris"]
        found_keywords = [kw for kw in keywords if kw in answer.lower()]
        
        strengths = []
        if found_keywords:
            strengths.append(f"Utilisation de termes clés: {', '.join(found_keywords)}")
        if "chiffre" in answer.lower() or "%" in answer:
            strengths.append("Utilisation de données quantifiées - excellent!")
        if len(answer.split()) > 50:
            strengths.append("Bonne longueur de réponse")
        
        improvements = []
        if "je" not in answer.lower():
            improvements.append("Utilisez plus le pronom 'je' pour parler de vos actions personnelles")
        if not any(kw in answer.lower() for kw in ["par exemple", "comme", "tel que"]):
            improvements.append("Ajoutez des exemples concrets pour illustrer vos propos")
        if answer_length < 50:
            improvements.append("Développez votre réponse avec plus de détails")
        
        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements,
            "sample_answer": self.generate_sample_answer(question)
        }
    
    def generate_sample_answer(self, question: str) -> str:
        """Generate a sample answer for reference"""
        
        sample_answers = {
            "parlez-moi": "Je suis passionné par la technologie depuis mon plus jeune âge. J'ai choisi de me spécialiser dans le développement logiciel car j'aime résoudre des problèmes complexes. Lors de mon dernier stage chez [entreprise], j'ai développé une application qui a réduit le temps de traitement de 30%. Cette expérience m'a confirmé que je souhaite poursuivre dans cette voie et contribuer à des projets innovants au Maroc.",
            "technologies": "Je suis constamment à l'affût des nouvelles technologies. Je suis des formations en ligne sur Coursera et Udemy, je participe à des meetups locaux comme le DevFest Casablanca, et je contribue à des projets open source sur GitHub. Actuellement, j'apprends Docker et Kubernetes pour améliorer mes compétences DevOps.",
            "maroc": "Le marché technologique marocain est en pleine expansion, avec des acteurs majeurs comme OCP, Attijariwafa Bank, et de nombreuses startups innovantes. Je vois un fort potentiel de croissance, particulièrement dans les domaines de la data et de l'IA. Je souhaite contribuer à cette dynamique en apportant mes compétences techniques et ma connaissance du marché local."
        }
        
        for key, answer in sample_answers.items():
            if key in question.lower():
                return answer
        
        return "Je pense que cette expérience m'a permis de développer mes compétences en résolution de problèmes et en travail d'équipe. J'ai appris à m'adapter rapidement aux nouvelles situations et à communiquer efficacement avec les différentes parties prenantes."
    
    def render(self):
        """Render interview coach interface"""
        st.header("🤖 Simulateur d'Entretien IA")
        
        # User context
        col1, col2 = st.columns(2)
        with col1:
            job_type = st.selectbox(
                "Niveau d'expérience",
                ["Stage", "Junior", "Senior", "Manager"]
            )
        with col2:
            question_type = st.selectbox(
                "Type de questions",
                ["🇲🇦 Comportementales", "💻 Techniques", "📊 Études de cas", "🌍 Contexte Maroc"]
            )
        
        # Technical specialization (for technical questions)
        tech_specialization = None
        if question_type == "💻 Techniques":
            tech_specialization = st.selectbox(
                "Spécialisation technique",
                ["Développeur", "Data Engineer", "DevOps", "Data Scientist"]
            )
        
        # Generate or select question
        if st.button("🎲 Générer une question"):
            questions = self.get_questions(tech_specialization or job_type, question_type)
            current_question = questions[0]  # For demo, pick first
            st.session_state.current_question = current_question
            st.session_state.question_generated = True
        
        # Display question
        if st.session_state.get('question_generated', False):
            st.info(f"**Question:** {st.session_state.current_question}")
            
            # User answer
            user_answer = st.text_area("Votre réponse:", height=200, key="answer")
            
            # Submit for analysis
            if st.button("📊 Analyser ma réponse"):
                with st.spinner("Analyse en cours..."):
                    analysis = self.analyze_answer(user_answer, st.session_state.current_question)
                    
                    # Display results
                    st.markdown("### 📈 Résultats de l'analyse")
                    
                    # Score with gauge
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Score", f"{analysis['score']}/10")
                    
                    # Feedback
                    st.success(f"**Feedback:** {analysis['feedback']}")
                    
                    # Strengths
                    if analysis['strengths']:
                        st.markdown("**✅ Points forts:**")
                        for strength in analysis['strengths']:
                            st.write(f"- {strength}")
                    
                    # Improvements
                    if analysis['improvements']:
                        st.markdown("**⚠️ Points à améliorer:**")
                        for improvement in analysis['improvements']:
                            st.write(f"- {improvement}")
                    
                    # Sample answer
                    with st.expander("💡 Voir un exemple de réponse"):
                        st.write(analysis['sample_answer'])
                    
                    # Tips
                    st.info("""
                    **💡 Conseils pour réussir vos entretiens:**
                    - Structurez vos réponses en STAR (Situation, Tâche, Action, Résultat)
                    - Quantifiez vos réalisations avec des chiffres
                    - Soyez honnête sur vos compétences
                    - Préparez des questions à poser à l'intervieweur
                    """)
        
        # Practice tips
        with st.expander("🇲🇦 Conseils pour réussir vos entretiens au Maroc"):
            st.markdown("""
            **Préparation générale:**
            - Renseignez-vous sur l'entreprise (site web, actualités, valeurs)
            - Préparez votre "pitch" de présentation (2 minutes)
            - Ayez des exemples concrets de vos réalisations
            
            **Spécificités marché marocain:**
            - Valorisez votre maîtrise du français et de l'anglais
            - Mentionnez votre connaissance du contexte local
            - Soyez prêt à discuter de votre mobilité (Casablanca, Rabat, etc.)
            """)
