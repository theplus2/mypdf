import fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap

class PDFEngine:
    def __init__(self):
        self.doc = None
    
    def open(self, file_path):
        self.doc = fitz.open(file_path)

    def get_total_pages(self):
        if self.doc:
            return len(self.doc)
        return 0

    def get_page_size(self, page_num):
        if self.doc:
            page = self.doc.load_page(page_num)
            return page.rect.width, page.rect.height
        return 0, 0

    def get_page_image(self, page_num, zoom_level, available_width, invert=False):
        if not self.doc:
            return None
        page = self.doc.load_page(page_num)
        target_width = int(available_width * zoom_level)
        zoom_factor = target_width / page.rect.width
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        
        # 야간 모드(색상 반전) 처리
        pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csRGB)
        if invert:
            pix.invert_irect()
            
        img_format = QImage.Format.Format_RGB888
        q_img = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        return QPixmap.fromImage(q_img)
    
    # [NEW] 썸네일(표지) 이미지를 파일로 저장하는 기능
    def create_thumbnail(self, pdf_path, save_path):
        try:
            # 잠깐 문서를 열어서
            doc = fitz.open(pdf_path)
            page = doc.load_page(0) # 첫 페이지만
            
            # 썸네일용 작은 크기로 변환 (너비 200px 정도)
            zoom = 200 / page.rect.width
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # 파일로 저장
            pix.save(save_path)
            doc.close()
            return True
        except:
            return False

    def close(self):
        if self.doc:
            self.doc.close()