from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import os
import requests
import base64
import json
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import sqlite3
import ssl
import tempfile
import subprocess
import qrcode
from io import BytesIO
import base64

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///convenience_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 파일 업로드 크기 제한 (50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# 토스페이먼츠 설정 (환경변수에서 가져오기)
app.config['TOSS_CLIENT_KEY'] = os.getenv('TOSS_CLIENT_KEY')
app.config['TOSS_SECRET_KEY'] = os.getenv('TOSS_SECRET_KEY')
app.config['TOSS_SECURITY_KEY'] = os.getenv('TOSS_SECURITY_KEY')
app.config['TOSS_API_URL'] = 'https://api.tosspayments.com'

# 관리자 설정
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')

# 이미지 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # webp 추가
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 오디오 파일 설정
AUDIO_FOLDER = 'static/audio'
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# 업로드 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# 한국시간 함수
def korea_now():
    """한국시간(KST)을 반환하는 함수"""
    utc_now = datetime.now(timezone.utc)
    kst = timezone(timedelta(hours=9))
    return utc_now.astimezone(kst)

# 관리자 인증 데코레이터
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# 파일 크기 제한 에러 핸들러
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '파일이 너무 큽니다. 50MB 이하의 파일만 업로드 가능합니다.'}), 413

# 데이터베이스 모델
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='fas fa-box')  # FontAwesome 아이콘
    color = db.Column(db.String(20), default='text-secondary')  # Bootstrap 색상 클래스
    created_at = db.Column(db.DateTime, default=korea_now)
    
    # 관계 설정
    products = db.relationship('Product', backref='category_obj', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # 기존 필드 (하위 호환성)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 새로운 외래키
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=korea_now)
    updated_at = db.Column(db.DateTime, default=korea_now, onupdate=korea_now)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=korea_now)
    status = db.Column(db.String(20), default='pending')
    
    # 관계 설정
    payments = db.relationship('Payment', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_key = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    payment_method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=korea_now)
    updated_at = db.Column(db.DateTime, default=korea_now, onupdate=korea_now)

class AudioSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    success_audio_url = db.Column(db.String(200))
    fail_audio_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=korea_now)
    updated_at = db.Column(db.DateTime, default=korea_now, onupdate=korea_now)

# 라우트
@app.route('/')
def index():
    """메인 페이지"""
    products = Product.query.all()
    categories = Category.query.order_by(Category.name).all()
    
    # 상품 데이터를 JSON으로 변환
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'category': product.category,
            'description': product.description,
            'stock': product.stock,
            'image_url': product.image_url
        })
    
    return render_template('index.html', products=products, products_data=products_data, categories=categories)

@app.route('/customer')
def customer():
    """손님용 할인쿠폰 뽑기 페이지"""
    return render_template('customer.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    
    flash(f'{product.name}이(가) 장바구니에 추가되었습니다!')
    return redirect(url_for('index'))

@app.route('/save_cart', methods=['POST'])
def save_cart():
    """장바구니를 세션에 저장"""
    try:
        cart_data = request.get_json()
        session['cart'] = cart_data
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/load_cart')
def load_cart():
    """세션에서 장바구니 로드"""
    cart_data = session.get('cart', {})
    return jsonify({'cart': cart_data})

@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total_amount=0, total_quantity=0)
    
    cart_items = []
    total_amount = 0
    total_quantity = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image_url': product.image_url,
                'category': product.category,
                'quantity': quantity,
                'total': item_total
            })
            total_amount += item_total
            total_quantity += quantity
    
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount, total_quantity=total_quantity)

@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    change = int(data.get('change'))

    if 'cart' not in session:
        session['cart'] = {}

    if product_id in session['cart']:
        session['cart'][product_id] += change
        if session['cart'][product_id] <= 0:
            del session['cart'][product_id]
        session.modified = True # 세션 변경 사항 저장
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '장바구니에 없는 상품입니다.'})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart_post():
    data = request.get_json()
    product_id = str(data.get('product_id'))

    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True # 세션 변경 사항 저장
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '장바구니에 없는 상품입니다.'})

@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('비밀번호가 올바르지 않습니다.', 'error')
    
    # 템플릿 파일이 없을 경우를 대비해 직접 HTML 반환
    try:
        return render_template('admin_login.html')
    except:
        # 임시 HTML 반환
        html_content = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>관리자 로그인 - 편의점</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header i {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .back-link {
            text-align: center;
            margin-top: 1rem;
        }
        .back-link a {
            color: #667eea;
            text-decoration: none;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="login-card">
                    <div class="login-header">
                        <i class="fas fa-user-shield"></i>
                        <h3>관리자 로그인</h3>
                        <p class="text-muted">관리자 비밀번호를 입력하세요</p>
                    </div>
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label for="password" class="form-label">비밀번호</label>
                            <div class="input-group">
                                <span class="input-group-text">
                                    <i class="fas fa-lock"></i>
                                </span>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-login">
                                <i class="fas fa-sign-in-alt me-2"></i>로그인
                            </button>
                        </div>
                    </form>
                    
                    <div class="back-link">
                        <a href="/">
                            <i class="fas fa-arrow-left me-1"></i>메인 페이지로 돌아가기
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        '''
        return html_content

@app.route('/admin/logout')
def admin_logout():
    """관리자 로그아웃"""
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin():
    """관리자 페이지"""
    products = Product.query.all()
    orders = Order.query.order_by(Order.order_date.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin.html', products=products, orders=orders, categories=categories)

@app.route('/admin/order/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status in ['pending', 'processing', 'completed', 'cancelled']:
        order.status = status
        db.session.commit()
        flash('주문 상태가 업데이트되었습니다.')
    return redirect(url_for('admin'))

# 토스페이먼츠 결제 관련 라우트
@app.route('/payment/request', methods=['POST'])
def request_payment():
    """결제 요청"""
    if 'cart' not in session or not session['cart']:
        return jsonify({'error': '장바구니가 비어있습니다.'}), 400
    
    try:
        # 장바구니 정보 가져오기 (새로운 형식)
        cart_items = []
        total = 0
        
        for product_id, item_data in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product:
                quantity = item_data.get('quantity', 1)
                item_total = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
        
        if not cart_items:
            return jsonify({'error': '장바구니에 유효한 상품이 없습니다.'}), 400
        
        # 주문 생성
        order = Order(
            customer_name=request.form.get('customer_name', '고객'),
            customer_phone=request.form.get('customer_phone', '000-0000-0000'),
            total_amount=total
        )
        db.session.add(order)
        db.session.flush()
        
        # 주문 아이템 생성
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(order_item)
        
        # 결제 정보 생성
        payment_key = create_payment_key()
        payment = Payment(
            order_id=order.id,
            payment_key=payment_key,
            amount=total
        )
        db.session.add(payment)
        db.session.commit()
        
        # 토스페이먼츠 결제 요청 데이터
        payment_data = {
            "amount": {
                "currency": "KRW",
                "value": int(total)
            },
            "orderId": f"order_{order.id}_{payment_key[:8]}",
            "orderName": get_order_items_text(cart_items),
            "customerName": order.customer_name,
            "customerEmail": request.form.get('customer_email', 'customer@example.com'),
            "successUrl": url_for('index', _external=True),
            "failUrl": url_for('payment_fail', _external=True),
            "windowTarget": "iframe"
        }
        
        return jsonify({
            'success': True,
            'payment_data': payment_data,
            'client_key': app.config['TOSS_CLIENT_KEY'],
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/payment/success', methods=['GET', 'POST'])
def payment_success():
    """결제 성공 처리"""
    if request.method == 'POST':
        # AJAX 요청 처리
        data = request.get_json()
        payment_key = data.get('paymentKey')
        order_id = data.get('orderId')
        amount = data.get('amount')
    else:
        # GET 요청 처리 (기존 방식)
        payment_key = request.args.get('paymentKey')
        order_id = request.args.get('orderId')
        amount = request.args.get('amount')
    
    if not all([payment_key, order_id, amount]):
        if request.method == 'POST':
            return jsonify({'success': False, 'message': '결제 정보가 올바르지 않습니다.'})
        else:
            flash('결제 정보가 올바르지 않습니다.')
            return redirect(url_for('index'))
    
    try:
        # orderId에서 실제 주문 ID 추출 (order_3_6115c042 -> 3)
        try:
            actual_order_id = int(order_id.split('_')[1])
        except (IndexError, ValueError):
            if request.method == 'POST':
                return jsonify({'success': False, 'message': '주문 ID 형식이 올바르지 않습니다.'})
            else:
                flash('주문 ID 형식이 올바르지 않습니다.')
                return redirect(url_for('index'))
        
        # 주문 정보 업데이트
        order = Order.query.get(actual_order_id)
        if not order:
            if request.method == 'POST':
                return jsonify({'success': False, 'message': '주문 정보를 찾을 수 없습니다.'})
            else:
                flash('주문 정보를 찾을 수 없습니다.')
                return redirect(url_for('index'))
        
        # 결제 승인 API 호출
        approve_data = {
            "amount": int(amount),
            "orderId": order_id
        }
        
        headers = get_toss_auth_header()
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(
            f"{app.config['TOSS_API_URL']}/v1/payments/{payment_key}",
            headers=headers,
            json=approve_data
        )
        
        if response.status_code == 200:
            payment_result = response.json()
            
            order.status = 'completed'
            db.session.commit()
            
            # 결제 정보 생성 또는 업데이트
            payment = Payment.query.filter_by(order_id=actual_order_id).first()
            if payment:
                payment.payment_key = payment_key
                payment.status = 'completed'
                payment.payment_method = payment_result.get('method', 'unknown')
            else:
                payment = Payment(
                    order_id=actual_order_id,
                    payment_key=payment_key,
                    amount=int(amount),
                    status='completed',
                    payment_method=payment_result.get('method', 'unknown')
                )
                db.session.add(payment)
            
            db.session.commit()
            
            # 장바구니 비우기
            session.pop('cart', None)
            
            if request.method == 'POST':
                return jsonify({
                    'success': True, 
                    'message': '결제가 성공적으로 완료되었습니다!',
                    'orderId': order_id
                })
            else:
                # GET 요청 시 메인화면으로 리다이렉트하면서 결제 정보 전달
                return redirect(url_for('index', 
                    paymentKey=payment_key, 
                    orderId=order_id, 
                    amount=amount,
                    success='true'
                ))
        else:
            error_response = response.json() if response.content else {}
            error_message = error_response.get('message', '알 수 없는 오류')
            
            if request.method == 'POST':
                return jsonify({'success': False, 'message': f'결제 승인에 실패했습니다: {error_message}'})
            else:
                # GET 요청 시 메인화면으로 리다이렉트하면서 오류 정보 전달
                return redirect(url_for('index', 
                    code=error_response.get('code', 'UNKNOWN_ERROR'),
                    message=error_message
                ))
            
    except Exception as e:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': f'결제 처리 중 오류가 발생했습니다: {str(e)}'})
        else:
            flash(f'결제 처리 중 오류가 발생했습니다: {str(e)}')
            return redirect(url_for('index'))

@app.route('/payment/fail', methods=['GET', 'POST'])
def payment_fail():
    """결제 실패 처리"""
    error_code = request.args.get('code')
    error_message = request.args.get('message')
    
    if request.method == 'POST':
        return jsonify({
            'success': False, 
            'message': f'결제에 실패했습니다. (코드: {error_code}, 메시지: {error_message})'
        })
    else:
        # GET 요청 시 메인화면으로 리다이렉트하면서 오류 정보 전달
        return redirect(url_for('index', 
            code=error_code,
            message=error_message
        ))

@app.route('/payment/widget')
def payment_widget():
    """결제위젯 페이지"""
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    return render_template('payment_widget.html', 
                         cart_items=cart_items, 
                         total=total,
                         client_key=app.config['TOSS_CLIENT_KEY'])

# 토스페이먼츠 결제 관련 함수들
def get_toss_auth_header():
    """토스페이먼츠 API 인증 헤더 생성"""
    secret_key = app.config['TOSS_SECRET_KEY']
    encoded_secret = base64.b64encode(f"{secret_key}:".encode()).decode()
    return {"Authorization": f"Basic {encoded_secret}"}

def create_payment_key():
    """결제 키 생성"""
    return str(uuid.uuid4()).replace('-', '')

def get_order_items_text(cart_items):
    """주문 상품명 생성"""
    if len(cart_items) == 1:
        return cart_items[0]['product'].name
    else:
        return f"{cart_items[0]['product'].name} 외 {len(cart_items)-1}건"

# 초기 데이터 생성
def create_sample_data():
    """샘플 데이터 생성 (기존 데이터가 없을 때만)"""
    with app.app_context():
        db.create_all()
        
        # 기존 데이터가 있으면 샘플 데이터 생성하지 않음
        if Category.query.first() or Product.query.first():
            print("기존 데이터가 존재합니다. 샘플 데이터를 생성하지 않습니다.")
            return
        
        print("샘플 데이터를 생성합니다...")
        
        # 기본 카테고리 생성
        categories = [
            Category(name='음식', description='신선한 음식과 식재료', icon='fas fa-utensils', color='text-warning'),
            Category(name='음료', description='다양한 음료와 주스', icon='fas fa-coffee', color='text-info'),
            Category(name='간식', description='과자와 스낵류', icon='fas fa-cookie-bite', color='text-success'),
            Category(name='생활용품', description='일상 생활에 필요한 용품', icon='fas fa-home', color='text-primary')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # 샘플 상품 생성
        sample_products = [
            Product(name='삼각김밥', price=1500, category='음식', description='신선한 삼각김밥', stock=20),
            Product(name='라면', price=1200, category='음식', description='맛있는 라면', stock=15),
            Product(name='커피', price=2000, category='음료', description='따뜻한 커피', stock=30),
            Product(name='콜라', price=1500, category='음료', description='시원한 콜라', stock=25),
            Product(name='과자', price=1000, category='간식', description='바삭한 과자', stock=40),
            Product(name='껌', price=500, category='간식', description='상쾌한 껌', stock=50),
            Product(name='휴지', price=3000, category='생활용품', description='부드러운 휴지', stock=10),
            Product(name='치약', price=2000, category='생활용품', description='깨끗한 치약', stock=8)
        ]
        
        for product in sample_products:
            db.session.add(product)
        
        db.session.commit()
        print("샘플 데이터 생성 완료!")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return f'/static/uploads/{unique_filename}'
    return None

def save_audio(file):
    if file and allowed_audio_file(file.filename):
        filename = secure_filename(file.filename)
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['AUDIO_FOLDER'], unique_filename)
        file.save(filepath)
        return f'/static/audio/{unique_filename}'
    return None

@app.route('/admin/product/<int:product_id>', methods=['GET'])
@admin_required
def get_product(product_id):
    """상품 정보 조회"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'category': product.category,
        'stock': product.stock,
        'description': product.description,
        'image_url': product.image_url
    })

@app.route('/admin/product/<int:product_id>', methods=['POST'])
@admin_required
def update_product(product_id):
    """상품 수정"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # 폼 데이터 업데이트
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.category = request.form.get('category')
        product.stock = int(request.form.get('stock'))
        product.description = request.form.get('description', '')
        
        # 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_url = save_image(file)
                if image_url:
                    product.image_url = image_url
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/product/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """상품 삭제"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # 이미지 파일 삭제
        if product.image_url:
            image_path = os.path.join(app.root_path, product.image_url.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_product', methods=['POST'])
@admin_required
def add_product():
    """상품 등록"""
    try:
        # 폼 데이터 가져오기
        name = request.form.get('name')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        stock = int(request.form.get('stock'))
        description = request.form.get('description', '')
        
        # 이미지 업로드 처리
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_url = save_image(file)
        
        # 상품 생성
        product = Product(
            name=name,
            price=price,
            category=category,
            stock=stock,
            description=description,
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('상품이 성공적으로 등록되었습니다!', 'success')
        return redirect(url_for('admin'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'상품 등록에 실패했습니다: {str(e)}', 'error')
        return redirect(url_for('admin'))

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """카테고리 관리 페이지"""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/category/add', methods=['POST'])
@admin_required
def add_category():
    """카테고리 추가"""
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        icon = request.form.get('icon', 'fas fa-box')
        color = request.form.get('color', 'text-secondary')
        
        # 중복 확인
        if Category.query.filter_by(name=name).first():
            flash('이미 존재하는 카테고리명입니다.', 'error')
            return redirect(url_for('admin_categories'))
        
        category = Category(
            name=name,
            description=description,
            icon=icon,
            color=color
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('카테고리가 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('admin_categories'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'카테고리 추가에 실패했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_categories'))

@app.route('/admin/category/<int:category_id>', methods=['GET'])
@admin_required
def get_category(category_id):
    """카테고리 정보 조회"""
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'icon': category.icon,
        'color': category.color
    })

@app.route('/admin/category/<int:category_id>', methods=['POST'])
@admin_required
def update_category(category_id):
    """카테고리 수정"""
    try:
        category = Category.query.get_or_404(category_id)
        
        name = request.form.get('name')
        description = request.form.get('description', '')
        icon = request.form.get('icon', 'fas fa-box')
        color = request.form.get('color', 'text-secondary')
        
        # 중복 확인 (자신 제외)
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != category_id:
            return jsonify({'success': False, 'error': '이미 존재하는 카테고리명입니다.'})
        
        category.name = name
        category.description = description
        category.icon = icon
        category.color = color
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/category/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """카테고리 삭제"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # 해당 카테고리의 상품이 있는지 확인
        if category.products:
            return jsonify({'success': False, 'error': '이 카테고리에 속한 상품이 있어 삭제할 수 없습니다.'})
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/audio/upload', methods=['POST'])
@admin_required
def upload_audio():
    """오디오 파일 업로드"""
    try:
        if 'success_audio' in request.files:
            file = request.files['success_audio']
            audio_url = save_audio(file)
            if audio_url:
                # 기존 설정이 있으면 업데이트, 없으면 새로 생성
                settings = AudioSettings.query.first()
                if not settings:
                    settings = AudioSettings()
                    db.session.add(settings)
                settings.success_audio_url = audio_url
                db.session.commit()
                return jsonify({'success': True, 'audio_url': audio_url})
        
        if 'fail_audio' in request.files:
            file = request.files['fail_audio']
            audio_url = save_audio(file)
            if audio_url:
                settings = AudioSettings.query.first()
                if not settings:
                    settings = AudioSettings()
                    db.session.add(settings)
                settings.fail_audio_url = audio_url
                db.session.commit()
                return jsonify({'success': True, 'audio_url': audio_url})
        
        return jsonify({'success': False, 'error': '파일이 없거나 지원되지 않는 형식입니다.'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/audio/settings')
@admin_required
def get_audio_settings():
    """오디오 설정 조회"""
    settings = AudioSettings.query.first()
    return jsonify({
        'success_audio_url': settings.success_audio_url if settings else None,
        'fail_audio_url': settings.fail_audio_url if settings else None
    })

@app.route('/admin/generate-qr', methods=['POST'])
@admin_required
def generate_qr_code():
    """서버 사이드 QR코드 생성"""
    try:
        data = request.get_json()
        qr_text = data.get('text', '')
        
        if not qr_text:
            return jsonify({'error': 'QR코드 텍스트가 필요합니다.'}), 400
        
        # QR코드 생성
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        # 이미지 생성
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 이미지를 base64로 인코딩
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': f'data:image/png;base64,{img_str}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-event-qr', methods=['GET'])
def generate_event_qr():
    """이벤트 페이지 QR코드 생성"""
    try:
        # 이벤트 페이지 URL 생성
        event_url = request.host_url.rstrip('/') + '/customer'
        
        # QR코드 생성
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=8,
            border=2,
        )
        qr.add_data(event_url)
        qr.make(fit=True)
        
        # 이미지 생성
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 이미지를 base64로 인코딩
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': f'data:image/png;base64,{img_str}',
            'url': event_url
        })
        
    except Exception as e:
        return jsonify({'error': f'이벤트 QR코드 생성 실패: {str(e)}'}), 500

@app.route('/generate-lottery-qr', methods=['POST'])
def generate_lottery_qr():
    """뽑기 결과 QR코드 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '데이터가 없습니다.'}), 400
        
        # 쿠폰 데이터 생성
        discount = data.get('discount', 1000)
        coupon_data = {
            'type': 'coupon',
            'code': data.get('code', f'{discount}원쿠폰'),
            'discount': discount,
            'discountType': 'fixed',
            'description': f'{discount}원 쿠폰',
            'createdAt': datetime.now().isoformat()
        }
        
        # QR코드 생성
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(coupon_data, ensure_ascii=False))
        qr.make(fit=True)
        
        # 이미지 생성
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 이미지를 base64로 인코딩
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': f'data:image/png;base64,{img_str}',
            'data': coupon_data
        })
        
    except Exception as e:
        return jsonify({'error': f'뽑기 QR코드 생성 실패: {str(e)}'}), 500

# Content Security Policy 헤더 설정
@app.after_request
def add_security_headers(response):
    # CSP 헤더 설정 (토스페이먼츠 로그 서버 포함)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: "
        "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
        "https://js.tosspayments.com https://kit.fontawesome.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
        "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: blob: https:; "
        "connect-src 'self' https://api.tosspayments.com https://log.tosspayments.com; "
        "frame-src 'self' https://js.tosspayments.com;"
    )
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)