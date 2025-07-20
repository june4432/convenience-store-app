#!/bin/bash

# DuckDNS 도메인 설정
DOMAIN="yourname.duckdns.org"
EMAIL="your-email@example.com"

echo "🚀 DuckDNS SSL 인증서 설정 시작"
echo "도메인: $DOMAIN"
echo "이메일: $EMAIL"

# 1. certbot 설치 확인
if ! command -v certbot &> /dev/null; then
    echo "❌ certbot이 설치되지 않았습니다."
    echo "설치 방법: sudo apt-get install certbot"
    exit 1
fi

# 2. Nginx 설치 확인
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx가 설치되지 않았습니다."
    echo "설치 방법: sudo apt-get install nginx"
    exit 1
fi

# 3. 포트 80, 443 방화벽 열기
echo "🔓 방화벽 포트 열기..."
sudo ufw allow 80
sudo ufw allow 443

# 4. SSL 인증서 발급
echo "🔐 SSL 인증서 발급 중..."
sudo certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# 5. Nginx 설정 파일 생성
echo "📝 Nginx 설정 파일 생성..."
sudo tee /etc/nginx/sites-available/convenience-store << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 6. Nginx 설정 활성화
echo "🔗 Nginx 설정 활성화..."
sudo ln -sf /etc/nginx/sites-available/convenience-store /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 7. 자동 갱신 설정
echo "🔄 SSL 인증서 자동 갱신 설정..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL 설정 완료!"
echo "🌐 접속 주소: https://$DOMAIN"
echo "📱 이제 카메라 기능이 정상 작동합니다!" 