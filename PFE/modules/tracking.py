import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class ApplicationTracker:
    """Enhanced tracking system with database"""
    
    def __init__(self, db_path="forsaflow.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS applications
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      company TEXT,
                      position TEXT,
                      status TEXT,
                      date TEXT,
                      notes TEXT,
                      user_id TEXT,
                      created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      date TEXT,
                      location TEXT,
                      status TEXT,
                      preparation INTEGER)''')
        
        conn.commit()
        conn.close()
        
        # Seed sample data if empty
        self.seed_sample_data()
    
    def seed_sample_data(self):
        """Add sample data for demonstration"""
        conn = sqlite3.connect(self.db_path)
        
        # Check if applications exist
        sample_apps = [
            ("OCP Group", "Data Engineer", "Entretien", "2024-03-10", "Premier entretien technique prévu", "user1", "2024-03-01"),
            ("Attijariwafa Bank", "Backend Developer", "Appliqué", "2024-03-12", "CV envoyé via site carrières", "user1", "2024-03-05"),
            ("DXC Technology", "Fullstack Developer", "Refusé", "2024-03-05", "Refus après test technique", "user1", "2024-02-28")
        ]
        
        sample_events = [
            ("Forum EHTP-Entreprises", "2024-05-15", "Casablanca", "À venir", 65),
            ("Forum de l'EMI", "2024-06-10", "Rabat", "À venir", 40),
            ("Salon AMGE-Caravane", "2024-04-22", "Casablanca", "À venir", 85)
        ]
        
        c = conn.cursor()
        
        # Add applications
        c.execute("SELECT COUNT(*) FROM applications")
        if c.fetchone()[0] == 0:
            for app in sample_apps:
                c.execute("INSERT INTO applications (company, position, status, date, notes, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", app)
        
        # Add events
        c.execute("SELECT COUNT(*) FROM events")
        if c.fetchone()[0] == 0:
            for event in sample_events:
                c.execute("INSERT INTO events (name, date, location, status, preparation) VALUES (?, ?, ?, ?, ?)", event)
        
        conn.commit()
        conn.close()
    
    def get_applications(self, user_id="user1") -> pd.DataFrame:
        """Get all applications for user"""
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT id, company, position, status, date, notes FROM applications WHERE user_id = '{user_id}' ORDER BY date DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_application(self, company, position, status, date, notes, user_id="user1"):
        """Add new application"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO applications (company, position, status, date, notes, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (company, position, status, date, notes, user_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def update_application(self, app_id, status):
        """Update application status"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
        conn.commit()
        conn.close()
    
    def delete_application(self, app_id):
        """Delete application"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        conn.close()
    
    def get_events(self) -> pd.DataFrame:
        """Get all events"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM events ORDER BY date", conn)
        conn.close()
        return df
    
    def update_event_preparation(self, event_id, preparation):
        """Update event preparation status"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE events SET preparation = ? WHERE id = ?", (preparation, event_id))
        conn.commit()
        conn.close()
    
    def render_tracking(self):
        """Render tracking interface"""
        st.header("📋 Suivi des Candidatures")
        
        # Add new application
        with st.expander("➕ Ajouter une candidature", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_company = st.text_input("Entreprise")
                new_position = st.text_input("Poste")
                new_date = st.date_input("Date de candidature")
            with col2:
                new_status = st.selectbox("Statut", ["Appliqué", "Entretien téléphonique", "Entretien technique", "Test technique", "Offre reçue", "Refusé"])
                new_notes = st.text_area("Notes")
            
            if st.button("💾 Ajouter"):
                if new_company and new_position:
                    self.add_application(new_company, new_position, new_status, new_date.strftime("%Y-%m-%d"), new_notes)
                    st.success("Candidature ajoutée!")
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires")
        
        # Display applications
        df = self.get_applications()
        
        if not df.empty:
            # Status colors
            status_colors = {
                "Appliqué": "🟡",
                "Entretien téléphonique": "🔵",
                "Entretien technique": "🔵",
                "Test technique": "🟣",
                "Offre reçue": "🟢",
                "Refusé": "🔴"
            }
            
            # Create interactive table with edit/delete
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.5, 1.5, 1, 1])
                
                with col1:
                    st.markdown(f"**{row['company']}**")
                with col2:
                    st.write(row['position'])
                with col3:
                    status_icon = status_colors.get(row['status'], "⚪")
                    st.write(f"{status_icon} {row['status']}")
                with col4:
                    st.write(row['date'])
                with col5:
                    # Edit button
                    new_status = st.selectbox("", ["Appliqué", "Entretien", "Offre", "Refusé"], 
                                             key=f"status_{row['id']}")
                    if st.button("✏️", key=f"edit_{row['id']}"):
                        self.update_application(row['id'], new_status)
                        st.success("Statut mis à jour!")
                        try:
                            st.rerun()
                        except AttributeError:
                            st.experimental_rerun()
                with col6:
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        self.delete_application(row['id'])
                        st.success("Candidature supprimée!")
                        try:
                            st.rerun()
                        except AttributeError:
                            st.experimental_rerun()
                
                # Show notes
                if row['notes']:
                    with st.expander(f"📝 Notes pour {row['company']}"):
                        st.write(row['notes'])
                
                st.markdown("---")
            
            # Analytics section
            st.subheader("📊 Analyse des Candidatures")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(df)
            interviews = len(df[df['status'].str.contains("Entretien", na=False)]) if not df.empty else 0
            offers = len(df[df['status'] == "Offre reçue"]) if not df.empty else 0
            response_rate = ((interviews + offers) / total * 100) if total > 0 else 0
            
            with col1:
                st.metric("Total Candidatures", total)
            with col2:
                st.metric("Entretiens obtenus", interviews)
            with col3:
                st.metric("Offres reçues", offers)
            with col4:
                st.metric("Taux de réponse", f"{response_rate:.0f}%")
            
            # Status distribution chart
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="Répartition par statut",
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Aucune candidature enregistrée. Ajoutez votre première candidature!")
        
        # Events section
        st.subheader("🎪 Salons & Événements au Maroc")
        
        events_df = self.get_events()
        
        if not events_df.empty:
            for _, event in events_df.iterrows():
                # Correct way to handle potential string/date conversion
                event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                days_left = (event_date - datetime.now()).days
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{event['name']}**")
                        st.caption(f"📍 {event['location']}")
                    with col2:
                        st.caption(f"📅 {event['date']}")
                        if days_left > 0:
                            st.caption(f"⏰ {days_left} jours restants")
                    with col3:
                        st.write(f"Préparation: {event['preparation']}%")
                        new_prep = st.slider("", 0, 100, int(event['preparation']), 
                                            key=f"prep_{event['id']}")
                        if new_prep != event['preparation']:
                            self.update_event_preparation(event['id'], new_prep)
                    
                    st.progress(event['preparation']/100)
                    st.markdown("---")
