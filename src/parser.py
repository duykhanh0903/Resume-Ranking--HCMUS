import json
import os
import pdfplumber
import pytesseract
from . import extractor as ext
import re
from docx import Document

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Thư mục src
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..')) # Thư mục gốc
TESSERACT_PATH = os.path.join(PROJECT_ROOT, 'vendor', 'Tesseract-OCR', 'tesseract.exe')
POPPLER_PATH = os.path.join(PROJECT_ROOT, 'vendor', 'poppler-25.12.0', 'Library', 'bin')
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class ResumeBlockParser:
    def __init__(self, line_gap=4, block_gap=12):
        self.line_gap = line_gap      # Khoảng cách tối đa giữa các từ để coi là cùng 1 dòng
        self.block_gap = block_gap    # Khoảng cách tối đa giữa các dòng để coi là cùng 1 khối

    def _is_scanned(self, page):
        """Kiểm tra xem trang PDF có phải là bản scan không (ít chữ digital)"""
        return len(page.extract_text() or "") < 50

    def parse_file(self, file_path):
        """Hàm entry point duy nhất để xử lý đa định dạng"""
        ext = file_path.split('.')[-1].lower()
        
        if ext == 'pdf':
            return self.parse_pdf(file_path)
        elif ext == 'docx':
            return self.parse_docx(file_path)
        else:
            print(f"Định dạng {ext} không hỗ trợ.")
            return []
        
    def parse_docx(self, docx_path):
        """Trích xuất văn bản từ file Word (Paragraphs & Tables)"""
        doc = Document(docx_path)
        page_data = []

        # Duyệt qua các thành phần theo thứ tự trong body
        for element in doc.element.body:
            # Kiểm tra nếu là Paragraph (thẻ <w:p>)
            if element.tag.endswith('p'):
                text = "".join(node.text for node in element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                if text.strip():
                    page_data.append({"type": "FULL", "text": text.strip()})
            
            # Kiểm tra nếu là Table (thẻ <w:tbl>)
            elif element.tag.endswith('tbl'):
                for table in doc.tables:
                    if table._element == element:
                        table_text = self._extract_table_text(table)
                        if table_text:
                            page_data.append({"type": "FULL", "text": table_text})
        return page_data

    def _extract_table_text(self, table):
        """Chuyển table thành text, giữ phân cách giữa các cột bằng '|'"""
        rows = []
        for row in table.rows:
            # Loại bỏ các cell trùng lặp do merge cell
            cells = []
            for cell in row.cells:
                if not cells or cell.text != cells[-1]:
                    cells.append(cell.text.strip())
            
            row_content = " | ".join(filter(None, cells))
            if row_content:
                rows.append(row_content)
        return "\n".join(rows)
    

    def parse_pdf(self, pdf_path):
        all_extracted_blocks = [] # List tổng để gom tất cả các trang
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                if self._is_scanned(page):
                    # Cập nhật: Hàm scan giờ trả về list
                    page_blocks = self._process_scanned_page(page)
                else:
                    # Hàm digital của bạn đã trả về page_data rồi
                    page_blocks = self._process_digital_page(page)
                
                if page_blocks:
                    all_extracted_blocks.extend(page_blocks)
        
        return all_extracted_blocks # QUAN TRỌNG: Phải return dữ liệu này

    def _process_scanned_page(self, page):
        """Sửa lại để trả về list dict đồng bộ với bản Digital"""
        pix = page.to_image(resolution=300).original
        text = pytesseract.image_to_string(pix, lang='eng+vie')
        
        page_data = []
        sections = [s.strip() for s in text.split('\n\n') if s.strip()]
        for s in sections:
            page_data.append({
                "type": "FULL",
                "text": s.replace('\n', ' ')
            })
        return page_data

    def _process_digital_page(self, page):
        words = page.extract_words(x_tolerance=3, y_tolerance=3)
        if not words: return

        lines = []
        words.sort(key=lambda w: (w['top'], w['x0']))
        if words:
            current_line = [words[0]]
            for i in range(1, len(words)):
                # Tính khoảng cách giữa tâm của 2 từ
                center_y_curr = (words[i]['top'] + words[i]['bottom']) / 2
                center_y_prev = (current_line[-1]['top'] + current_line[-1]['bottom']) / 2
                
                if abs(center_y_curr - center_y_prev) <= 4:
                    current_line.append(words[i])
                else:
                    current_line.sort(key=lambda w: w['x0']) # Sắp xếp X trong nội bộ dòng
                    lines.append(current_line)
                    current_line = [words[i]]
            current_line.sort(key=lambda w: w['x0'])
            lines.append(current_line)

        # 2. Gom các dòng vào các Block dựa trên khoảng cách Y (Paragraphs)
        blocks_of_lines = []
        if lines:
            current_block = [lines[0]]
            for i in range(1, len(lines)):
                gap = lines[i][0]['top'] - current_block[-1][0]['bottom']
                if gap < self.block_gap:
                    current_block.append(lines[i])
                else:
                    blocks_of_lines.append(current_block)
                    current_block = [lines[i]]
            blocks_of_lines.append(current_block)

        page_data = [] # Chứa các block của trang này
        for block in blocks_of_lines:
            block_words = [w for line in block for w in line]
            split_x = self._find_gutter_in_block(block_words, page.width)
            
            if split_x:
                left = [w for w in block_words if w['x1'] <= split_x]
                right = [w for w in block_words if w['x0'] > split_x]
                left.sort(key=lambda w: (w['top'], w['x0']))
                right.sort(key=lambda w: (w['top'], w['x0']))
                
                # Lưu rõ ràng: Đây là block 2 cột
                page_data.append({"type": "LEFT", "text": " ".join([w['text'] for w in left])})
                page_data.append({"type": "RIGHT", "text": " ".join([w['text'] for w in right])})
            else:
                block_words.sort(key=lambda w: (w['top'], w['x0']))
                page_data.append({"type": "FULL", "text": " ".join([w['text'] for w in block_words])})
                
        return page_data

    def _find_gutter_in_block(self, words, page_width):
        """Tìm máng trắng trong một phạm vi cụ thể"""
        width = int(page_width)
        occ = [0] * width
        for w in words:
            for x in range(int(w['x0']), int(w['x1'])):
                if 0 <= x < width: occ[x] = 1
                
        max_gap = 0
        best_split = None
        curr_gap = 0
        # Quét vùng máng khả thi (từ 20% đến 70% chiều rộng)
        for x in range(int(width*0.2), int(width*0.7)):
            if occ[x] == 0:
                curr_gap += 1
            else:
                if curr_gap > max_gap:
                    max_gap = curr_gap
                    best_split = x - (curr_gap // 2)
                curr_gap = 0
        
        # Nếu máng đủ rộng (ví dụ > 30px) thì mới coi là 2 cột
        return best_split if max_gap > 30 else None

    def restructure_data(self, all_blocks):
        """
        Hợp nhất FULL, LEFT, RIGHT thành văn bản phẳng.
        Cover mọi trường hợp layout hỗn hợp.
        """
        if not all_blocks:
            return ""

        final_fragments = []
        
        for block in all_blocks:
            text = block.get('text', '').strip()
            if not text:
                continue

            # --- BƯỚC 1: LÀM SẠCH RÁC OCR ---
            # Loại bỏ các ký tự rác thường xuất hiện khi scan hoặc có icon
            text = re.sub(r'[|\\_~*•►«»©®™¥%]', '', text)
            
            # --- BƯỚC 2: NỐI TỪ BỊ NGẮT (HYPHENATION) ---
            # Ví dụ: "Manage-" và "ment" -> "Management"
            text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)

            # --- BƯỚC 3: XỬ LÝ KHOẢNG TRẮNG ---
            # Xóa các khoảng trắng thừa do OCR nhận diện sai khoảng cách
            text = re.sub(r'\s+', ' ', text)

            # --- BƯỚC 4: GỘP VÀO KẾT QUẢ ---
            # Vì Parser đã sắp xếp theo thứ tự: TOP -> (LEFT rồi đến RIGHT)
            # Nên ta chỉ cần add vào list. 
            final_fragments.append(text)

        # Nối các khối bằng 2 dấu xuống dòng để LLM phân biệt các đoạn (Context)
        # Điều này giúp AI biết khi nào kết thúc một công ty và sang công ty mới
        full_text = "\n\n".join(final_fragments)
        
        return full_text.strip()
    
    # Trong class ResumeBlockParser, sửa lại để trả về data thay vì chỉ in
    def parse_pdf_to_list(self, pdf_path):
        all_extracted_blocks = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Giả sử hàm _process_digital_page trả về list các block
                page_blocks = self._process_digital_page(page) 
                all_extracted_blocks.extend(page_blocks)
        return all_extracted_blocks


if __name__ == "__main__":
    # Giả sử test với file docx trong thư mục data [cite: 26, 153]
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Thư mục src
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..')) # Thư mục gốc

    # Đường dẫn tới các công cụ trong vendor
    TESSERACT_PATH = os.path.join(PROJECT_ROOT, 'vendor', 'Tesseract-OCR', 'tesseract.exe')
    POPPLER_PATH = os.path.join(PROJECT_ROOT, 'vendor', 'poppler-25.12.0', 'Library', 'bin')

    # Đường dẫn tới thư mục data (Cùng cấp với src)
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

    # Giả sử bạn để file ngay trong folder hiện tại để test
    test_file = os.path.join(DATA_DIR, "9.docx")


    if os.path.exists(test_file):
        parser = ResumeBlockParser()
        
        # 1. Tự động nhận diện và trích xuất thành danh sách block
        raw_data = parser.parse_file(test_file) 
        
        # 2. Hợp nhất thành văn bản thuần (giữ logic làm sạch OCR/rác của bạn)
        final_text = parser.restructure_data(raw_data)

        # 3. Đưa vào LLM Extractor
        extractor = ext.ResumeExtractor()
        doc_type = extractor.detect_document_type(final_text)
    
        if doc_type == 'resume':
            result_json = extractor.extract_structured_data(final_text)
            print(json.dumps(result_json, indent=4, ensure_ascii=False))
        else:
            print(f"Cảnh báo: Tài liệu này được phân loại là '{doc_type}', không phải CV.")
        # result_json = extractor.extract_structured_data(final_text)