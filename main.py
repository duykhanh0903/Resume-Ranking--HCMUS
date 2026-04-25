# main.py
from src.parser import ResumeBlockParser
from src.extractor import ResumeExtractor
from src.resume_analyzer import ResumeScorer
import json

def main():
    # 1. Khởi tạo các module
    parser = ResumeBlockParser()
    extractor = ResumeExtractor(model_name='llama3') # Đảm bảo Ollama đang chạy
    scorer = ResumeScorer()

    # 2. Xử lý file đầu vào
    file_name = "4.pdf"
    file_path = f"data/{file_name}"

    
    
    print(f"--- Đang đọc file: {file_name} ---")
    raw_blocks = parser.parse_file(file_path)

    clean_text = parser.restructure_data(raw_blocks)

    extractor = ResumeExtractor()
    doc_type = extractor.detect_document_type(clean_text)

    if doc_type == 'resume':
        print("--- Đang bóc tách thực thể bằng Ollama... ---")
        structured_json = extractor.extract_structured_data(clean_text)
        print(json.dumps(structured_json, indent=4, ensure_ascii=False))
    else:
        print(f"Cảnh báo: Tài liệu này được phân loại là '{doc_type}', không phải CV.")
        return 
    
    if structured_json:
        target_role = "Data Analyst"
        job_requirements = None

        # Duyệt qua các Category để tìm Role tương ứng
        for category, roles in scorer.roles.items():
            if target_role in roles:
                job_requirements = roles[target_role]
                break

        if not job_requirements:
            print(f"Lỗi: Không tìm thấy yêu cầu cho vị trí {target_role}")
        else:
            # Tiếp tục gọi hàm analyze_resume
            results = scorer.analyze_resume(
                resume_data=clean_text,
                structured_json=structured_json,
                job_requirements=job_requirements
            )
            print("\n" + "="*50)
            print(f"KẾT QUẢ PHÂN TÍCH CV: {file_name}")
            print(f"Vị trí ứng tuyển: {target_role}")
            print("="*50)
            
            print("\n[CHI TIẾT ĐIỂM SỐ]")
            for section_name, score in results['section_scores'].items():
                # In ra tên phần đã viết hoa chữ cái đầu và điểm tương ứng
                print(f"- {section_name.replace('_', ' ').capitalize()}: {score}/100")

            print("\n[ĐỀ XUẤT CHỈNH SỬA]")
            counter = 1
            for category, suggestion_list in results['suggesstion'].items():
                for msg in suggestion_list:
                    print(f"{counter}. {msg}")
                    counter += 1
            print("="*50)

if __name__ == "__main__":
    main()

