# 편의점 POS 시스템

토스페이먼츠 결제 연동이 가능한 편의점 포인트 오브 세일(POS) 시스템입니다.

## 주요 기능

- 🛍️ **상품 관리**: 상품 등록, 수정, 삭제
- 📂 **카테고리 관리**: 동적 카테고리 생성 및 관리
- 🛒 **장바구니**: 세션 기반 장바구니 기능
- 💳 **결제 시스템**: 토스페이먼츠 연동 결제
- 📊 **주문 관리**: 주문 상태 관리 및 조회
- 🖼️ **이미지 업로드**: 상품 이미지 업로드 기능

## 기술 스택

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite
- **Payment**: 토스페이먼츠 API
- **Environment**: python-dotenv

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd convenience_store
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# 토스페이먼츠 설정
TOSS_CLIENT_KEY=your_client_key_here
TOSS_SECRET_KEY=your_secret_key_here
TOSS_SECURITY_KEY=your_security_key_here

# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### 5. 서버 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 사용 방법

### 관리자 페이지
- URL: `http://localhost:5000/admin`
- 상품 등록, 수정, 삭제
- 카테고리 관리
- 주문 상태 관리

### 카테고리 관리
- URL: `http://localhost:5000/admin/categories`
- 카테고리 추가, 수정, 삭제
- 아이콘 및 색상 설정

### 결제 테스트
- 토스페이먼츠 연결 시 다양한 방법으로 테스트해볼 수 있습니다.

## 프로젝트 구조

```
convenience_store/
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # Python 의존성
├── .env                  # 환경변수 (gitignore됨)
├── .gitignore           # Git 무시 파일
├── README.md            # 프로젝트 설명
├── static/              # 정적 파일
│   └── uploads/         # 업로드된 이미지
├── templates/           # HTML 템플릿
│   ├── base.html        # 기본 템플릿
│   ├── index.html       # 메인 페이지
│   ├── admin.html       # 관리자 페이지
│   └── admin_categories.html  # 카테고리 관리
└── instance/            # 데이터베이스 파일
    └── convenience_store.db
```

## 환경변수 설명

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `TOSS_CLIENT_KEY` | 토스페이먼츠 클라이언트 키 | ✅ |
| `TOSS_SECRET_KEY` | 토스페이먼츠 시크릿 키 | ✅ |
| `TOSS_SECURITY_KEY` | 토스페이먼츠 보안 키 | ✅ |
| `SECRET_KEY` | Flask 시크릿 키 | ✅ |

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- 실제 운영 환경에서는 보안 키를 안전하게 관리하세요
- 토스페이먼츠 키는 테스트용과 실제용을 구분해서 사용하세요

## 라이선스

MIT License 