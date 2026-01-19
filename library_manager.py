import json
import os
from pdf_engine import PDFEngine
from config import get_data_directory 

class LibraryManager:
    def __init__(self, filename="books.json"):
        # 데이터 디렉토리 경로 가져오기
        self.data_dir = get_data_directory()
        self.filename = os.path.join(self.data_dir, filename)
        
        self.data = {
            "categories": ["전체 보기"],
            "books": []
        }
        
        # covers 폴더도 데이터 디렉토리 안에 생성
        self.cover_dir = os.path.join(self.data_dir, "covers")
        if not os.path.exists(self.cover_dir):
            os.makedirs(self.cover_dir)
            
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, list):
                        self.data["books"] = loaded_data
                    else:
                        self.data = loaded_data
            except:
                pass
        
        if "전체 보기" not in self.data["categories"]:
            self.data["categories"].insert(0, "전체 보기")

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def update_last_page(self, path, page_num):
        self.load_data() # [FIX] 항상 최신 데이터를 불러와서 업데이트 (새로 추가된 책 인식 문제 해결)
        import datetime
        for book in self.data["books"]:
            if book['path'] == path:
                book['last_page'] = page_num
                book['last_read'] = datetime.datetime.now().isoformat()
                self.save_data()
                return True
        return False

    # [NEW] 파일 경로(주소) 업데이트 기능
    def update_book_path(self, old_path, new_path):
        self.load_data()
        for book in self.data["books"]:
            if book['path'] == old_path:
                book['path'] = new_path # 경로 갱신
                
                # 만약 파일명이 바뀌었을 수도 있으니 제목도 갱신할까요? (선택사항)
                # book['title'] = os.path.basename(new_path)
                
                self.save_data()
                return True
        return False

    def add_category(self, name):
        if name not in self.data["categories"]:
            self.data["categories"].append(name)
            self.save_data()
            return True
        return False

    def delete_category(self, name):
        if name == "전체 보기": return False
        
        if name in self.data["categories"]:
            self.data["categories"].remove(name)
            for i in range(len(self.data["books"]) - 1, -1, -1):
                if self.data["books"][i].get('category') == name:
                    self.delete_book(i)
            self.save_data()
            return True
        return False

    def get_categories(self):
        return self.data["categories"]

    def add_books(self, paths, category="전체 보기", progress_callback=None):
        count = 0
        temp_engine = PDFEngine()
        total_files = len(paths)
        
        for i, path in enumerate(paths):
            if progress_callback:
                if not progress_callback(i + 1, total_files, path):
                    break

            if any(b['path'] == path for b in self.data["books"]):
                continue

            title = os.path.basename(path)
            thumb_name = f"{title}_thumb.png"
            thumb_path = os.path.join(self.cover_dir, thumb_name)
            
            # [최적화] 썸네일이 이미 존재하면 재생성하지 않음
            if not os.path.exists(thumb_path):
                temp_engine.create_thumbnail(path, thumb_path)
            
            temp_engine.open(path)
            total_pages = temp_engine.get_total_pages()
            temp_engine.close()
            
            book_info = {
                'path': path,
                'title': title,
                'cover': thumb_path,
                'category': category,
                'last_page': 0,
                'total_pages': total_pages,
                'last_read': None,
                'favorite': False
            }
            self.data["books"].append(book_info)
            count += 1
            
        self.save_data()
        return count

    def move_book(self, path, new_category):
        self.load_data() 
        for book in self.data["books"]:
            if book['path'] == path:
                book['category'] = new_category
                self.save_data()
                return True
        return False

    def delete_book(self, index):
        if 0 <= index < len(self.data["books"]):
            book = self.data["books"][index]
            if 'cover' in book and os.path.exists(book['cover']):
                try: os.remove(book['cover'])
                except: pass
            del self.data["books"][index]
            self.save_data()
            return True
        return False
    
    def delete_book_by_path(self, path):
        self.load_data()
        for i, book in enumerate(self.data["books"]):
            if book['path'] == path:
                return self.delete_book(i)
        return False

    def get_books(self, category="전체 보기"):
        if category == "전체 보기":
            return self.data["books"]
        elif category == "최근 읽은 책":
            # 최근 읽은 순서대로 정렬하여 상위 10권 반환
            read_books = [b for b in self.data["books"] if b.get('last_read')]
            read_books.sort(key=lambda x: x['last_read'], reverse=True)
            return read_books[:10]
        elif category == "즐겨찾기":
            return [b for b in self.data["books"] if b.get('favorite')]
        else:
            return [b for b in self.data["books"] if b.get('category') == category]

    def toggle_favorite(self, path):
        for book in self.data["books"]:
            if book['path'] == path:
                book['favorite'] = not book.get('favorite', False)
                self.save_data()
                return book['favorite']
        return False