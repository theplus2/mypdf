; 스크립트 시작
[Setup]
; 1. 프로그램 기본 정보
AppName=나만의 PDF 서재
AppVersion=1.0.4
DefaultGroupName=나만의 PDF 서재
AppPublisher=윤영천 목사

; [핵심] 2. 설치 경로 설정 ({sd}는 C드라이브를 뜻합니다)
; 이렇게 하면 C:\MyPDFLibrary 폴더에 설치됩니다. (권한 문제 해결!)
DefaultDirName={sd}\MyPDFLibrary

; 3. 결과물(설치파일) 설정
; 설치파일이 만들어질 폴더 (바탕화면 등으로 변경 가능, 지금은 프로젝트 폴더)
OutputDir=.
; 설치파일 이름 (예: PDF_Library_Setup.exe)
OutputBaseFilename=PDF_Library_Setup
; 설치파일 자체의 아이콘
SetupIconFile=book.ico
; 압축 방식 (최고 효율)
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; 바탕화면 아이콘 만들기 체크박스
Name: "desktopicon"; Description: "바탕화면에 아이콘 만들기"; GroupDescription: "추가 설정"; Flags: unchecked

[Files]
; [중요] 여기에 우리가 만든 exe 파일과 ico 파일이 있어야 합니다.
; 파일명 앞에 경로가 없으므로, 이 스크립트 파일을 main.py 옆에 저장해야 합니다.
Source: "dist\MyPDFLibrary.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "book.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 시작 메뉴에 바로가기 생성
Name: "{group}\나만의 PDF 서재"; Filename: "{app}\MyPDFLibrary.exe"; IconFilename: "{app}\book.ico"
; 바탕화면에 바로가기 생성
Name: "{commondesktop}\나만의 PDF 서재"; Filename: "{app}\MyPDFLibrary.exe"; IconFilename: "{app}\book.ico"; Tasks: desktopicon

[Run]
; 설치 끝나고 바로 실행할지 묻기
Filename: "{app}\MyPDFLibrary.exe"; Description: "나만의 PDF 서재 실행하기"; Flags: nowait postinstall skipifsilent