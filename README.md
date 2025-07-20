# 🏪 대환장편의점 POS 시스템

**점주**: 카냥이 🐱  
**특징**: 토스페이먼츠 결제 연동 + 재미있는 할인쿠폰 뽑기 이벤트!

## 🎰 주요 기능

### 🛍️ **상품 관리**
- 상품 등록, 수정, 삭제
- 카테고리별 분류 (음식, 음료, 간식 등)
- 상품 이미지 업로드
- 재고 관리

### 🎯 **할인쿠폰 뽑기 이벤트**
- **손님용 뽑기 페이지**: `/customer`
- **1000원~10000원** 천원단위 할인쿠폰
- **재미있는 애니메이션**: 스피닝, 컨페티, 반짝이는 효과
- **QR코드 생성**: 뽑은 쿠폰을 QR코드로 생성
- **포스기 연동**: 이벤트 QR코드로 손님 참여 유도

### 🛒 **장바구니 & 결제**
- 세션 기반 장바구니
- QR코드 쿠폰 스캔 및 적용
- 쿠폰 취소 기능
- 토스페이먼츠 연동 결제
- 결제 성공/실패 시 소리 재생

### 📊 **관리자 기능**
- 관리자 로그인/로그아웃
- 주문 상태 관리
- 오디오 파일 업로드 (결제 소리)
- 서버 사이드 QR코드 생성

## 🛠️ 기술 스택

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, JavaScript, CSS3 애니메이션
- **Database**: SQLite
- **Payment**: 토스페이먼츠 API
- **QR Code**: Python qrcode 라이브러리
- **Environment**: python-dotenv

## 🚀 설치 및 실행

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

# 관리자 설정
ADMIN_PASSWORD=your_admin_password_here
```

### 5. 서버 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 🎮 사용 방법

### 📱 **손님용 뽑기 이벤트**
1. **포스기에서 이벤트 시작**:
   - 메인 화면 헤더의 "이벤트" 버튼 클릭
   - 이벤트 배너가 나타나며 QR코드 표시

2. **손님이 뽑기 참여**:
   - 본인 폰으로 QR코드 스캔
   - `/customer` 페이지로 이동
   - "뽑기 시작!" 버튼 클릭
   - 재미있는 애니메이션과 함께 할인쿠폰 뽑기

3. **쿠폰 사용**:
   - 뽑은 쿠폰의 QR코드를 포스기에서 스캔
   - 장바구니에 할인 적용

### 🛒 **포스기 사용**
- **상품 선택**: 카테고리별 필터링, 상품 클릭으로 장바구니 추가
- **쿠폰 적용**: QR코드 스캔 또는 수동 입력
- **결제**: 토스페이먼츠로 안전한 결제

### 🔧 **관리자 페이지**
- URL: `http://localhost:5000/admin`
- **로그인 필요**: 관리자 비밀번호 입력
- 상품/카테고리 관리
- 주문 상태 관리
- 오디오 파일 업로드

## 🎰 뽑기 시스템

### 🎯 **할인쿠폰 종류**
- **1000원 쿠폰**: 기본 할인쿠폰 🎁
- **2000원 쿠폰**: 기본 할인쿠폰 🎁
- **3000원 쿠폰**: 좋은 할인쿠폰 🎉
- **4000원 쿠폰**: 좋은 할인쿠폰 🎉
- **5000원 쿠폰**: 큰 할인쿠폰 🎊
- **6000원 쿠폰**: 큰 할인쿠폰 🎊
- **7000원 쿠폰**: 큰 할인쿠폰 🎊
- **8000원 쿠폰**: 최고 할인쿠폰 🏆
- **9000원 쿠폰**: 최고 할인쿠폰 🏆
- **10000원 쿠폰**: 최고 할인쿠폰 🏆

### ✨ **애니메이션 효과**
- **스피닝 효과**: 뽑기 중 숫자가 빠르게 바뀜
- **컨페티 효과**: 뽑기 완료 시 색깔별 종이 조각들이 떨어짐
- **반짝이는 효과**: 배너와 버튼에 빛나는 애니메이션
- **호버 효과**: 마우스 오버 시 확대 및 그림자 효과

## 📁 프로젝트 구조

```
convenience_store/
├── app.py                    # 메인 Flask 애플리케이션
├── requirements.txt          # Python 의존성
├── .env                     # 환경변수 (gitignore됨)
├── .gitignore              # Git 무시 파일
├── README.md               # 프로젝트 설명
├── static/                 # 정적 파일
│   ├── uploads/            # 업로드된 이미지
│   └── audio/              # 오디오 파일
├── templates/              # HTML 템플릿
│   ├── base.html           # 기본 템플릿
│   ├── index.html          # 메인 포스기 페이지
│   ├── customer.html       # 손님용 뽑기 페이지
│   ├── admin.html          # 관리자 페이지
│   ├── admin_categories.html  # 카테고리 관리
│   ├── admin_login.html    # 관리자 로그인
│   ├── cart.html           # 장바구니 페이지
│   ├── order_success.html  # 주문 성공 페이지
│   └── payment_widget.html # 결제 위젯
└── instance/               # 데이터베이스 파일
    └── convenience_store.db
```

## 🔧 API 엔드포인트

### 🎰 **뽑기 관련**
- `GET /customer` - 손님용 뽑기 페이지
- `GET /generate-event-qr` - 이벤트 페이지 QR코드 생성
- `POST /generate-lottery-qr` - 뽑기 결과 QR코드 생성

### 🛒 **장바구니 & 결제**
- `POST /save_cart` - 장바구니 세션 저장
- `GET /load_cart` - 장바구니 세션 로드
- `POST /payment/request` - 결제 요청
- `GET /payment/success` - 결제 성공 처리
- `GET /payment/fail` - 결제 실패 처리

### 🔧 **관리자**
- `GET /admin` - 관리자 페이지
- `POST /admin/login` - 관리자 로그인
- `GET /admin/logout` - 관리자 로그아웃
- `POST /admin/generate-qr` - 관리자용 QR코드 생성

## 🌐 환경변수 설명

| 변수명 | 설명 | 필수 | 기본값 |
|--------|------|------|--------|
| `TOSS_CLIENT_KEY` | 토스페이먼츠 클라이언트 키 | ✅ | - |
| `TOSS_SECRET_KEY` | 토스페이먼츠 시크릿 키 | ✅ | - |
| `TOSS_SECURITY_KEY` | 토스페이먼츠 보안 키 | ✅ | - |
| `SECRET_KEY` | Flask 시크릿 키 | ✅ | - |
| `ADMIN_PASSWORD` | 관리자 비밀번호 | ❌ | admin123 |

## 📱 카메라 사용을 위한 HTTPS 필수

모던 브라우저는 보안상 HTTP에서 카메라 접근을 차단합니다.

### 🚀 **실행 방법**

#### 방법 1: HTTPS로 직접 실행 (권장)
```bash
python app.py
```
- 자동으로 SSL 인증서 생성
- `https://localhost:5000`으로 접속
- 카메라 기능 정상 작동

#### 방법 2: ngrok으로 HTTPS 터널링
```bash
# 1. HTTP로 서버 실행
python app.py

# 2. 새 터미널에서 ngrok 실행
ngrok http 5000

# 3. ngrok에서 제공하는 HTTPS URL 사용
# 예: https://abc123.ngrok.io
```

#### 방법 3: 수동 쿠폰 입력 (카메라 불가 시)
- QR코드 스캔 대신 쿠폰 코드 직접 입력
- 카메라 권한 문제 해결

## ⚠️ 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- 실제 운영 환경에서는 보안 키를 안전하게 관리하세요
- 토스페이먼츠 키는 테스트용과 실제용을 구분해서 사용하세요
- 카메라 기능 사용 시 HTTPS 필수

## 🎉 특징

- **재미있는 뽑기 시스템**: 10가지 할인쿠폰 + 애니메이션
- **안정적인 QR코드**: Python 서버에서 생성
- **모바일 친화적**: 반응형 디자인
- **실시간 결제**: 토스페이먼츠 연동
- **사용자 친화적**: 직관적인 UI/UX

## 📄 라이선스

MIT License

---

**대환장편의점** - 카냥이 사장님이 운영하는 최고의 편의점입니다! 🐱✨