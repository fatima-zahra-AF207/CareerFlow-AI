import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List
try:
    import spacy
except ImportError:
    spacy = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

class CVAnalyzer:
    """Advanced CV analysis with detailed feedback"""
    
    def __init__(self):
        # Load NLP models - handle errors if not installed
        try:
            self.nlp_fr = spacy.load("fr_core_news_sm")
            self.nlp_en = spacy.load("en_core_web_sm")
        except:
            self.nlp_fr = None
            self.nlp_en = None
        
    def extract_text(self, uploaded_file) -> str:
        """Extract text from PDF, DOCX, or image files with multiple fallbacks"""
        text = ""
        
        if uploaded_file.type == "application/pdf":
            # Stage 1: PyPDF2 (fastest)
            if PyPDF2:
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                except:
                    pass
            
            # Stage 2: pdfplumber (more robust for complex layouts/Chrome PDF)
            if (not text or len(text.strip()) < 100) and pdfplumber:
                try:
                    uploaded_file.seek(0)
                    with pdfplumber.open(uploaded_file) as pdf:
                        text = ""
                        for page in pdf.pages:
                            extracted = page.extract_text()
                            if extracted:
                                text += extracted + "\n"
                except:
                    pass
            
            # Stage 3: OCR fallback (for scanned PDFs)
            if (not text or len(text.strip()) < 50) and pytesseract:
                try:
                    from pdf2image import convert_from_bytes
                    uploaded_file.seek(0)
                    images = convert_from_bytes(uploaded_file.read())
                    text = ""
                    for img in images:
                        text += pytesseract.image_to_string(img, lang="fra+eng+ara")
                except:
                    text = "L'extraction de texte a échoué. Essayez de convertir le PDF en images ou DOCX."

            if not text and PyPDF2 is None and pdfplumber is None:
                raise ImportError("Bibliothèques PDF manquantes (PyPDF2, pdfplumber).")
                
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if docx is None:
                raise ImportError("La bibliothèque 'python-docx' est manquante pour l'analyse des fichiers Word. Veuillez l'installer.")
            doc = docx.Document(uploaded_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
        elif uploaded_file.type.startswith("image/"):
            if Image is None:
                raise ImportError("La bibliothèque 'Pillow' est manquante pour l'analyse des images. Veuillez l'installer.")
            image = Image.open(uploaded_file)
            if pytesseract:
                text = pytesseract.image_to_string(image, lang="fra+ara+eng")
            else:
                text = "OCR non disponible (pytesseract non installé)"
            
        return text
    
    def extract_skills(self, text: str) -> Dict[str, int]:
        """Extract skills and rate proficiency"""
        skills_database = {
            # Programming Languages
            "Python": ["python", "django", "flask", "fastapi"],
            "JavaScript": ["javascript", "react", "angular", "vue", "node.js"],
            "Java": ["java", "spring boot", "j2ee"],
            "PHP": ["php", "laravel", "symfony"],
            "SQL": ["sql", "mysql", "postgresql", "oracle"],
            
            # Cloud & DevOps
            "AWS": ["aws", "ec2", "s3", "lambda"],
            "Docker": ["docker", "container", "kubernetes"],
            "CI/CD": ["jenkins", "gitlab ci", "github actions"],
            
            # Data & AI
            "Machine Learning": ["machine learning", "ml", "tensorflow", "pytorch"],
            "Data Science": ["data science", "pandas", "numpy", "scikit-learn"],
            
            # Languages
            "Français": ["français", "french", "langue française"],
            "Anglais": ["anglais", "english", "toeic", "ielts"],
            "Arabe": ["arabe", "arabic", "langue arabe"]
        }
        
        skills_scores = {}
        text_lower = text.lower()
        
        for skill, keywords in skills_database.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 20
            if score > 0:
                skills_scores[skill] = min(score, 100)
                
        return skills_scores
    
    def calculate_ats_score(self, text: str) -> int:
        """Calculate ATS compatibility score based on Moroccan market"""
        score = 0
        text_lower = text.lower()
        
        # Structure checks (20 points)
        if "expérience" in text_lower or "experience" in text_lower:
            score += 5
        if "formation" in text_lower or "education" in text_lower:
            score += 5
        if "compétences" in text_lower or "skills" in text_lower:
            score += 5
        if "contact" in text_lower or "email" in text_lower:
            score += 5
            
        # Keywords for Moroccan market (30 points)
        moroccan_keywords = ["maroc", "casablanca", "rabat", "tanger", "ocp", "attijari", "cdg"]
        for keyword in moroccan_keywords:
            if keyword in text_lower:
                score += 3
                
        # Format quality (20 points)
        words = text.split()
        if 200 < len(words) < 800:
            score += 10
        if "\n" in text:
            score += 5
        if any(char.isdigit() for char in text):
            score += 5
            
        # Language proficiency (30 points)
        if "français" in text_lower or "french" in text_lower:
            score += 15
        if "anglais" in text_lower or "english" in text_lower:
            score += 10
        if "arabe" in text_lower or "arabic" in text_lower:
            score += 5
            
        return min(score, 100)
    
    def generate_suggestions(self, text: str, skills: Dict[str, int], ats_score: int) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        text_lower = text.lower()
        
        # ATS-based suggestions
        if ats_score < 70:
            suggestions.append("⚠️ Ajoutez plus de mots-clés spécifiques à votre secteur pour améliorer le score ATS")
        if "linkedin" not in text_lower:
            suggestions.append("🔗 Ajoutez votre profil LinkedIn pour plus de crédibilité")
            
        # Structure suggestions
        if "résumé" not in text_lower and "resume" not in text_lower:
            suggestions.append("📝 Ajoutez un résumé professionnel en haut de votre CV")
        if len(text.split()) < 300:
            suggestions.append("📄 Votre CV est trop court. Développez vos expériences avec des réalisations concrètes")
            
        # Moroccan market suggestions
        if "maroc" not in text_lower:
            suggestions.append("🇲🇦 Mentionnez votre disponibilité pour travailler au Maroc")
        if not any(word in text_lower for word in ["français", "french"]):
            suggestions.append("🇫🇷 Le français est essentiel sur le marché marocain. Ajoutez votre niveau")
            
        # Skills suggestions
        if len(skills) < 5:
            suggestions.append("💪 Ajoutez une section compétences avec au moins 5-7 technologies clés")
            
        # Achievement suggestions
        if not any(word in text_lower for word in ["%", "augmenté", "réduit", "géré", "dirigé"]):
            suggestions.append("🏆 Quantifiez vos réalisations avec des chiffres et des résultats concrets")
            
        return suggestions
    
    def analyze(self, uploaded_file) -> Dict:
        """Complete CV analysis"""
        text = self.extract_text(uploaded_file)
        skills = self.extract_skills(text)
        ats_score = self.calculate_ats_score(text)
        suggestions = self.generate_suggestions(text, skills, ats_score)
        
        return {
            "text": text,
            "skills": skills,
            "ats_score": ats_score,
            "suggestions": suggestions,
            "word_count": len(text.split())
        }
