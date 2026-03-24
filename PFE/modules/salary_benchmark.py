import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict

class SalaryBenchmark:
    """Salary comparison for Moroccan market"""
    
    def __init__(self):
        self.salary_data = self.load_salary_data()
    
    def load_salary_data(self) -> pd.DataFrame:
        """Load salary data for Moroccan market"""
        data = {
            "role": [
                "Data Engineer", "Data Engineer", "Data Engineer",
                "Full Stack Dev", "Full Stack Dev", "Full Stack Dev",
                "DevOps", "DevOps", "DevOps",
                "Data Scientist", "Data Scientist", "Data Scientist",
                "Product Manager", "Product Manager", "Product Manager"
            ],
            "experience": [0, 3, 5, 0, 3, 5, 0, 3, 5, 0, 3, 5, 0, 3, 5],
            "casablanca": [8000, 15000, 22000, 7000, 14000, 20000, 9000, 16000, 24000, 8500, 15500, 23000, 10000, 18000, 28000],
            "rabat": [7500, 14000, 20000, 6500, 13000, 18000, 8500, 15000, 22000, 8000, 14500, 21000, 9500, 17000, 26000],
            "tanger": [7000, 13000, 18000, 6000, 12000, 16000, 8000, 14000, 20000, 7500, 13500, 19000, 9000, 16000, 24000],
            "marrakech": [6500, 12500, 17000, 5500, 11500, 15500, 7500, 13500, 19000, 7000, 13000, 18000, 8500, 15500, 23000]
        }
        
        return pd.DataFrame(data)
    
    def get_salary_estimate(self, role: str, experience: int, city: str) -> Dict:
        """Get salary estimate for specific parameters"""
        
        filtered = self.salary_data[
            (self.salary_data['role'] == role) & 
            (self.salary_data['experience'] == experience)
        ]
        
        if not filtered.empty:
            salary = filtered[city.lower()].values[0]
            
            # Calculate range (±15%)
            min_salary = int(salary * 0.85)
            max_salary = int(salary * 1.15)
            
            return {
                "estimated": int(salary),
                "min": min_salary,
                "max": max_salary,
                "currency": "DH"
            }
        else:
            # Interpolate if exact match not found
            return self.interpolate_salary(role, experience, city)
    
    def interpolate_salary(self, role: str, experience: int, city: str) -> Dict:
        """Interpolate salary for non-standard experience levels"""
        
        role_data = self.salary_data[self.salary_data['role'] == role].sort_values('experience')
        
        if experience <= role_data['experience'].min():
            salary = role_data[city.lower()].values[0]
        elif experience >= role_data['experience'].max():
            salary = role_data[city.lower()].values[-1]
        else:
            # Linear interpolation between known points
            exp_prev = role_data[role_data['experience'] <= experience]['experience'].max()
            exp_next = role_data[role_data['experience'] >= experience]['experience'].min()
            
            salary_prev = role_data[role_data['experience'] == exp_prev][city.lower()].values[0]
            salary_next = role_data[role_data['experience'] == exp_next][city.lower()].values[0]
            
            # Linear interpolation
            salary = salary_prev + (salary_next - salary_prev) * (experience - exp_prev) / (exp_next - exp_prev)
        
        min_salary = int(salary * 0.85)
        max_salary = int(salary * 1.15)
        
        return {
            "estimated": int(salary),
            "min": min_salary,
            "max": max_salary,
            "currency": "DH"
        }
    
    def get_market_comparison(self, role: str, experience: int, city: str) -> Dict:
        """Get market comparison statistics"""
        
        # Get salaries for all cities
        cities = ['casablanca', 'rabat', 'tanger', 'marrakech']
        salaries = []
        
        for c in cities:
            data = self.get_salary_estimate(role, experience, c)
            salaries.append(data['estimated'])
        
        city_estimate = self.get_salary_estimate(role, experience, city)['estimated']
        national_average = int(sum(salaries) / len(salaries))
        
        return {
            "national_average": national_average,
            "city_average": city_estimate,
            "max_city": max(salaries),
            "min_city": min(salaries),
            "percentile_25": int(np.percentile(salaries, 25)),
            "percentile_75": int(np.percentile(salaries, 75))
        }
    
    def render(self):
        """Render salary benchmark interface"""
        st.subheader("💰 Benchmark Salarial Maroc")
        
        # Input parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            role = st.selectbox(
                "Poste",
                ["Data Engineer", "Full Stack Dev", "DevOps", "Data Scientist", "Product Manager"]
            )
        
        with col2:
            experience = st.slider(
                "Années d'expérience",
                min_value=0,
                max_value=10,
                value=2,
                step=1
            )
        
        with col3:
            city = st.selectbox(
                "Ville",
                ["Casablanca", "Rabat", "Tanger", "Marrakech"]
            )
        
        if st.button("📊 Comparer"):
            with st.spinner("Analyse en cours..."):
                # Get salary data
                salary = self.get_salary_estimate(role, experience, city.lower())
                comparison = self.get_market_comparison(role, experience, city.lower())
                
                # Display main metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Votre estimation",
                        f"{salary['estimated']:,} DH",
                        delta=f"{salary['min']:,} - {salary['max']:,} DH",
                        delta_color="off"
                    )
                
                with col2:
                    diff = comparison['city_average'] - comparison['national_average']
                    st.metric(
                        "Moyenne nationale",
                        f"{comparison['national_average']:,} DH",
                        delta=f"{diff:,} DH",
                        delta_color="inverse" if diff < 0 else "normal"
                    )
                
                with col3:
                    ratio = (comparison['city_average'] / comparison['national_average'] - 1) * 100
                    st.metric(
                        f"Moyenne {city}",
                        f"{comparison['city_average']:,} DH",
                        delta=f"+{ratio:.0f}% vs national"
                    )
                
                # Create visualization
                fig = go.Figure()
                
                # Add bar for current city
                fig.add_trace(go.Bar(
                    name=f"{city}",
                    x=['Votre estimation'],
                    y=[salary['estimated']],
                    marker_color='#FF6B35',
                    text=[f"{salary['estimated']:,} DH"],
                    textposition='auto',
                    error_y=dict(
                        type='data',
                        symmetric=False,
                        array=[salary['max'] - salary['estimated']],
                        arrayminus=[salary['estimated'] - salary['min']],
                        color='#FF6B35'
                    )
                ))
                
                # Add bar for national average
                fig.add_trace(go.Bar(
                    name='Moyenne nationale',
                    x=['Moyenne nationale'],
                    y=[comparison['national_average']],
                    marker_color='#2E86AB',
                    text=[f"{comparison['national_average']:,} DH"],
                    textposition='auto'
                ))
                
                # Add range for national
                fig.add_trace(go.Bar(
                    name='Fourchette nationale',
                    x=['Fourchette'],
                    y=[comparison['percentile_75']],
                    marker_color='#A23B72',
                    text=[f"{comparison['percentile_25']:,} - {comparison['percentile_75']:,} DH"],
                    textposition='auto',
                    opacity=0.6
                ))
                
                fig.update_layout(
                    title=f"Comparaison salariale - {role} ({experience} ans)",
                    yaxis_title="Salaire mensuel (DH)",
                    barmode='group',
                    showlegend=True,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # City comparison
                st.subheader("📊 Comparaison par ville")
                
                cities = ['Casablanca', 'Rabat', 'Tanger', 'Marrakech']
                city_salaries = []
                
                for c in cities:
                    s = self.get_salary_estimate(role, experience, c.lower())
                    city_salaries.append(s['estimated'])
                
                fig_cities = px.bar(
                    x=cities,
                    y=city_salaries,
                    title=f"Salaire selon la ville - {role} ({experience} ans)",
                    labels={'x': 'Ville', 'y': 'Salaire mensuel (DH)'},
                    color=city_salaries,
                    color_continuous_scale='Viridis'
                )
                
                st.plotly_chart(fig_cities, use_container_width=True)
                
                # Negotiation tips
                st.subheader("💡 Conseils de négociation")
                
                tips = [
                    f"📍 À {city}, le salaire moyen pour ce poste est de {comparison['city_average']:,} DH",
                    f"📈 Avec {experience} ans d'expérience, vous pouvez viser entre {salary['min']:,} et {salary['max']:,} DH",
                    "🇲🇦 N'hésitez pas à demander des avantages complémentaires: prime de performance, tickets restaurant, mutuelle",
                    "📊 Préparez des arguments basés sur votre valeur ajoutée et les données du marché",
                    "🗣️ La négociation est bien perçue au Maroc si elle est bien préparée et argumentée"
                ]
                
                for tip in tips:
                    st.info(tip)
