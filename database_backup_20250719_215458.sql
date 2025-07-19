-- 편의점 POS 시스템 데이터베이스 백업
-- 생성일시: 2025-07-19 21:54:58
-- 파일: database_backup_20250719_215458.sql

-- 테이블: category
CREATE TABLE category (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	color VARCHAR(20), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

-- category 테이블 데이터 (5개 행)
INSERT INTO category (id, name, description, icon, color, created_at) VALUES (1, '음식', '신선한 음식과 식재료', 'fas fa-utensils', 'text-warning', '2025-07-19 12:22:13.477720');
INSERT INTO category (id, name, description, icon, color, created_at) VALUES (2, '음료', '다양한 음료와 주스', 'fas fa-coffee', 'text-info', '2025-07-19 12:22:13.479798');
INSERT INTO category (id, name, description, icon, color, created_at) VALUES (3, '간식', '과자와 스낵류', 'fas fa-cookie-bite', 'text-success', '2025-07-19 12:22:13.480322');
INSERT INTO category (id, name, description, icon, color, created_at) VALUES (4, '생활용품', '일상 생활에 필요한 용품', 'fas fa-home', 'text-primary', '2025-07-19 12:22:13.480733');
INSERT INTO category (id, name, description, icon, color, created_at) VALUES (5, '아이스크림', '아이스크림', 'fas fa-utensils', 'text-info', '2025-07-19 12:22:49.521739');

-- 테이블: order
CREATE TABLE "order" (
	id INTEGER NOT NULL, 
	customer_name VARCHAR(100) NOT NULL, 
	customer_phone VARCHAR(20) NOT NULL, 
	total_amount FLOAT NOT NULL, 
	order_date DATETIME, 
	status VARCHAR(20), 
	PRIMARY KEY (id)
);

