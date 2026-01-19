import os
import sys
import shutil
from pathlib import Path

def get_data_directory():
    """운영체제별 적절한 데이터 디렉토리 경로 반환"""
    if sys.platform == 'win32':
        # Windows: AppData\Local\MyPDFLibrary
        base_path = os.getenv('LOCALAPPDATA')
        if not base_path:
            base_path = os.path.expanduser('~\\AppData\\Local')
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/MyPDFLibrary
        base_path = os.path.expanduser('~/Library/Application Support')
    else:
        # Linux: ~/.local/share/MyPDFLibrary
        base_path = os.path.expanduser('~/.local/share')
    
    data_dir = os.path.join(base_path, 'MyPDFLibrary')
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    return data_dir

def get_old_data_directory():
    """기존 데이터가 있던 디렉토리 경로 반환 (실행 파일 위치)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일인 경우
        old_dir = os.path.dirname(sys.executable)
    else:
        # 개발 환경에서 실행하는 경우
        old_dir = os.path.dirname(os.path.abspath(__file__))
    
    return old_dir

def check_old_data_exists():
    """기존 위치에 데이터가 있는지 확인"""
    old_dir = get_old_data_directory()
    old_json = os.path.join(old_dir, 'books.json')
    old_covers = os.path.join(old_dir, 'covers')
    
    # books.json 또는 covers 폴더가 있으면 True
    return os.path.exists(old_json) or os.path.exists(old_covers)

def migrate_old_data():
    """기존 데이터를 새 위치로 마이그레이션
    
    Returns:
        tuple: (성공 여부, 마이그레이션된 항목 리스트)
    """
    old_dir = get_old_data_directory()
    old_json = os.path.join(old_dir, 'books.json')
    old_covers = os.path.join(old_dir, 'covers')
    
    new_dir = get_data_directory()
    new_json = os.path.join(new_dir, 'books.json')
    new_covers = os.path.join(new_dir, 'covers')
    
    migrated_items = []
    
    try:
        # books.json 마이그레이션
        if os.path.exists(old_json) and not os.path.exists(new_json):
            shutil.copy2(old_json, new_json)
            migrated_items.append('books.json')
        
        # covers 폴더 마이그레이션
        if os.path.exists(old_covers) and not os.path.exists(new_covers):
            shutil.copytree(old_covers, new_covers)
            migrated_items.append('covers 폴더')
        
        return True, migrated_items
    except Exception as e:
        print(f"마이그레이션 오류: {e}")
        return False, []

def cleanup_old_data():
    """기존 위치의 데이터 파일 삭제 (마이그레이션 후)"""
    old_dir = get_old_data_directory()
    old_json = os.path.join(old_dir, 'books.json')
    old_covers = os.path.join(old_dir, 'covers')
    
    try:
        # books.json 삭제
        if os.path.exists(old_json):
            os.remove(old_json)
        
        # covers 폴더 삭제
        if os.path.exists(old_covers):
            shutil.rmtree(old_covers)
        
        return True
    except Exception as e:
        print(f"기존 데이터 삭제 오류: {e}")
        return False
