# 무료 터널링 서비스 비교

## 🆓 무료 대안들

### 1. **Cloudflare Tunnel (권장)**
- ✅ **완전 무료**
- ✅ **무제한 터널**
- ✅ **자동 HTTPS**
- ✅ **도메인 제공**
```bash
# 설치
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# 로그인
cloudflared tunnel login

# 터널 생성
cloudflared tunnel create convenience-store

# 실행
cloudflared tunnel run convenience-store
```

### 2. **LocalTunnel**
- ✅ **무료**
- ✅ **여러 터널 가능**
- ❌ **가끔 불안정**
```bash
npm install -g localtunnel
lt --port 5000 --subdomain convenience-store
```

### 3. **Serveo**
- ✅ **무료**
- ✅ **SSH 기반**
- ❌ **가끔 느림**
```bash
ssh -R 80:localhost:5000 serveo.net
```

### 4. **PageKite**
- ✅ **무료 플랜**
- ✅ **안정적**
- ❌ **설정 복잡**
```bash
pip install pagekite
python -m pagekite 5000 yourname.pagekite.me
```

## 🎯 추천 순서

1. **Cloudflare Tunnel** (가장 안정적)
2. **기존 Nginx에 서브도메인 추가**
3. **LocalTunnel** (간단한 테스트용)
4. **포트 8080으로 변경** (로컬 테스트용)

## 🔧 현재 상황에 맞는 방법

### 기존 Nginx 사용 중이라면:
```bash
# 1. 서브도메인 추가
# store.yourname.duckdns.org → localhost:5000

# 2. 편의점 앱 실행
cd convenience_store
python app.py

# 3. 접속
# https://store.yourname.duckdns.org
```

### 완전히 독립적으로 사용하려면:
```bash
# Cloudflare Tunnel 사용
cloudflared tunnel run convenience-store
``` 