import sys
import os
import re
from collections import Counter

# Import JOB_ROLES
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.configs.job_role import JOB_ROLES


class ResumeScorer:
    def __init__(self):
        self.roles = JOB_ROLES

        # --- Skill normalization ---
        self.SKILL_SYNONYMS = {
            "nodejs": "node.js",
            "node": "node.js",
            "rest api": "apis",
            "restful api": "apis",
            "postgres": "sql",
            "mysql": "sql",
            "mongo": "mongodb",
            "js": "javascript",
            "py": "python"
        }

        # Education ranking
        self.EDU_MAP = {
            "high school": 1,
            "bachelor": 2,
            "master": 3,
            "phd": 4
        }

    def calculate_keyword_match(self, resume_text, required_skills):
        resume_text = resume_text.lower()
        found_skills = []
        missing_skills = []
        
        for skill in required_skills:
            skill_lower = skill.lower()
            # Check for exact match
            if skill_lower in resume_text:
                found_skills.append(skill)
            # Check for partial matches (e.g., "Python" in "Python programming")
            elif any(skill_lower in phrase for phrase in resume_text.split('.')):
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        match_score = (len(found_skills) / len(required_skills)) * 100 if required_skills else 0
        
        return {
            'score': match_score,
            'found_skills': found_skills,
            'missing_skills': missing_skills
        }

    def check_resume_sections(self, text):
        text = text.lower()
        essential_sections = {
            'contact': ['email', 'phone', 'address', 'linkedin'],
            'education': ['education', 'university', 'college', 'degree', 'academic'],
            'experience': ['experience', 'work', 'employment', 'job', 'internship'],
            'skills': ['skills', 'technologies', 'tools', 'proficiencies', 'expertise']
        }
        
        section_scores = {}
        for section, keywords in essential_sections.items():
            found = sum(1 for keyword in keywords if keyword in text)
            section_scores[section] = min(25, (found / len(keywords)) * 25)
            
        return sum(section_scores.values())
    
    def check_formatting(self, text):
        lines = text.split('\n')
        score = 100
        deductions = []
        
        # Check for minimum content
        if len(text) < 300:
            score -= 30
            deductions.append("Resume is too short")
            
        # Check for section headers
        if not any(line.isupper() for line in lines):
            score -= 20
            deductions.append("No clear section headers found")
            
        # Check for bullet points
        if not any(line.strip().startswith(('•', '-', '*', '→')) for line in lines):
            score -= 20
            deductions.append("No bullet points found for listing details")
            
        # Check for consistent spacing
        if any(len(line.strip()) == 0 and len(next_line.strip()) == 0 
               for line, next_line in zip(lines[:-1], lines[1:])):
            score -= 15
            deductions.append("Inconsistent spacing between sections")
            
        # Check for contact information format
        contact_patterns = [
            r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone
            r'linkedin\.com/\w+',  # LinkedIn
        ]
        if not any(re.search(pattern, text) for pattern in contact_patterns):
            score -= 15
            deductions.append("Missing or improperly formatted contact information")
            
        return max(0, score), deductions

    def analyze_resume(self, resume_data, structured_json, job_requirements):
        required_skills = job_requirements.get('required_skills', [])

        raw_skills     = structured_json.get('skills', {}) or {}
        technical_skills = raw_skills.get('technical', []) or []
        soft_skills      = raw_skills.get('soft', []) or []
        all_user_skills  = technical_skills + soft_skills

        skills = [
            self.SKILL_SYNONYMS.get(skill.lower(), skill.lower())
            for skill in all_user_skills
        ]
        keyword_match = self.calculate_keyword_match(resume_data, required_skills)

        education_info = structured_json.get('education', []) or []
        education      = [edu.get('degree', '') or '' for edu in education_info if isinstance(edu, dict)]

        experience = structured_json.get('experience', []) or []
        summary    = structured_json.get('summary', '')    or ''

        section_score = self.check_resume_sections(resume_data)
        format_score, format_deductions = self.check_formatting(resume_data)

        # Contact suggestions
        personal_info      = structured_json.get('contact', {}) or {}
        contact_suggestions = []
        if not personal_info.get('email'):
            contact_suggestions.append("Add your email address")
        if not personal_info.get('phone'):
            contact_suggestions.append("Add your phone number")
        if not personal_info.get('links'):
            contact_suggestions.append("Add your LinkedIn/Github/Portfolio profile URL")

        # Summary suggestions
        summary_suggestions = []
        if not summary:
            summary_suggestions.append("Add a professional summary to highlight your key qualifications")
        elif len(summary.split()) < 30:
            summary_suggestions.append("Expand your professional summary to better highlight your experience and goals")
        elif len(summary.split()) > 100:
            summary_suggestions.append("Consider making your summary more concise (aim for 50-75 words)")

        # Skills suggestions
        skills_suggestions = []
        if keyword_match['score'] < 100:
            missing = keyword_match.get('missing_skills', [])
            if missing:
                skills_suggestions.append(f"Missing critical skills for this role: {', '.join(missing)}")

        # Experience suggestions — guard every field with `or ''`
        experience_suggestions = []
        if not experience:
            experience_suggestions.append("Add your work experience section")
        else:
            has_dates = any(
                re.search(r'\b(19|20)\d{2}\b', str(exp.get('period', '') or ''))
                for exp in experience
            )
            has_bullets = any(
                re.search(r'[•\-\*]', str(exp.get('description', '') or ''))
                for exp in experience
            )
            has_action_verbs = any(
                re.search(
                    r'\b(developed|managed|created|implemented|designed|led|improved)\b',
                    str(exp.get('description', '') or '').lower()
                )
                for exp in experience
            )

            if not has_dates:
                experience_suggestions.append("Include dates for each work experience")
            if not has_bullets:
                experience_suggestions.append("Use bullet points to list your achievements and responsibilities")
            if not has_action_verbs:
                experience_suggestions.append("Start bullet points with strong action verbs")

        # Education suggestions — guard every field with `or ''`
        education_suggestions = []
        if not education:
            education_suggestions.append("Add your educational background")
        else:
            has_dates = any(
                re.search(r'\b(19|20)\d{2}\b', str(edu) or '')
                for edu in education
            )
            has_degree = any(
                re.search(
                    r'\b(bachelor|master|phd|b\.|m\.|diploma)\b',
                    str(edu.get('degree', '') or '').lower()
                )
                for edu in education_info
            )
            has_gpa = any(
                re.search(r'\b(gpa|cgpa|grade|percentage)\b', str(edu).lower())
                for edu in education
            )

            if not has_dates:
                education_suggestions.append("Include graduation dates")
            if not has_degree:
                education_suggestions.append("Specify your degree type")
            if not has_gpa and job_requirements.get('require_gpa', False):
                education_suggestions.append("Include your GPA if it's above 3.0")

        format_suggestions = list(format_deductions) if format_score < 100 else []

        # Scores
        contact_score   = max(0, 100 - len(contact_suggestions)   * 25)
        summary_score   = max(0, 100 - len(summary_suggestions)   * 33)
        skills_score    = keyword_match['score']
        experience_score = max(0, 100 - len(experience_suggestions) * 25)
        education_score  = max(0, 100 - len(education_suggestions)  * 25)

        ats_score = (
            int(round(contact_score    * 0.1)) +
            int(round(summary_score    * 0.1)) +
            int(round(skills_score     * 0.3)) +
            int(round(experience_score * 0.2)) +
            int(round(education_score  * 0.1)) +
            int(round(format_score     * 0.2))
        )

        return {
            'suggesstion': {
                'contact_suggestions':    contact_suggestions,
                'summary_suggestions':    summary_suggestions,
                'skills_suggestions':     skills_suggestions,
                'experience_suggestions': experience_suggestions,
                'education_suggestions':  education_suggestions,
                'format_suggestions':     format_suggestions,
            },
            'section_scores': {
                'ats_score':  ats_score,
                'contact':    contact_score,
                'summary':    summary_score,
                'skills':     skills_score,
                'experience': experience_score,
                'education':  education_score,
                'format':     format_score,
            }
        }