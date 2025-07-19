#!/usr/bin/env python3
"""
데이터베이스 내보내기 스크립트
현재 데이터베이스의 모든 데이터를 SQL 파일로 내보냅니다.
"""

import sqlite3
import os
from datetime import datetime

def export_database():
    """데이터베이스를 SQL 파일로 내보내기"""
    db_path = 'instance/convenience_store.db'
    
    if not os.path.exists(db_path):
        print("데이터베이스 파일을 찾을 수 없습니다.")
        return
    
    # SQL 파일명 생성 (날짜 포함)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sql_file = f'database_backup_{timestamp}.sql'
    
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL 파일 생성
        with open(sql_file, 'w', encoding='utf-8') as f:
            # 헤더 작성
            f.write(f"-- 편의점 POS 시스템 데이터베이스 백업\n")
            f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 파일: {sql_file}\n\n")
            
            # 테이블 스키마 내보내기
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                f.write(f"-- 테이블: {table_name}\n")
                
                # 테이블 생성 스크립트
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                create_sql = cursor.fetchone()[0]
                f.write(f"{create_sql};\n\n")
                
                # 데이터 내보내기
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                if rows:
                    # 컬럼명 가져오기
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    f.write(f"-- {table_name} 테이블 데이터 ({len(rows)}개 행)\n")
                    
                    for row in rows:
                        # NULL 값과 문자열 처리
                        formatted_values = []
                        for value in row:
                            if value is None:
                                formatted_values.append('NULL')
                            elif isinstance(value, str):
                                # SQL 인젝션 방지를 위한 이스케이프
                                escaped_value = value.replace("'", "''")
                                formatted_values.append(f"'{escaped_value}'")
                            else:
                                formatted_values.append(str(value))
                        
                        f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(formatted_values)});\n")
                    
                    f.write("\n")
        
        conn.close()
        print(f"✅ 데이터베이스가 성공적으로 내보내졌습니다: {sql_file}")
        print(f"📁 파일 크기: {os.path.getsize(sql_file)} bytes")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def import_database(sql_file):
    """SQL 파일에서 데이터베이스 복원"""
    if not os.path.exists(sql_file):
        print(f"SQL 파일을 찾을 수 없습니다: {sql_file}")
        return
    
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect('instance/convenience_store.db')
        cursor = conn.cursor()
        
        # SQL 파일 읽기 및 실행
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # SQL 문장들을 분리하여 실행
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        print(f"✅ 데이터베이스가 성공적으로 복원되었습니다: {sql_file}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'import':
        if len(sys.argv) > 2:
            import_database(sys.argv[2])
        else:
            print("사용법: python export_db.py import <sql_file>")
    else:
        export_database()
        print("\n📋 사용법:")
        print("  내보내기: python export_db.py")
        print("  복원하기: python export_db.py import <sql_file>") 