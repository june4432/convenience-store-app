import sqlite3
import os
from app import app, db # User, Order, PointHistory 모델은 직접 임포트하지 않습니다.

# Flask 애플리케이션 컨텍스트를 활성화합니다.
# SQLAlchemy 작업은 애플리케이션 컨텍스트 내에서 실행되어야 합니다.
with app.app_context():
    print("새로운 테이블 (user, point_history)을 생성하기 위해 db.create_all()을 실행합니다...")
    # db.create_all()은 app.py에 정의된 모든 모델에 대한 테이블을 생성합니다.
    # 이미 존재하는 테이블은 건드리지 않습니다.
    db.create_all()
    print("db.create_all() 완료.")

    # SQLite 데이터베이스 파일 경로
    db_path = os.path.join(app.root_path, 'instance', 'convenience_store.db')

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 'order' 테이블에 'user_id' 컬럼이 존재하는지 확인합니다.
        cursor.execute("PRAGMA table_info(\"order\")")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns] # 컬럼 이름만 추출

        if 'user_id' not in column_names:
            print("'order' 테이블에 'user_id' 컬럼을 추가합니다...")
            cursor.execute("ALTER TABLE \"order\" ADD COLUMN user_id INTEGER")
            conn.commit()
            print("'user_id' 컬럼이 'order' 테이블에 성공적으로 추가되었습니다.")
        else:
            print("'user_id' 컬럼이 'order' 테이블에 이미 존재합니다. 건너뜁니다.")

    except sqlite3.Error as e:
        print(f"데이터베이스 오류 발생: {e}")
        if conn:
            conn.rollback() # 오류 발생 시 변경사항 롤백
    finally:
        if conn:
            conn.close() # 연결 종료

print("데이터베이스 마이그레이션 스크립트가 완료되었습니다.")