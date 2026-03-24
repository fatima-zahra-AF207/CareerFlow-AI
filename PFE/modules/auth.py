# modules/auth.py - Version corrigée

import streamlit as st
import hashlib
import sqlite3
import re
from datetime import datetime

class AuthManager:
    """User authentication manager"""
    
    def __init__(self, db_path="forsaflow.db"):
        self.db_path = db_path
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Initialize authentication tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      email TEXT UNIQUE,
                      password TEXT,
                      name TEXT,
                      city TEXT,
                      created_at TEXT,
                      last_login TEXT)''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format - Version corrigée"""
        # Vérification simple mais efficace
        if not email or '@' not in email:
            return False
        
        # Séparer local et domaine
        try:
            local, domain = email.split('@', 1)
        except ValueError:
            return False
        
        # Vérifier que le domaine a au moins un point
        if '.' not in domain:
            return False
        
        # Vérifier que le domaine ne commence/finit pas par un point
        if domain.startswith('.') or domain.endswith('.'):
            return False
        
        # Vérifier que l'email n'est pas trop long
        if len(email) > 254:
            return False
        
        # Vérifier qu'il y a au moins un caractère avant @
        if len(local) == 0:
            return False
        
        return True
    
    def register(self, name: str, email: str, password: str, confirm_password: str, city: str) -> tuple:
        """Register new user - Version avec messages d'erreur détaillés"""
        
        # Vérifier que tous les champs sont remplis
        if not all([name, email, password, confirm_password, city]):
            return False, "Tous les champs sont obligatoires"
        
        # Vérifier la validité de l'email
        if not self.validate_email(email):
            return False, f"Format d'email invalide: {email}"
        
        # Vérifier la correspondance des mots de passe
        if password != confirm_password:
            return False, "Les mots de passe ne correspondent pas"
        
        # Vérifier la longueur du mot de passe
        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères"
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            hashed_password = self.hash_password(password)
            c.execute(
                "INSERT INTO users (name, email, password, city, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, email, hashed_password, city, datetime.now().isoformat())
            )
            conn.commit()
            return True, "Inscription réussie! Vous pouvez maintenant vous connecter."
        except sqlite3.IntegrityError:
            return False, "Cet email est déjà utilisé"
        except Exception as e:
            return False, f"Erreur lors de l'inscription: {str(e)}"
        finally:
            conn.close()
    
    def login(self, email: str, password: str) -> tuple:
        """Login user"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        hashed_password = self.hash_password(password)
        
        c.execute(
            "SELECT id, name, email, city FROM users WHERE email = ? AND password = ?",
            (email, hashed_password)
        )
        
        user = c.fetchone()
        
        if user:
            # Update last login
            c.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(), user[0])
            )
            conn.commit()
            
            # Store in session
            st.session_state.user_id = user[0]
            st.session_state.user_name = user[1]
            st.session_state.user_email = user[2]
            st.session_state.user_city = user[3]
            st.session_state.logged_in = True
            
            conn.close()
            return True, "Connexion réussie!"
        else:
            conn.close()
            return False, "Email ou mot de passe incorrect"
    
    def logout(self):
        """Logout user"""
        for key in ['user_id', 'user_name', 'user_email', 'user_city', 'logged_in']:
            if key in st.session_state:
                del st.session_state[key]
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return st.session_state.get('logged_in', False)
    
    def render_login(self):
        """Render login form - Version corrigée"""
        st.title("🇲🇦 ForsaFlow AI - Maroc")
        st.markdown("### Connectez-vous à votre espace")
        
        tab1, tab2 = st.tabs(["🔑 Connexion", "📝 Inscription"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                
                submitted = st.form_submit_button("Se connecter")
                
                if submitted:
                    if not email or not password:
                        st.error("Veuillez remplir tous les champs")
                    else:
                        success, message = self.login(email, password)
                        if success:
                            st.success(message)
                            try:
                                st.rerun()
                            except AttributeError:
                                st.experimental_rerun()
                        else:
                            st.error(message)
            
            # Injection JS pour l'auto-complétion
            st.markdown("""
                <script>
                    var inputs = window.parent.document.querySelectorAll('input');
                    inputs.forEach(input => {
                        if (input.placeholder.includes('Email') || input.getAttribute('aria-label') == 'Email') {
                            input.setAttribute('autocomplete', 'email');
                            input.setAttribute('name', 'email');
                        }
                    });
                </script>
            """, unsafe_allow_html=True)
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Nom complet", placeholder="Ex: Fatima Zahra Mahracha")
                email = st.text_input("Email", placeholder="Ex: fatimazahramahracha205@gmail.com")
                password = st.text_input("Mot de passe", type="password", placeholder="Minimum 6 caractères")
                confirm_password = st.text_input("Confirmer mot de passe", type="password")
                city = st.selectbox("Ville", ["Casablanca", "Rabat", "Tanger", "Marrakech", "Fès", "Agadir", "Autre"])
                
                submitted = st.form_submit_button("S'inscrire")
                
                if submitted:
                    success, message = self.register(name, email, password, confirm_password, city)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                        # Afficher un exemple d'email valide
                        if "email" in message.lower():
                            st.info("💡 Exemple d'email valide: prenom.nom@gmail.com, contact@entreprise.ma")
            
            # Injection JS pour l'auto-complétion (Inscription)
            st.markdown("""
                <script>
                    var inputs = window.parent.document.querySelectorAll('input');
                    inputs.forEach(input => {
                        if (input.placeholder.includes('Fatima') || input.getAttribute('aria-label') == 'Nom complet') {
                            input.setAttribute('autocomplete', 'name');
                            input.setAttribute('name', 'full-name');
                        }
                        if (input.placeholder.includes('email') || input.getAttribute('aria-label') == 'Email') {
                            input.setAttribute('autocomplete', 'email');
                            input.setAttribute('name', 'email');
                        }
                    });
                </script>
            """, unsafe_allow_html=True)
    
    def render_user_menu(self):
        """Render user menu in sidebar"""
        if self.is_logged_in():
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
            st.sidebar.caption(f"📧 {st.session_state.user_email}")
            st.sidebar.caption(f"📍 {st.session_state.user_city}")
            
            if st.sidebar.button("🚪 Déconnexion"):
                self.logout()
