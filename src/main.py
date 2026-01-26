import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QLineEdit, QScrollArea, QMessageBox, QStackedWidget, 
                             QListWidget, QListWidgetItem, QInputDialog, QAbstractItemView,
                             QMenu, QStyle, QProgressDialog)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer
from .pdf_engine import PDFEngine 
from .library_manager import LibraryManager
from .config import check_old_data_exists, migrate_old_data, cleanup_old_data

# =========================================================
# 0. UI 스타일시트 정의 (현대적이고 깔끔한 디자인)
# =========================================================
DARK_THEME = """
    QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; }
    QListWidget { background-color: #333333; border: 1px solid #444444; border-radius: 10px; padding: 5px; }
    QListWidget::item { border-radius: 8px; margin: 5px; }
    QListWidget::item:hover { background-color: #3d3d3d; }
    QListWidget::item:selected { background-color: #4a9eff; color: white; }
    QPushButton { background-color: #444444; border: none; border-radius: 8px; padding: 8px 15px; font-weight: bold; }
    QPushButton:hover { background-color: #555555; }
    QPushButton#action_btn { background-color: #4a9eff; color: white; }
    QPushButton#action_btn:hover { background-color: #64b5f6; }
    QPushButton#danger_btn { background-color: #ff5252; color: white; }
    QPushButton#danger_btn:hover { background-color: #ff867f; }
    QLineEdit { background-color: #3d3d3d; border: 1px solid #555555; border-radius: 8px; padding: 5px; color: white; }
"""
class LibraryWidget(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app 
        self.manager = LibraryManager()
        self.current_category = "전체 보기" 
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True) 
        self.search_timer.setInterval(300)    
        self.search_timer.timeout.connect(self.execute_search)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # --- [왼쪽] ---
        left_layout = QVBoxLayout()
        lbl_folder = QLabel("📂 폴더 목록")
        lbl_folder.setStyleSheet("font-weight: bold; font-size: 16px;")
        left_layout.addWidget(lbl_folder)

        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("font-size: 14px; padding: 5px;")
        self.folder_list.itemClicked.connect(self.change_category)
        left_layout.addWidget(self.folder_list)

        folder_btn_layout = QHBoxLayout()
        self.btn_add_folder = QPushButton("+ 추가")
        self.btn_add_folder.clicked.connect(self.add_folder)
        folder_btn_layout.addWidget(self.btn_add_folder)
        
        self.btn_del_folder = QPushButton("- 삭제")
        self.btn_del_folder.clicked.connect(self.delete_folder)
        folder_btn_layout.addWidget(self.btn_del_folder)
        left_layout.addLayout(folder_btn_layout)
        
        # --- [오른쪽] ---
        right_layout = QVBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 책 제목 검색... (0.3초 뒤 검색됩니다)")
        self.search_bar.setMinimumHeight(40)
        self.search_bar.textChanged.connect(self.on_search_text_changed) 
        self.search_bar.setStyleSheet("""
            QLineEdit { border: 2px solid #ccc; border-radius: 10px; padding: 5px; font-size: 14px; }
        """)
        right_layout.addWidget(self.search_bar)

        self.lbl_title = QLabel("📚 전체 보기")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        right_layout.addWidget(self.lbl_title)

        self.book_list = QListWidget()
        self.book_list.setViewMode(QListWidget.ViewMode.IconMode) 
        self.book_list.setIconSize(QSize(120, 160)) 
        self.book_list.setSpacing(20) 
        self.book_list.setResizeMode(QListWidget.ResizeMode.Adjust) 
        self.book_list.setMovement(QListWidget.Movement.Static)
        self.book_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.book_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.book_list.customContextMenuRequested.connect(self.show_context_menu)

        self.book_list.setStyleSheet("""
            QListWidget::item { width: 150px; height: 220px; margin: 10px; }
            QListWidget::item:selected { background-color: #e0e0e0; border-radius: 10px; color: black; }
        """)
        self.book_list.itemDoubleClicked.connect(self.open_selected_book) 
        right_layout.addWidget(self.book_list)

        book_btn_layout = QHBoxLayout()
        self.btn_add_book = QPushButton("+ 책 대량 추가")
        self.btn_add_book.setMinimumHeight(40)
        self.btn_add_book.setObjectName("action_btn")
        self.btn_add_book.clicked.connect(self.add_books)
        book_btn_layout.addWidget(self.btn_add_book)
        
        self.btn_del_book = QPushButton("🗑️ 선택 삭제")
        self.btn_del_book.setMinimumHeight(40)
        self.btn_del_book.setObjectName("danger_btn")
        self.btn_del_book.clicked.connect(self.delete_selected_books)
        book_btn_layout.addWidget(self.btn_del_book)

        self.btn_open_book = QPushButton("📖 읽기")
        self.btn_open_book.setMinimumHeight(40)
        self.btn_open_book.setObjectName("action_btn")
        self.btn_open_book.clicked.connect(self.open_selected_book)
        book_btn_layout.addWidget(self.btn_open_book)

        right_layout.addLayout(book_btn_layout)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(right_widget, 8)
        
        self.refresh_all()

    def on_search_text_changed(self, text):
        self.search_timer.stop()
        self.search_timer.start()

    def execute_search(self):
        text = self.search_bar.text()
        self.book_list.setUpdatesEnabled(False)
        self.book_list.clear()

        if not text.strip():
            self.refresh_all(skip_clear=True) 
        else:
            self.lbl_title.setText(f"🔍 검색 결과: '{text}'")
            all_books = self.manager.get_books("전체 보기")
            for book in all_books:
                if text.lower() in book['title'].lower():
                    self.add_book_to_list_widget(book)
        
        self.book_list.setUpdatesEnabled(True)

    def add_book_to_list_widget(self, book):
        last_page = book.get('last_page', 0)
        total_pages = book.get('total_pages', '?')
        
        display_text = f"{book['title']}\n({last_page + 1} / {total_pages} P)"
        
        item = QListWidgetItem(display_text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if 'cover' in book and os.path.exists(book['cover']):
            item.setIcon(QIcon(book['cover']))
        
        item.setData(Qt.ItemDataRole.UserRole, book['path'])
        item.setData(Qt.ItemDataRole.UserRole + 1, last_page)
        
        self.book_list.addItem(item)

    def refresh_all(self, skip_clear=False):
        self.manager.load_data()
        self.folder_list.setUpdatesEnabled(False)
        self.book_list.setUpdatesEnabled(False)

        self.folder_list.clear()
        
        # 기본 카테고리 (최근 읽은 책, 즐겨찾기 추가)
        base_categories = ["전체 보기", "최근 읽은 책", "즐겨찾기"]
        categories = base_categories + [c for c in self.manager.get_categories() if c not in base_categories]
        
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        star_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation) # 대용
        clock_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload) # 대용

        for cat in categories:
            item = QListWidgetItem(cat)
            if cat == "최근 읽은 책": item.setIcon(clock_icon)
            elif cat == "즐겨찾기": item.setIcon(star_icon)
            else: item.setIcon(folder_icon)
            self.folder_list.addItem(item)
        
        # 현재 선택된 카테고리 유지
        items = self.folder_list.findItems(self.current_category, Qt.MatchFlag.MatchExactly)
        if items:
            self.folder_list.setCurrentItem(items[0])

        self.search_bar.blockSignals(True)
        if not self.search_bar.text():
            self.search_bar.clear()
        self.search_bar.blockSignals(False)

        if not skip_clear:
            self.book_list.clear()
            
        if not self.search_bar.text():
            self.change_category(None, skip_refresh=True)
            
        self.folder_list.setUpdatesEnabled(True)
        self.book_list.setUpdatesEnabled(True)

    def change_category(self, item, skip_refresh=False):
        if item:
            self.current_category = item.text()
        else:
            items = self.folder_list.findItems(self.current_category, Qt.MatchFlag.MatchExactly)
            if items:
                self.folder_list.setCurrentItem(items[0])
        
        self.lbl_title.setText(f"📚 {self.current_category}")
        
        if not skip_refresh:
            self.book_list.setUpdatesEnabled(False)
            self.book_list.clear()
            
        books = self.manager.get_books(self.current_category)
        for book in books:
            self.add_book_to_list_widget(book)
            
        if not skip_refresh:
            self.book_list.setUpdatesEnabled(True)

    def show_context_menu(self, pos):
        item = self.book_list.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        action_read = QAction("📖 읽기", self)
        action_read.triggered.connect(self.open_selected_book)
        menu.addAction(action_read)

        path = item.data(Qt.ItemDataRole.UserRole)
        is_fav = any(b['path'] == path and b.get('favorite') for b in self.manager.data['books'])
        action_fav = QAction("⭐ 즐겨찾기 해제" if is_fav else "⭐ 즐겨찾기 추가", self)
        action_fav.triggered.connect(lambda: self.toggle_fav(path))
        menu.addAction(action_fav)
        
        move_menu = menu.addMenu("📂 폴더 이동")
        categories = [c for c in self.manager.get_categories() if c not in ["전체 보기", "최근 읽은 책", "즐겨찾기"]]
        for cat in categories:
            if cat == self.current_category:
                continue
            action_move = QAction(cat, self)
            action_move.triggered.connect(lambda checked=False, c=cat: self.move_selected_books(c))
            move_menu.addAction(action_move)

        menu.addSeparator()
        action_del = QAction("🗑️ 삭제", self)
        action_del.triggered.connect(self.delete_selected_books)
        menu.addAction(action_del)

        menu.exec(self.book_list.mapToGlobal(pos))

    def toggle_fav(self, path):
        self.manager.toggle_favorite(path)
        self.refresh_all()

    def move_selected_books(self, target_category):
        selected_items = self.book_list.selectedItems()
        if not selected_items: return

        count = 0
        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            if self.manager.move_book(path, target_category):
                count += 1
        
        self.search_bar.clear() 
        self.refresh_all()
        QMessageBox.information(self, "이동 완료", f"{count}권 이동됨")

    def add_folder(self):
        text, ok = QInputDialog.getText(self, '폴더 추가', '새 폴더 이름:')
        if ok and text:
            if self.manager.add_category(text):
                self.refresh_all()
            else:
                QMessageBox.warning(self, "오류", "이미 존재하는 폴더 이름입니다.")

    def delete_folder(self):
        item = self.folder_list.currentItem()
        if not item: return
        name = item.text()
        if name == "전체 보기":
            QMessageBox.warning(self, "불가", "'전체 보기' 폴더는 삭제할 수 없습니다.")
            return

        reply = QMessageBox.question(self, '폴더 삭제', f"'{name}' 폴더와 목록을 삭제하시겠습니까?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_category(name)
            self.current_category = "전체 보기" 
            self.refresh_all()

    def add_books(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "PDF 파일 선택", "", "PDF Files (*.pdf)")
        if file_names:
            target_cat = self.current_category
            total_files = len(file_names)
            
            progress = QProgressDialog("책을 서재에 등록하는 중입니다...", "취소", 0, total_files, self)
            progress.setWindowTitle("잠시만 기다려주세요")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            
            progress.show()

            def update_progress(current, total, path=None):
                progress.setValue(current)
                filename = os.path.basename(path) if path else ""
                progress.setLabelText(f"책 등록 중... ({current} / {total})\n처리 중: {filename}")
                QApplication.processEvents()
                if progress.wasCanceled(): return False
                return True

            count = self.manager.add_books(file_names, target_cat, update_progress)
            progress.setValue(total_files)
            self.refresh_all()
            
            if progress.wasCanceled():
                QMessageBox.information(self, "중단됨", f"{count}권까지만 추가하고 중단했습니다.")
            else:
                QMessageBox.information(self, "성공", f"{count}권의 책이 추가되었습니다!")

    def delete_selected_books(self):
        selected_items = self.book_list.selectedItems()
        if not selected_items: return
            
        count = len(selected_items)
        reply = QMessageBox.question(self, '삭제 확인', f"선택한 {count}권을 삭제하시겠습니까?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                path = item.data(Qt.ItemDataRole.UserRole)
                self.manager.delete_book_by_path(path)
            
            if self.search_bar.text():
                self.execute_search()
            else:
                self.refresh_all()

    # [수정됨] 책 열 때 파일 존재 여부 체크 및 재연결 로직
    def open_selected_book(self):
        try:
            current_item = self.book_list.currentItem()
            if current_item:
                path = current_item.data(Qt.ItemDataRole.UserRole)
                last_page = current_item.data(Qt.ItemDataRole.UserRole + 1)
                
                # [CHECK] 파일이 진짜 있는지 확인
                if not os.path.exists(path):
                    # 파일이 없음! 물어보기
                    box = QMessageBox()
                    box.setIcon(QMessageBox.Icon.Warning)
                    box.setWindowTitle("파일을 찾을 수 없음")
                    box.setText("원본 파일이 이동되었거나 삭제된 것 같습니다.")
                    box.setInformativeText("새로운 위치를 찾아 연결하시겠습니까?")
                    
                    btn_find = box.addButton("새 위치 찾기", QMessageBox.ButtonRole.AcceptRole)
                    btn_cancel = box.addButton("취소", QMessageBox.ButtonRole.RejectRole)
                    
                    box.exec()
                    
                    if box.clickedButton() == btn_find:
                        # 새 파일 찾기 창 띄우기
                        new_path, _ = QFileDialog.getOpenFileName(self, "이동된 파일 찾기", "", "PDF Files (*.pdf)")
                        if new_path:
                            # 매니저에게 주소 갱신 요청
                            if self.manager.update_book_path(path, new_path):
                                QMessageBox.information(self, "완료", "책이 성공적으로 다시 연결되었습니다!")
                                self.refresh_all() # 화면 갱신
                                # 연결됐으니 바로 열어주기 (선택사항)
                                self.parent_app.show_reader(new_path, last_page)
                            else:
                                QMessageBox.warning(self, "실패", "주소를 업데이트하지 못했습니다.")
                    return

                # 파일이 잘 있으면 그냥 열기
                self.parent_app.show_reader(path, last_page)
            else:
                QMessageBox.warning(self, "알림", "읽을 책을 선택해주세요.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"책을 여는 도중 오류가 발생했습니다:\n{str(e)}")
            print(f"Error opening book: {e}")

# =========================================================
# 2. 독서 화면 (Ver 5.0 유지)
# =========================================================
class ReaderWidget(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.manager = LibraryManager() 
        self.engine = PDFEngine()
        
        self.current_book_path = None 
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.dark_mode = True # 기본 야간 모드 ON
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        control_layout = QHBoxLayout()
        self.btn_back = QPushButton("📚 서재로")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_back)

        self.btn_dark_mode = QPushButton("🌙 야간 모드 ON")
        self.btn_dark_mode.clicked.connect(self.toggle_dark_mode)
        self.btn_dark_mode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_dark_mode)

        self.btn_first = QPushButton("⏮ 처음")
        self.btn_first.clicked.connect(self.go_first_page)
        self.btn_first.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_first)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_prev.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("▶")
        self.btn_next.clicked.connect(self.next_page)
        self.btn_next.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_next)

        self.input_page = QLineEdit()
        self.input_page.setPlaceholderText("Page")
        self.input_page.setFixedWidth(60)
        self.input_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_page.returnPressed.connect(self.jump_to_page)
        self.input_page.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        control_layout.addWidget(self.input_page)

        self.lbl_total_page = QLabel("/ 0")
        control_layout.addWidget(self.lbl_total_page)

        control_layout.addStretch()

        self.btn_fit = QPushButton("⟲ 한눈에 보기")
        self.btn_fit.clicked.connect(self.fit_to_window)
        self.btn_fit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_fit)

        self.btn_zoom_out = QPushButton("축소 (-)")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_zoom_out.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_zoom_out)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setFixedWidth(50)
        self.lbl_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.lbl_zoom)

        self.btn_zoom_in = QPushButton("확대 (+)")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_in.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        control_layout.addWidget(self.btn_zoom_in)

        self.main_layout.addLayout(control_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.installEventFilter(self)
        self.main_layout.addWidget(self.scroll_area)

        self.lbl_viewer = QLabel("파일을 열어주세요")
        self.lbl_viewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_viewer.setStyleSheet("background-color: #505050; color: #aaaaaa; font-size: 30px; font-weight: bold;")
        self.scroll_area.setWidget(self.lbl_viewer)

    def go_back(self):
        if self.current_book_path:
            self.manager.update_last_page(self.current_book_path, self.current_page)
            if self.parent_app.library_widget.search_bar.text():
                self.parent_app.library_widget.search_books(self.parent_app.library_widget.search_bar.text())
            else:
                self.parent_app.library_widget.refresh_all()
            
        self.parent_app.show_library()

    def load_file(self, file_path, initial_page=0): 
        try:
            if os.path.exists(file_path):
                self.engine.open(file_path)
                self.current_book_path = file_path 
                
                self.total_pages = self.engine.get_total_pages()
                
                if initial_page >= self.total_pages:
                    initial_page = 0
                
                self.current_page = initial_page
                
                self.fit_to_window()
                self.lbl_total_page.setText(f"/ {self.total_pages}")
                self.scroll_area.verticalScrollBar().setValue(0)
                self.scroll_area.setFocus()
            else:
                QMessageBox.critical(self, "오류", "파일을 찾을 수 없습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"PDF 파일을 로드하는 중 오류가 발생했습니다:\n{str(e)}")
            print(f"Error loading PDF: {e}")

    def go_first_page(self):
        if self.engine.doc:
            self.current_page = 0
            self.show_page()
            self.scroll_area.verticalScrollBar().setValue(0)
            self.scroll_area.setFocus()

    def fit_to_window(self):
        if not self.engine.doc: return
        page_w, page_h = self.engine.get_page_size(self.current_page)
        if page_w == 0 or page_h == 0: return
        view_w = self.scroll_area.width() - 25
        view_h = self.scroll_area.height() - 25
        if view_w <= 0 or view_h <= 0: return
        ratio_w = view_w / page_w
        ratio_h = view_h / page_h
        best_ratio = min(ratio_w, ratio_h)
        target_width = page_w * best_ratio
        self.zoom_level = target_width / view_w
        self.show_page()

    def zoom_in(self):
        if self.engine.doc:
            if self.zoom_level < 4.0:
                self.zoom_level += 0.1
                self.show_page()

    def zoom_out(self):
        if self.engine.doc:
            if self.zoom_level > 0.15:
                self.zoom_level -= 0.1
                self.show_page()

    def show_page(self):
        if self.engine.doc:
            self.input_page.setText(str(self.current_page + 1))
            self.lbl_zoom.setText(f"{int(self.zoom_level * 100)}%")
            available_width = self.scroll_area.width() - 25 
            pixmap = self.engine.get_page_image(self.current_page, self.zoom_level, available_width, invert=self.dark_mode)
            if pixmap:
                self.lbl_viewer.setPixmap(pixmap)
                self.lbl_viewer.adjustSize()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.btn_dark_mode.setText("🌙 야간 모드 ON" if self.dark_mode else "☀️ 야간 모드 OFF")
        self.show_page()

    def resizeEvent(self, event):
        if self.engine.doc: self.show_page()
        super().resizeEvent(event)

    def prev_page(self):
        if self.engine.doc and self.current_page > 0:
            self.current_page -= 1
            self.show_page()
            self.scroll_area.verticalScrollBar().setValue(0)

    def next_page(self):
        if self.engine.doc and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()
            self.scroll_area.verticalScrollBar().setValue(0)
            
    def jump_to_page(self):
        if not self.engine.doc: return
        text = self.input_page.text()
        if text.isdigit():
            page_num = int(text)
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num - 1
                self.show_page()
                self.scroll_area.verticalScrollBar().setValue(0)
                self.scroll_area.setFocus()

    def eventFilter(self, source, event):
        if source == self.scroll_area:
            if event.type() == QEvent.Type.Wheel:
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.KeyboardModifier.ControlModifier:
                    if event.angleDelta().y() > 0: self.zoom_in()
                    else: self.zoom_out()
                else:
                    if event.angleDelta().y() > 0: self.prev_page()
                    else: self.next_page()
                return True
            elif event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Left:
                    self.prev_page()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.next_page()
                    return True
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()

# =========================================================
# 3. 메인 윈도우
# =========================================================
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나만의 PDF 서재 - Ver 1.0.2 by 윤영천 목사")
        self.setGeometry(100, 100, 1300, 900)
        self.setStyleSheet(DARK_THEME) # 테마 적용

        self.init_menu()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.library_widget = LibraryWidget(self) 
        self.reader_widget = ReaderWidget(self)   

        self.stack.addWidget(self.library_widget)
        self.stack.addWidget(self.reader_widget)
        self.stack.setCurrentIndex(0)
        
        # [새로운 기능] 프로그램 시작 시 데이터 마이그레이션 확인
        self.check_and_migrate_data()

    def init_menu(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("도움말")
        
        show_help_action = QAction("사용 방법 및 정보", self)
        show_help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(show_help_action)
    
    def check_and_migrate_data(self):
        """기존 데이터가 있으면 새 위치로 마이그레이션"""
        if check_old_data_exists():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("데이터 위치 변경")
            msg.setText("프로그램 데이터 저장 위치가 변경되었습니다.")
            msg.setInformativeText(
                "기존 데이터를 새 위치로 이동하시겠습니까?\n\n"
                "새 위치: "
                "Windows - AppData\\Local\\MyPDFLibrary\n"
                "macOS - ~/Library/Application Support/MyPDFLibrary\n\n"
                "이동하면 바탕화면이 깨끗해집니다!"
            )
            
            btn_migrate = msg.addButton("이동하기", QMessageBox.ButtonRole.AcceptRole)
            btn_keep = msg.addButton("나중에", QMessageBox.ButtonRole.RejectRole)
            
            msg.exec()
            
            if msg.clickedButton() == btn_migrate:
                success, migrated_items = migrate_old_data()
                
                if success and migrated_items:
                    # 마이그레이션 성공 - 기존 파일 삭제 여부 묻기
                    cleanup_msg = QMessageBox(self)
                    cleanup_msg.setIcon(QMessageBox.Icon.Question)
                    cleanup_msg.setWindowTitle("마이그레이션 완료")
                    cleanup_msg.setText("데이터가 성공적으로 이동되었습니다!")
                    cleanup_msg.setInformativeText(
                        f"이동된 항목: {', '.join(migrated_items)}\n\n"
                        "기존 위치의 파일을 삭제하시겠습니까?"
                    )
                    
                    btn_delete = cleanup_msg.addButton("삭제", QMessageBox.ButtonRole.AcceptRole)
                    btn_keep_old = cleanup_msg.addButton("보관", QMessageBox.ButtonRole.RejectRole)
                    
                    cleanup_msg.exec()
                    
                    if cleanup_msg.clickedButton() == btn_delete:
                        if cleanup_old_data():
                            QMessageBox.information(self, "완료", "기존 파일이 삭제되었습니다.")
                    
                    # 서재 화면 새로고침
                    self.library_widget.refresh_all()
                elif success:
                    QMessageBox.information(self, "알림", "데이터가 이미 새 위치에 있습니다.")
                else:
                    QMessageBox.warning(self, "오류", "마이그레이션 중 오류가 발생했습니다.")

    def show_help_dialog(self):
        help_text = """
        <h2 style='color: #4a9eff;'>📖 나만의 PDF 서재 사용 방법</h2>
        <p>안녕하세요! <b>나만의 PDF 서재</b>를 이용해주셔서 감사합니다. 이 프로그램은 여러분의 PDF 도서들을 체계적으로 관리하고 편안하게 읽을 수 있도록 설계되었습니다.</p>
        
        <h3 style='color: #64b5f6;'>1. 서재 관리 (도서 등록 및 분류)</h3>
        <ul>
            <li><b>폴더 추가:</b> 왼쪽 '폴더 목록' 하단의 <b>[+ 추가]</b> 버튼을 눌러 카테고리(예: 신학, 소설, 업무 등)를 만듭니다.</li>
            <li><b>책 대량 추가:</b> 메인 화면 하단의 <b>[+ 책 대량 추가]</b> 버튼을 눌러 여러 PDF 파일을 한꺼번에 서재에 등록할 수 있습니다.</li>
            <li><b>즐겨찾기:</b> 책 표지를 <b>마우스 우클릭</b>하여 '즐겨찾기 추가'를 선택하면 상단 별표(⭐) 폴더에서 따로 모아볼 수 있습니다.</li>
            <li><b>도서 검색:</b> 상단 검색창에 제목을 입력하면 실시간으로 도서를 찾아줍니다.</li>
            <li><b>도서 이동/삭제:</b> 책을 우클릭하여 다른 폴더로 이동하거나, 서재에서 삭제할 수 있습니다.</li>
        </ul>

        <h3 style='color: #64b5f6;'>2. 독서 기능 (뷰어 조작)</h3>
        <ul>
            <li><b>책 열기:</b> 책을 <b>더블 클릭</b>하거나 <b>[📖 읽기]</b> 버튼을 누르면 독서 화면으로 전환됩니다.</li>
            <li><b>야간 모드:</b> <b>[🌙 야간 모드 ON]</b> 버튼을 누르면 눈이 편안한 어두운 배경과 반전된 텍스트로 보실 수 있습니다.</li>
            <li><b>확대/축소:</b> 상단 <b>[확대/축소]</b> 버튼 또는 <b>Ctrl + 마우스 휠</b>을 사용하여 글자 크기를 조절하세요.</li>
            <li><b>페이지 이동:</b> 마우스 휠, 키보드 방향키(←, →), 또는 상단 이동 버튼을 사용합니다.</li>
            <li><b>서재로 복귀:</b> <b>[📚 서재로]</b> 버튼을 누르면 현재 읽던 페이지가 자동으로 저장되며 다시 서재 화면으로 돌아갑니다.</li>
        </ul>

        <hr>
        <h3 style='color: #4a9eff;'>👨‍💻 개발자 소개</h3>
        <p style='font-size: 1.1em;'><b>잠실한빛교회 청년부 담당 윤영천 목사</b></p>
        <p>프로그램 사용 중 문의사항이나 피드백은 아래 블로그를 방문해주세요!</p>
        <p>🔗 <b>공식 블로그:</b> <a style='color: #4a9eff;' href='http://blog.naver.com/theplus2'>http://blog.naver.com/theplus2</a></p>
        <p style='font-size: 0.9em; color: #aaaaaa;'>Version 1.0.2 (2026.01.19) | by 윤영천 목사</p>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("프로그램 정보 및 도움말")
        msg.setText(help_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def show_reader(self, file_path, page=0):
        self.reader_widget.load_file(file_path, page) 
        self.stack.setCurrentIndex(1) 

    def show_library(self):
        self.stack.setCurrentIndex(0) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())