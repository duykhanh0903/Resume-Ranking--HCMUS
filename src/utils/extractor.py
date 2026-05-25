import re
import json
import ollama

class ResumeExtractor:
    def __init__(self, model_name='llama3'):
        self.model_name = model_name
        # Định nghĩa các tập từ khóa đặc trưng
        self.document_types = {
            'resume': ['experience', 'education', 'skills', 'projects', 'summary'],
            'marksheet': ['grade', 'cgpa', 'semester', 'subject', 'marks'],
            'certificate': ['awarded', 'certification', 'completed', 'achievement']
        }

    def detect_document_type(self, text):
        text = text.lower()
        scores = {}
        
        for doc_type, keywords in self.document_types.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            density = matches / len(keywords)
            # Tránh chia cho 0 nếu text rỗng
            frequency = matches / (len(text.split()) + 1)  
            # Trọng số ưu tiên độ phủ của từ khóa (Density)
            scores[doc_type] = (density * 0.7) + (frequency * 0.3)
        
        best_match = max(scores.items(), key=lambda x: x[1])
        # Chỉ công nhận nếu điểm tin cậy > 0.15
        return best_match[0] if best_match[1] > 0.15 else 'unknown'


    def _extract_by_regex(self, text: str, embedded_links: list = None) -> dict:
        email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

        phone = re.findall(
            r'(?<!\d)'
            r'(?:\+?\d{1,3}[\s.-]?)?'
            r'(?:\(\d{2,4}\)[\s.-]?)'
            r'\d{3,4}[\s.-]?\d{3,4}'
            r'|(?<!\d)'
            r'(?:\+?\d{1,3}[\s.-]?)?'
            r'\d{3,4}[\s.-]\d{3,4}[\s.-]\d{3,4}'
            r'(?!\d)',
            text
        )

        text_links = re.findall(
            r'(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com|behance\.net|portfolio\S+)\S+',
            text
        )

        all_links = list(set(text_links + (embedded_links or [])))

        return {
            "emails": list(set(email)),
            "phones": list(set(p.strip() for p in phone if len(re.sub(r'\D', '', p)) >= 9)),
            "links":  all_links,
        }

    def extract_structured_data(self, clean_text: str, embedded_links: list = None) -> dict:
        regex_info = self._extract_by_regex(clean_text, embedded_links)
        
        prompt = f"""
        Role: Expert Resume Data Extractor.
        Task: Extract data into a structured JSON. 

        ### CONSTRAINTS (CRITICAL):
        1. DO NOT INVENT: If a field (e.g., email, phone) is not present in the text, return null. DO NOT guess from other context.
        2. NO REWRITING: Keep the original text for 'summary', 'description', and 'school' names. Do not paraphrase.
        3. OCR REPAIR: Only fix obvious OCR character errors (e.g., 'Pyth0n' -> 'Python').
        4. SOURCE TRUTH: Only use the provided RESUME TEXT. Ignore your internal knowledge about any companies or people mentioned.

        ### OUTPUT SCHEMA:
        {{
            "full_name": "Extract exactly as written",
            "contact": {{
                "email": "null if missing",
                "phone": "null if missing",
                "address": "null if missing"
            }},
            "education": [
                {{ 
                    "degree": "Academic level ONLY",
                    "field": "The specific major or study area",
                    "institution": "Full school name",
                    "graduation_year": "The four-digit end year of study"
                }}
            ,
            "summary": "Original text only, null if missing",
            "total_exp_years": "Numeric value only",
            "experience": [
                {{
                    "company": "Original name",
                    "role": "Original title",
                    "period": "YYYY-MM to YYYY-MM",
                    "description": "Original bullet points/sentences"
                }}
            ],
            "skills": {{
                "technical": [],
                "soft": []
            }}
        }}

        RESUME TEXT:
        {clean_text}
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0} # Để kết quả ổn định nhất
            )
            llm_data = json.loads(response['message']['content'])
            
            final_contact = {
                "email": regex_info['emails'][0] if regex_info['emails'] else llm_data.get('contact', {}).get('email'),
                "phone": regex_info['phones'][0] if regex_info['phones'] else llm_data.get('contact', {}).get('phone'),
                "address": llm_data.get('contact', {}).get('address'), # Địa chỉ thường LLM trích xuất tốt hơn Regex
                "links": regex_info['links'] # Lưu toàn bộ danh sách link LinkedIn/GitHub
            }
            
            # Ghi đè lại vào một key duy nhất
            llm_data['contact'] = final_contact
            
            # Xóa bỏ các key thừa nếu cần
            if 'contact_info' in llm_data: del llm_data['contact_info']
            return llm_data
            
        except Exception as e:
            print(f"Lỗi Extraction: {e}")
            return None
        
    def extract_narrative_text(self, clean_text: str) -> str:
        """
        Kiểu trích xuất thứ 2: Tổng hợp CV thành đoạn văn bản mô tả dài 
        để phục vụ mô hình SBERT Fine-tuned (So sánh đoạn văn vs đoạn văn).
        """
        prompt = f"""
        Role: Technical Recruiter.
        Task: Summarize the candidate's professional experience, skills, technologies, and projects from the resume text into a concise narrative paragraph.
        
        CRITICAL CONSTRAINTS:
        1. Output ONLY the plain text paragraph summarizing their technical backgrounds.
        2. Do not use JSON formatting, bullet points, headers, or any markdown.
        3. Match the writing style of a job applicant describing their experience.

        RESUME TEXT:
        {clean_text}
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.2}
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Lỗi trích xuất dạng văn bản: {e}")
            # Fallback về text sạch ban đầu nếu LLM lỗi
            return clean_text[:1000]

    