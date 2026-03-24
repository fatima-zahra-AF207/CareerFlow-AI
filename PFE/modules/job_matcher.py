import streamlit as st
import requests
from typing import List, Dict
import pandas as pd
from datetime import datetime

class JobMatcher:
    """Enhanced job matching with multiple sources"""
    
    def __init__(self):
        self.sources = {
            "linkedin": "https://www.linkedin.com/jobs",
            "rekrute": "https://www.rekrute.com",
            "emploi": "https://www.emploi.ma"
        }
        
    def fetch_jobs(self, keywords: str, location: str, job_type: str) -> List[Dict]:
        """Fetch jobs from multiple sources"""
        # Note: In production, use actual APIs or web scraping
        # This is a mock implementation with realistic data
        
        mock_jobs = [
            {
                "id": 1,
                "title": "Data Engineer",
                "company": "OCP Group",
                "location": "Casablanca",
                "type": "CDI",
                "description": "Recherche Data Engineer avec expérience en Python, SQL et Big Data",
                "match_score": 92,
                "source": "LinkedIn",
                "date_posted": "2024-03-20",
                "salary_range": "15,000 - 22,000 DH"
            },
            {
                "id": 2,
                "title": "Full Stack Developer",
                "company": "Attijariwafa Bank",
                "location": "Casablanca",
                "type": "CDI",
                "description": "Développeur Full Stack avec React, Node.js et Laravel",
                "match_score": 85,
                "source": "ReKrute",
                "date_posted": "2024-03-18",
                "salary_range": "12,000 - 18,000 DH"
            },
            {
                "id": 3,
                "title": "DevOps Engineer",
                "company": "Maroc Telecom",
                "location": "Rabat",
                "type": "CDI",
                "description": "Ingénieur DevOps avec Docker, Kubernetes et AWS",
                "match_score": 78,
                "source": "Emploi.ma",
                "date_posted": "2024-03-15",
                "salary_range": "14,000 - 20,000 DH"
            },
            {
                "id": 4,
                "title": "Data Scientist (Stage)",
                "company": "Capgemini",
                "location": "Casablanca",
                "type": "Stage",
                "description": "Stage Data Science avec Python, Machine Learning",
                "match_score": 88,
                "source": "LinkedIn",
                "date_posted": "2024-03-22",
                "salary_range": "3,000 - 5,000 DH"
            },
            {
                "id": 5,
                "title": "Backend Developer",
                "company": "HPS",
                "location": "Casablanca",
                "type": "CDI",
                "description": "Développeur Backend Java/Spring Boot",
                "match_score": 75,
                "source": "ReKrute",
                "date_posted": "2024-03-19",
                "salary_range": "13,000 - 19,000 DH"
            }
        ]
        
        # Filter based on user input
        filtered_jobs = []
        for job in mock_jobs:
            if keywords.lower() in job["title"].lower() or keywords.lower() in job["description"].lower():
                if location == "Toutes" or location in job["location"]:
                    if job_type == "Tous" or job_type == job["type"]:
                        filtered_jobs.append(job)
        
        # Sort by match score
        filtered_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return filtered_jobs
    
    def display_job_card(self, job: Dict):
        """Display job in a card format"""
        with st.container():
            # Status badge
            status_color = {
                "CDI": "🟢",
                "CDD": "🟡",
                "Stage": "🔵",
                "Freelance": "🟣"
            }.get(job["type"], "⚪")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {job['title']}")
                st.caption(f"🏢 {job['company']} • 📍 {job['location']} • {status_color} {job['type']}")
            with col2:
                st.markdown(f"**Match: {job['match_score']}%**")
                st.progress(job['match_score']/100)
            
            st.write(job['description'][:200] + "...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"📅 {job['date_posted']}")
            with col2:
                st.caption(f"💰 {job['salary_range']}")
            with col3:
                st.caption(f"🔗 {job['source']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📝 Postuler", key=f"apply_{job['id']}"):
                    st.success(f"Candidature ajoutée pour {job['company']}!")
                    # Add to tracking
            with col2:
                st.button(f"💾 Sauvegarder", key=f"save_{job['id']}")
            
            st.markdown("---")
    
    def render(self):
        """Render job matching interface"""
        st.header("🇲🇦 Offres Recommandées")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            keywords = st.text_input("Mots-clés", placeholder="Ex: Python, React, Stage")
        with col2:
            location = st.selectbox("Ville", ["Toutes", "Casablanca", "Rabat", "Tanger", "Marrakech", "Fès"])
        with col3:
            job_type = st.selectbox("Type de contrat", ["Tous", "CDI", "CDD", "Stage", "Freelance"])
        
        # Search button
        if st.button("🔍 Rechercher"):
            with st.spinner("Recherche des offres en cours..."):
                jobs = self.fetch_jobs(keywords or "développeur", location, job_type)
                
                if jobs:
                    st.success(f"{len(jobs)} offres trouvées")
                    for job in jobs:
                        self.display_job_card(job)
                else:
                    st.info("Aucune offre trouvée. Essayez d'autres mots-clés.")
