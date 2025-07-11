# ap/app_server.py
from flask import Flask, request, jsonify
import os
import psycopg2 # PostgreSQL 드라이버
from psycopg2 import extras # 딕셔너리 형태로 결과 가져오기 위함

app = Flask(__name__)

# 환경 변수에서 DB 연결 정보 가져오기
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'app_db')
DB_USER = os.getenv('DB_USER', 'app_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password') # 프로덕션에서는 Secret으로 관리

def get_db_connection():
    """PostgreSQL 데이터베이스 연결을 반환합니다."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"데이터베이스 연결 오류: {e}")
        raise # 연결 실패 시 예외 발생

def init_db():
    """데이터베이스 테이블을 초기화합니다."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        print("PostgreSQL 'items' 테이블 생성 또는 확인 완료.")

        # 테스트 데이터 추가 (테이블이 비어있을 경우에만)
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        if count == 0:
            print("테스트 데이터 추가 중...")
            cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s)", ("PostgreSQL Item 1", "This is the first item from PostgreSQL."))
            cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s)", ("PostgreSQL Item 2", "This is the second item from PostgreSQL."))
            conn.commit()
            print("테스트 데이터 추가 완료.")

    except Exception as e:
        print(f"데이터베이스 초기화 오류: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/api/items', methods=['GET'])
def get_all_items():
    """모든 아이템을 조회하여 반환합니다."""
    conn = None
    try:
        conn = get_db_connection()
        # DictCursor를 사용하여 딕셔너리 형태로 결과 가져오기
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        # DictRow 객체를 표준 딕셔너리로 변환하여 JSON 직렬화 가능하게 함
        return jsonify([dict(item) for item in items]), 200
    except Exception as e:
        print(f"아이템 조회 오류: {e}")
        return jsonify({"error": "아이템을 가져오는 중 오류 발생"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/items', methods=['POST'])
def add_new_item():
    """새로운 아이템을 추가합니다."""
    if not request.is_json:
        return jsonify({"error": "요청은 JSON 형식이어야 합니다."}), 400

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"error": "이름은 필수입니다."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id", (name, description))
        item_id = cursor.fetchone()[0] # 새로 삽입된 ID 가져오기
        conn.commit()
        return jsonify({"message": "아이템이 성공적으로 추가되었습니다.", "id": item_id}), 201
    except Exception as e:
        print(f"아이템 추가 오류: {e}")
        return jsonify({"error": "아이템 추가 중 오류 발생"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """지정된 ID의 아이템을 삭제합니다."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
        deleted_id = cursor.fetchone()
        conn.commit()

        if deleted_id:
            return jsonify({"message": f"아이템 (ID: {item_id})이 성공적으로 삭제되었습니다."}), 200
        else:
            return jsonify({"error": f"ID: {item_id}인 아이템을 찾을 수 없습니다."}), 404
    except Exception as e:
        print(f"아이템 삭제 오류 (ID: {item_id}): {e}")
        return jsonify({"error": "아이템 삭제 중 오류 발생"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # AP 서버 시작 전에 DB 초기화 시도
    # (주의: DB 서버가 아직 준비되지 않았을 수 있으므로 K8s Health Check가 중요)
    init_db()
    print("AP 계층 서버 시작 중...")
    app.run(host='0.0.0.0', port=5001, debug=True)
