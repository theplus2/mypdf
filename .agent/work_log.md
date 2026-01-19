# MyPDF 작업일지

## 프로젝트 개요
- **프로젝트명**: 나만의 PDF 서재
- **개발자**: 윤영천 목사 (잠실한빛교회 청년부 담당)
- **저장소**: https://github.com/theplus2/mypdf
- **현재 버전**: v1.0.2
- **기술 스택**: Python, PyQt6, PyMuPDF, PyInstaller
- **플랫폼**: Windows, macOS

## 프로젝트 구조
```
MyPDF/
├── main.py                    # 메인 애플리케이션 (UI 로직)
├── library_manager.py         # 도서관 데이터 관리
├── pdf_engine.py              # PDF 렌더링 엔진
├── config.py                  # 데이터 디렉토리 관리 (v1.0.2+)
├── books.json                 # 도서 데이터베이스 (데이터 디렉토리로 이동)
├── covers/                    # 책 표지 썸네일 (데이터 디렉토리로 이동)
├── book.ico                   # Windows 아이콘
├── book.icns                  # macOS 아이콘
├── convert_icon.py            # 아이콘 변환 스크립트
├── MyPDFLibrary.spec          # Windows 빌드 설정
├── MyPDFLibrary_Mac.spec      # macOS 빌드 설정
├── MyPDFLibrary.iss           # Windows 인스톨러 설정
├── build_windows.ps1          # Windows 빌드 스크립트
├── requirements.txt           # Python 의존성
└── .github/workflows/
    └── build_and_release.yml  # CI/CD 파이프라인
```

## 주요 기능
1. **서재 관리**
   - PDF 파일 대량 추가
   - 폴더별 분류 (카테고리)
   - 즐겨찾기 기능
   - 최근 읽은 책 자동 추적
   - 책 검색 기능

2. **독서 기능**
   - PDF 뷰어
   - 야간 모드
   - 확대/축소
   - 페이지 이동 (마우스 휠, 키보드)
   - 마지막 읽은 페이지 자동 저장

3. **자동 빌드 & 배포**
   - GitHub Actions를 통한 자동 빌드
   - Windows/Mac 동시 빌드
   - 태그 기반 자동 릴리즈

---

## 작업 히스토리

### 2026-01-19 세션 1: v1.0.0 초기 배포 및 Mac 빌드 수정

#### 1. 버전 1.0.0 통일 및 배포
**작업 내용**:
- 프로그램 버전을 `1.0.0`으로 통일
  - `main.py`: 윈도우 타이틀, 도움말 다이얼로그
  - `MyPDFLibrary.iss`: Windows 인스톨러
  - `MyPDFLibrary_Mac.spec`: macOS 번들
- Git 태그 `v1.0.0` 생성 및 푸시
- 대용량 파일 문제 해결:
  - `build/`, `dist/` 폴더가 git에 추적되어 100MB 제한 초과
  - `.gitignore`에 이미 있었지만 이전에 커밋됨
  - `git reset --soft`, `git rm --cached`로 제거 후 재커밋

**결과**: Windows 빌드 성공, Mac 빌드 실패 (아이콘 오류)

#### 2. Mac 빌드 아이콘 오류 수정 (1차 시도)
**문제**:
```
ValueError: Received icon image '/Users/runner/work/mypdf/mypdf/book.icns' 
which exists but is not in the correct format.
```

**원인**: 
- `build_and_release.yml`에서 `touch book.icns`로 빈 더미 파일 생성
- 빈 파일은 유효한 ICNS 포맷이 아님

**시도한 해결책**:
- `requirements.txt`에 `Pillow` 추가
- `MyPDFLibrary_Mac.spec`에서 `icon='book.ico'`로 변경 (Pillow가 자동 변환하도록)
- 더미 아이콘 생성 단계 제거

**결과**: 여전히 실패 (Pillow의 자동 변환이 CI 환경에서 작동하지 않음)

#### 3. Mac 빌드 아이콘 오류 수정 (2차 시도 - 성공)
**최종 해결책**:
- `convert_icon.py` 스크립트 작성
  - `book.ico`에서 최대 크기 이미지 추출
  - Pillow를 사용해 `book.icns` 생성
- 로컬에서 `book.icns` 생성 후 git에 커밋
- `MyPDFLibrary_Mac.spec`에서 `icon='book.icns'` 사용

**결과**: Mac 빌드 성공, v1.0.0 배포 완료

---

### 2026-01-19 세션 2: v1.0.1 버그 수정

#### 4. 페이지 저장 및 최근 읽은 책 버그 수정
**문제**:
1. 새로 추가한 책을 읽고 닫아도 마지막 페이지가 저장되지 않음
2. 최근 읽은 책 목록에 표시되지 않음

**원인 분석**:
- `ReaderWidget`이 자체 `LibraryManager` 인스턴스를 가짐
- `LibraryWidget`에서 책을 추가하면 `books.json`에 저장됨
- 하지만 `ReaderWidget`의 `LibraryManager`는 초기화 시점의 데이터만 가지고 있음
- `update_last_page()` 호출 시 새 책을 찾지 못해 업데이트 실패

**해결책**:
```python
# library_manager.py
def update_last_page(self, path, page_num):
    self.load_data()  # [FIX] 항상 최신 데이터 로드
    import datetime
    for book in self.data["books"]:
        if book['path'] == path:
            book['last_page'] = page_num
            book['last_read'] = datetime.datetime.now().isoformat()
            self.save_data()
            return True
    return False
```

**버전 업데이트**:
- 모든 버전 문자열을 `1.0.1`로 변경
- Git 태그 `v1.0.1` 생성 및 푸시

**결과**: 버그 수정 완료, v1.0.1 배포 완료

---

### 2026-01-19 세션 3: v1.0.2 데이터 파일 위치 개선 및 코드 최적화

#### 5. 데이터 파일 위치 개선
**문제**:
- 프로그램 실행 파일과 같은 위치에 `books.json`과 `covers/` 폴더가 생성됨
- 바탕화면에 실행 파일을 두면 바탕화면이 지저분해 보임
- macOS에서도 동일한 문제 발생

**해결책**:
1. **새로운 `config.py` 모듈 생성**
   - 운영체제별 적절한 데이터 디렉토리 경로 관리
   - Windows: `%LOCALAPPDATA%\MyPDFLibrary`
   - macOS: `~/Library/Application Support/MyPDFLibrary`
   - Linux: `~/.local/share/MyPDFLibrary`

2. **`library_manager.py` 수정**
   - `config.get_data_directory()`를 사용하여 데이터 경로 설정
   - `books.json`과 `covers/` 폴더가 데이터 디렉토리에 생성되도록 변경

3. **`main.py`에 마이그레이션 로직 추가**
   - 프로그램 시작 시 기존 데이터 존재 여부 확인
   - 사용자에게 데이터 이동 여부 물어보기
   - 자동 마이그레이션 및 기존 파일 정리 옵션 제공

**결과**: 
- 바탕화면이 깨끗해짐
- 기존 사용자 데이터 자동 마이그레이션 지원

#### 6. 코드 최적화
**최적화 항목**:

1. **썸네일 중복 생성 방지** (`library_manager.py`)
   - 썸네일이 이미 존재하면 재생성하지 않음
   - 대량 추가 시 속도 향상
   - 불필요한 파일 I/O 감소

2. **UI 업데이트 배치 처리** (`main.py`)
   - 이미 `setUpdatesEnabled(False/True)` 사용 중
   - 검색 디바운싱 (300ms) 적용되어 있음

**버전 업데이트**:
- 모든 버전 문자열을 `1.0.2`로 변경
  - `main.py`: 윈도우 타이틀, 도움말 다이얼로그
  - `MyPDFLibrary.iss`: Windows 인스톨러
  - `MyPDFLibrary_Mac.spec`: macOS 번들

**결과**: 성능 개선 및 사용자 경험 향상

---

## 주요 기술적 결정 사항

### 1. 아이콘 처리
- **Windows**: `book.ico` 직접 사용
- **macOS**: `book.ico`에서 변환한 `book.icns` 사용
- **이유**: macOS PyInstaller는 ICNS 포맷 요구, CI 환경에서 자동 변환 불안정

### 2. 데이터 동기화
- 각 위젯이 독립적인 `LibraryManager` 인스턴스 사용
- 중요 작업 전 `load_data()` 호출로 최신 상태 보장
- JSON 파일 기반 단순 데이터베이스

### 3. 데이터 저장 위치 (v1.0.2부터)
- **Windows**: `%LOCALAPPDATA%\MyPDFLibrary`
- **macOS**: `~/Library/Application Support/MyPDFLibrary`
- **Linux**: `~/.local/share/MyPDFLibrary`
- **이유**: 운영체제 표준 위치 사용, 바탕화면 정리

### 4. CI/CD 파이프라인
- GitHub Actions 사용
- Windows/Mac 병렬 빌드
- 태그 푸시 시 자동 릴리즈 생성
- 빌드 산출물: Windows `.exe`, macOS `.zip` (앱 번들 포함)

---

## 알려진 이슈 및 개선 사항

### 현재 알려진 이슈
- 없음 (v1.0.2 기준)

### 향후 개선 가능 사항
1. **성능 최적화**
   - 대용량 PDF 로딩 속도 개선
   - 썸네일 생성 비동기 처리

2. **기능 추가**
   - 북마크 기능
   - 메모/하이라이트 기능
   - PDF 내 텍스트 검색
   - 클라우드 동기화

3. **UI/UX 개선**
   - 드래그 앤 드롭으로 책 추가
   - 그리드/리스트 뷰 전환
   - 커스텀 테마

---

## 의존성 관리

### requirements.txt
```
PyQt6
pymupdf
pyinstaller
Pillow
```

### 주요 라이브러리 역할
- **PyQt6**: GUI 프레임워크
- **PyMuPDF (fitz)**: PDF 렌더링 및 썸네일 생성
- **PyInstaller**: 실행 파일 빌드
- **Pillow**: 이미지 처리 (아이콘 변환)

---

## 배포 프로세스

### 로컬 빌드
```powershell
# Windows
python -m PyInstaller MyPDFLibrary.spec --clean --noconfirm
```

```bash
# macOS
python -m PyInstaller MyPDFLibrary_Mac.spec --clean --noconfirm
```

### 자동 배포
1. 코드 수정 및 커밋
2. 버전 번호 업데이트 (main.py, .iss, .spec)
3. Git 태그 생성: `git tag v1.x.x`
4. 푸시: `git push origin master && git push origin v1.x.x`
5. GitHub Actions 자동 실행
6. 릴리즈 페이지에 빌드 결과 자동 업로드

---

## 문제 해결 가이드

### 빌드 실패 시
1. **대용량 파일 오류**
   - `build/`, `dist/` 폴더가 git에 추적되는지 확인
   - `.gitignore` 확인 및 `git rm --cached` 사용

2. **아이콘 오류 (Mac)**
   - `book.icns` 파일이 저장소에 있는지 확인
   - 필요시 `python convert_icon.py` 재실행

3. **의존성 오류**
   - `requirements.txt` 최신 상태 확인
   - CI 환경에서 `pip install -r requirements.txt` 성공 여부 확인

### 런타임 오류 시
1. **책이 열리지 않음**
   - PDF 파일 경로 확인
   - `books.json`의 `path` 필드 검증

2. **페이지가 저장되지 않음**
   - `library_manager.py`의 `update_last_page`에 `load_data()` 호출 확인
   - `books.json` 파일 권한 확인

3. **데이터 파일을 찾을 수 없음 (v1.0.2)**
   - 데이터 디렉토리 경로 확인
   - Windows: `%LOCALAPPDATA%\MyPDFLibrary`
   - macOS: `~/Library/Application Support/MyPDFLibrary`

---

## 연락처 및 리소스
- **개발자 블로그**: http://blog.naver.com/theplus2
- **GitHub 저장소**: https://github.com/theplus2/mypdf
- **릴리즈 페이지**: https://github.com/theplus2/mypdf/releases

---

*마지막 업데이트: 2026-01-19*
*현재 버전: v1.0.2*
