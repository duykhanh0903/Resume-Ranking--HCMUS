import os
import re
import json
from groq import Groq

class ResumeExtractor:
    def __init__(self, model_name='llama-3.3-70b-versatile'):
        self.model_name = model_name

        self.keys = [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"GROQ_API_KEY_{i}")]
        if not self.keys:
            print("⚠️ CẢNH BÁO: Không tìm thấy GROQ_API_KEY trong .env")

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

    def _call_groq_with_fallback(self, prompt: str, is_json=False) -> str:
        """Gọi Groq API tự động xoay vòng key nếu bị Rate Limit"""
        for i, key in enumerate(self.keys):
            try:
                client = Groq(api_key=key)
                params = {
                    "model": self.model_name,
                    "messages": [{'role': 'user', 'content': prompt}],
                    "temperature": 0 if is_json else 0.2
                }
                if is_json:
                    params["response_format"] = {"type": "json_object"}
                    
                response = client.chat.completions.create(**params)
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ [Extractor] Key {i+1} lỗi: {e}. Đang chuyển key...")
                continue
        return None

    def _mask_pii(self, text: str, regex_info: dict) -> str:
        """Kỹ thuật che giấu dữ liệu cá nhân (Ethics/Privacy)"""
        masked_text = text
        for email in regex_info.get("emails", []):
            masked_text = masked_text.replace(email, "[REDACTED_EMAIL]")
        for phone in regex_info.get("phones", []):
            masked_text = masked_text.replace(phone, "[REDACTED_PHONE]")
        for link in regex_info.get("links", []):
            masked_text = masked_text.replace(link, "[REDACTED_URL]")
        return masked_text

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
        masked_text = self._mask_pii(clean_text, regex_info)
        
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
                "email": "null",
                "phone": "null",
                "address": "null"
            }},
            "education": [
                {{ 
                    "degree": "Academic level ONLY",
                    "field": "The specific major or study area",
                    "institution": "Full school name",
                    "graduation_year": "The four-digit end year of study"
                }}
            ],
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
        {masked_text}
        """
        response_content = self._call_groq_with_fallback(prompt, is_json=True)
        if not response_content:
            return None
        try:
            llm_data = json.loads(response_content)
            
            # 5. Đắp lại thông tin thật từ Regex vào output JSON
            llm_contact = llm_data.get('contact', {}) or {}
            
            final_email = regex_info['emails'][0] if regex_info['emails'] else llm_contact.get('email')
            final_phone = regex_info['phones'][0] if regex_info['phones'] else llm_contact.get('phone')
            
            if final_email == "[REDACTED_EMAIL]": final_email = None
            if final_phone == "[REDACTED_PHONE]": final_phone = None

            final_contact = {
                "email": final_email,
                "phone": final_phone,
                "address": llm_contact.get('address'),
                "links": regex_info['links']
            }
            
            llm_data['contact'] = final_contact
            llm_data['email'] = final_contact['email']
            llm_data['phone'] = final_contact['phone']
            llm_data['links'] = final_contact['links']
            
            if 'contact_info' in llm_data: 
                del llm_data['contact_info']
                
            return llm_data
            
        except Exception as e:
            print(f"Lỗi Parse JSON từ Groq: {e}")
            return None
        
    def extract_narrative_text(self, clean_text: str) -> str:
        """
        Kiểu trích xuất thứ 2: Tổng hợp CV thành đoạn văn bản mô tả dài 
        để phục vụ mô hình SBERT Fine-tuned (So sánh đoạn văn vs đoạn văn).
        """
        regex_info = self._extract_by_regex(clean_text)
        masked_text = self._mask_pii(clean_text, regex_info)

        prompt = f"""
        Role: Technical Recruiter.
        Task: Summarize the candidate's professional experience, skills, technologies, and projects from the resume text into a concise narrative paragraph.
        
        CRITICAL CONSTRAINTS:
        1. Output ONLY the plain text paragraph summarizing their technical backgrounds.
        2. Do not use JSON formatting, bullet points, headers, or any markdown.
        3. Match the writing style of a job applicant describing their experience.

        RESUME TEXT:
        {masked_text}
        """
        try:
            response_content = self._call_groq_with_fallback(prompt, is_json=False)
            return response_content.strip() if response_content else clean_text[:1000]
        except Exception as e:
            print(f"Lỗi trích xuất dạng văn bản: {e}")
            # Fallback về text sạch ban đầu nếu LLM lỗi
            return clean_text[:1000]

    